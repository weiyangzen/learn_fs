# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_common.c

## Purpose
`ixgbe_common.c` is the shared hardware-service layer for Intel ixgbe 10 GbE adapters. It provides generic implementations for MAC start/stop, reset-time initialization, flow control advertisement and enablement, EEPROM/NVM access, receive address and multicast/VLAN filters, VMDq mapping, link-state reads, PCIe quiescing, manageability host-interface commands, firmware/option-ROM version reads, thermal sensor access, RX enable/disable, and multispeed fiber link setup. Chip-specific files bind these routines through `struct ixgbe_mac_operations`, `struct ixgbe_eeprom_operations`, and `struct ixgbe_phy_operations`.

## Important APIs, Types, And Functions
- `ixgbe_setup_fc_generic()`, `ixgbe_fc_enable_generic()`, `ixgbe_fc_autoneg()`, and `ixgbe_negotiate_fc()` implement 802.3x pause advertisement, autonegotiation resolution, and register programming for fiber, backplane, and copper media.
- `ixgbe_start_hw_generic()`, `ixgbe_start_hw_gen2()`, `ixgbe_init_hw_generic()`, `ixgbe_stop_adapter_generic()`, and `ixgbe_clear_hw_cntrs_generic()` implement common device bring-up, counter clearing, and stop/quiesce behavior.
- EEPROM/NVM paths include `ixgbe_init_eeprom_params_generic()`, EERD/EEWR helpers, bit-banged SPI read/write helpers, page-size detection, checksum calculation, checksum validation, and checksum update.
- Receive filtering is handled by `ixgbe_set_rar_generic()`, `ixgbe_clear_rar_generic()`, `ixgbe_init_rx_addrs_generic()`, multicast table helpers, VMDq helpers, UTA initialization, VLAN/VLVF/VLVFB programming, and full VFTA clearing.
- Link and bus helpers include PCIe bus-width/speed conversion, LAN-id detection, MSI-X count detection, `ixgbe_check_mac_link_generic()`, crosstalk gating, and multispeed fiber fallback between 10G and 1G.
- Management and firmware helpers include `ixgbe_hic_unlocked()`, `ixgbe_host_interface_command()`, `ixgbe_set_fw_drv_ver_generic()`, `ixgbe_mng_present()`, and NVM version readers for OROM, OEM product version, and ETrack ID.
- Hardware state protection uses SW/FW semaphore APIs `ixgbe_acquire_swfw_sync()` and `ixgbe_release_swfw_sync()`, plus protected AUTOC read/write shims.

## Control Flow
Initialization normally flows from the chip-specific reset routine into `ixgbe_init_hw_generic()`, then `start_hw`, which identifies media/PHY, clears VFTA and counters, sets no-snoop disable, programs flow-control advertisement, and caches crosstalk-fix requirements. Stop flow sets `adapter_stopped`, disables RX, masks interrupts, flushes TX/RX descriptor control, and disables PCIe primary access to avoid bus hangs before reset.

EEPROM control has two paths. EERD/EEWR operations write command registers and poll done bits. Bit-banged SPI operations acquire the SW/FW EEPROM semaphore, request/grant access via EEC, clock opcodes and data through DI/DO/SK/CS bits, wait for ready status, then release EEC request and the semaphore. Large EEPROM writes may detect page size by writing a scratch marching pattern and observing wraparound.

Filtering control updates hardware in safety-oriented order. RAR writes program VMDq before enabling the address and flush low words before high/valid bits. RAR clears invalidate high/valid bits before low words. VLAN operations update VLVF/VLVFB before VFTA on enable, and clear VFTA before disabling a last VLVF pool on removal to reduce stray-packet leakage to the PF default pool.

Flow control setup first validates requested mode, adjusts advertisement registers by media type, and for backplane uses protected AUTOC access. Later `fc_enable` resolves negotiated or requested mode and programs MFLCN/FCCFG, watermarks, pause timers, and refresh thresholds. Link checks read `LINKS`, optionally wait, derive speed encoding, and apply SFP crosstalk checks for affected devices.

## State And Persistence
The file persists no filesystem state. It mutates device MMIO registers, PCI config space, EEPROM/NVM words, PHY/I2C registers, and fields in `struct ixgbe_hw` such as `adapter_stopped`, `need_crosstalk_fix`, EEPROM geometry, bus identity, cached MAC address, multicast shadow table, flow-control state, thermal sensor data, and flags such as `IXGBE_FLAGS_DOUBLE_RESET_REQUIRED`. EEPROM writes and checksum updates are durable device state and require careful ordering with checksum maintenance.

## Dependencies And Integration Points
The implementation depends on Linux PCI, delay, scheduler, and netdevice APIs, ixgbe register macros from `ixgbe_type.h`, common declarations from `ixgbe_common.h`, PHY helpers from `ixgbe_phy.h`, and the adapter backpointer used by debug/error macros. It is called from chip-specific MAC operation tables, probe/reset paths, ethtool/debug operations, SR-IOV/VMDq code, link-service task handling, DCB/PFC paths, and firmware manageability setup.

## Risks
- EEPROM bit-bang and checksum paths can permanently corrupt adapter NVM if offsets, page-size detection, or checksum update ordering are wrong.
- SW/FW semaphore errors can deadlock or race firmware if release paths are skipped; the code has many timeout and release fallbacks that need preservation.
- Flow-control and PFC-adjacent watermarks can cause XOFF floods or TX hangs if low/high water values are invalid.
- Stop/reset code touches PCIe primary-disable and double-reset behavior; regressions can hang the bus on affected 82599/X540 devices.
- VLAN and VMDq ordering protects against packet leakage between PF/VF pools; changes should be tested with SR-IOV and VLAN filter churn.
- `ixgbe_check_mac_link_generic()` includes device-specific crosstalk behavior; speed decoding errors affect link reporting and link setup fallback.

## Test Signals
Useful signals include probe/reset success across 82598, 82599, X540, X550, X550EM, and E610 variants; `ethtool -S` counter sanity after clear-on-read; EEPROM read/checksum validation and guarded write tests on sacrificial hardware; link up/down and speed changes for copper, backplane, SFP, and QSFP; pause/PFC behavior under congestion; multicast/VLAN filter programming with packet capture; SR-IOV VMDq isolation; firmware host-interface command success; thermal sensor sysfs/ethtool readings; and reset stress tests that watch for PCIe transaction timeout or double-reset paths.
