# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/falcon.c

## Purpose

`falcon.c` is the Falcon/SFC4000 NIC implementation layer for the legacy Solarflare `sfc-falcon` Ethernet driver. It binds the generic `ef4_nic_type` operation table used by the rest of the driver to Falcon A1 and B0 hardware behavior: probing the ASIC, reading NVRAM configuration, setting up SPI and I2C side buses, selecting board and PHY support, managing resets, configuring the XMAC/XAUI data path, exposing stats, handling MDIO access, and publishing revision-specific capabilities.

The file is not a standalone network path implementation. TX/RX/event queues and filters are mostly delegated to `farch.c`; board-specific power and sensor behavior is delegated to `falcon_boards.c`; PHY-specific behavior is delegated to `sfx7101`, `qt202x`, and `txc` PHY operation tables. `falcon.c` is the orchestration point that sequences those pieces around hardware reset, port reconfiguration, monitoring, and `struct ef4_nic_type` callbacks.

## Important APIs, Types, And Functions

The exported integration objects are `falcon_a1_nic_type` and `falcon_b0_nic_type`. They fill the driver core's `struct ef4_nic_type` with Falcon-specific callbacks for probe/remove/init, reset mapping, IRQ handling, queue operations, event processing, filter management, stats, Wake-on-LAN, and optional MTD operations. The A1 table uses `falcon_legacy_interrupt_a1`, limits interrupt mode to MSI, disables RSS, sets A1 register-table bases, and has no RX scatter. The B0 table uses the shared farch legacy interrupt handler, supports MSI-X, RSS, RX hash, ntuple filtering, scatter, and B0 register-table bases.

NVRAM structures (`struct falcon_nvconfig`, `falcon_nvconfig_board_v2`, `falcon_nvconfig_board_v3`) model the first 0x400 bytes of flash/EEPROM board configuration. `falcon_read_nvram()` chooses flash or EEPROM, reads the NVRAM region under `nic_data->spi_lock`, validates magic/version/checksum, and optionally returns a copy. `falcon_probe_nvconfig()` extracts PHY type/address, SPI device descriptions, permanent MAC address, and board revision, then calls `falcon_probe_board()`.

SPI helpers (`falcon_spi_cmd()`, `falcon_spi_read()`, and, under `CONFIG_SFC_FALCON_MTD`, write/erase/sync helpers) operate via Falcon EE/SPI registers. `falcon_spi_device_init()` decodes device geometry from NVRAM bitfields or fallback defaults. MTD wrappers (`falcon_mtd_probe()`, `falcon_mtd_read()`, `falcon_mtd_write()`, `falcon_mtd_erase()`, `falcon_mtd_sync()`) expose the boot ROM and boot config partitions when enabled.

Port and MAC functions include `falcon_probe_port()`, `falcon_reconfigure_port()`, `falcon_reconfigure_xmac()`, `falcon_reconfigure_xmac_core()`, `falcon_reconfigure_xgxs_core()`, `falcon_reset_macs()`, `falcon_reset_xaui()`, `falcon_deconfigure_mac_wrapper()`, and `falcon_reconfigure_mac_wrapper()`. They coordinate PHY polling/reconfiguration, Falcon XMAC setup, XAUI/XGXS loopback state, multicast hash programming, flow control, frame size, MAC address, FIFO drain, and stats suppression around disruptive operations.

Reset and init functions include `falcon_probe_nic()`, `falcon_init_nic()`, `falcon_remove_nic()`, `falcon_reset_hw()`, `__falcon_reset_hw()`, `falcon_reset_sram()`, `falcon_map_reset_reason()`, and `falcon_map_reset_flags()`. These functions allocate `struct falcon_nic_data`, reject unsupported revisions, find A1 secondary PCI function state, reset hardware, allocate the interrupt-status DMA buffer, add the bit-banged I2C bus, initialize board hardware, initialize SRAM/cache/RX/TX global configuration, and release all resources in reverse.

Stats functions (`falcon_stats_request()`, `falcon_stats_complete()`, `falcon_stats_timer_func()`, `falcon_start_nic_stats()`, `falcon_stop_nic_stats()`, `falcon_update_nic_stats()`) drive XMAC statistics DMA into `efx->stats_buffer`, maintain `nic_data->stats`, derive software/core stats, and use `stats_disable_count` to prevent stats DMA while MAC/XAUI state is being reset.

MDIO functions (`falcon_mdio_read()`, `falcon_mdio_write()`, `falcon_gmii_wait()`) expose PHY register access through the Falcon GMII management registers and are installed into `efx->mdio` by `falcon_probe_port()`.

## Control Flow

Probe starts in `falcon_probe_nic()`. It allocates Falcon private state, rejects FPGA/A0/unsupported strap combinations, finds the second PCI function for A1 dual-function reset handling, performs a full reset, allocates the interrupt-status DMA buffer, probes SPI boot devices, reads and validates NVRAM, derives channel/timer limits, constructs the GPIO-backed I2C adapter, and calls the selected board type's `init()` method. Later `falcon_probe_port()` selects a PHY ops table from `efx->phy_type`, wires MDIO access, probes the PHY, initializes flow-control defaults, and allocates the MAC stats buffer.

Device init through `falcon_init_nic()` switches to on-chip SRAM, resets SRAM contents, applies hardware workarounds, configures RX FIFO thresholds/hash insertion, pushes RSS state on B0, sets flush event destination, and delegates common descriptor-cache/interrupt setup to `ef4_farch_init_common()`.

Port reconfiguration first polls loopback or PHY state, stops stats, isolates and drains MAC/RX/TX paths, resets MACs, reconfigures the PHY, reprograms XGXS/XMAC and wrapper registers, restarts stats, and informs the net stack via `ef4_link_status_changed()`. Monitor flow (`falcon_monitor()`) additionally runs board sensor checks and may force PHY low-power mode on board fault.

Reset requests are normalized by `falcon_map_reset_reason()` and ethtool flags by `falcon_map_reset_flags()`. Hardware reset uses `__falcon_reset_hw()`, with `RESET_TYPE_WORLD` preserving/restoring PCI config for both functions and other resets selectively excluding PHY/PCIe/EEPROM blocks. `falcon_reset_hw()` serializes reset against SPI operations with `spi_lock`.

## State And Persistence Behavior

Persistent hardware identity comes from NVRAM: PHY type/address, board revision, MAC address, and SPI flash/EEPROM geometry. The code validates checksum before trusting it and fails probe on invalid NVRAM. Optional MTD support exposes persistent boot flash/config partitions and verifies writes/erases by reading data back.

Runtime state lives mainly in `struct falcon_nic_data` under `efx->nic_data`: board info, SPI flash/EEPROM descriptors, locks, stats timer/state, XAUI poll flag, and A1 secondary PCI device pointer. `efx` carries link state, PHY mode, multicast hash, RSS tables, stats buffer, IRQ status buffer, and filter state. Stats state is long-lived across polls but is not persistent; it is rebuilt from hardware DMA counters and software counters.

Concurrency is explicit: SPI is serialized by `spi_lock`; MDIO by `mdio_lock`; MAC operations expect `mac_lock`; stats use `stats_lock`, barriers, and a timer; reset pending is read with `READ_ONCE()`. Stats are deliberately disabled around MAC and XAUI reset windows to avoid DMA failures or stale done flags.

## Dependencies And Integration Points

The file depends on Linux PCI, I2C, MTD, netdevice, timer, MDIO/MII, and kernel synchronization APIs. Driver-local dependencies include `net_driver.h`, `efx.h`, `nic.h`, `farch_regs.h`, `io.h`, `phy.h`, `workarounds.h`, `selftest.h`, and `mdio_10g.h`.

It integrates directly with `farch.c` through queue/event/filter/IRQ/common-init callbacks, with `falcon_boards.c` through `falcon_probe_board()` and board operation tables, with PHY drivers through `falcon_sfx7101_phy_ops`, `falcon_qt202x_phy_ops`, and `falcon_txc_phy_ops`, with ethtool through stats, reset, WOL, and self-test callbacks, and with optional MTD through `CONFIG_SFC_FALCON_MTD`.

## Risks And Edge Cases

This code is hardware-sequencing heavy. Ordering mistakes around reset, MAC drain, XAUI reset, stats DMA, or interrupt status buffers can produce data-path hangs or false fatal errors. Several paths depend on revision-specific workarounds (`EF4_WORKAROUND_*`) and A1/B0 register differences; applying B0 behavior to A1 or vice versa is a major risk.

NVRAM validation is a hard probe gate; malformed or absent flash/EEPROM leaves the NIC unusable even if hardware might be manually configurable. SPI MTD writes are potentially destructive, so lock coverage, write-enable sequencing, timeout handling, and read-back verification are important. `falcon_spi_read()` and write/erase loops allow interruption and rescheduling, which prevents CPU stalls but requires callers to handle partial lengths.

Stats DMA uses a done flag inside the DMA buffer plus memory barriers. Missing barriers or enabling stats during MAC/XAUI reset can cause stale or timed-out stat reads. `stats_disable_count` underflow would also be dangerous; callers use warnings but correct pairing remains essential.

Board monitor failures intentionally force PHY low power or off modes. That protects hardware but can surprise users if sensor reads fail transiently. Flow-control recovery differs by revision: A1 schedules an invisible reset while B0 drains/reconfigures the EM/MAC path.

## Test Signals

Hardware self-test entry points include `falcon_test_nvram()` and `falcon_b0_test_chip()`, which uses `ef4_farch_test_registers()` over a B0 register mask after forcing a loopback-capable port state. Runtime test signals include SPI timeout and checksum errors, GMII timeout/error logs, XMAC/XAUI reset timeout logs, NVRAM magic/version/checksum failures, stats DMA timeout logs, board sensor shutdown logs, and reset scheduling from global RX recovery events.

Regression coverage should exercise probe/unwind on invalid NVRAM and failed I2C/SPI allocations, reset mapping for invisible/all/world resets, stats start/stop pairing, link reconfiguration with loopback and no-loopback paths, B0 RSS push, MTD read/write/erase verification under `CONFIG_SFC_FALCON_MTD`, and A1-specific legacy interrupt acknowledgement behavior.
