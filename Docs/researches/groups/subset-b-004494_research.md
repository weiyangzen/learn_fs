# subset-b-004494 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_common.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_common.h

## Purpose
`ixgbe_common.h` exposes the shared ixgbe hardware-service API and low-level register access wrappers used by the driver. It declares generic MAC, EEPROM, flow-control, filtering, bus, firmware, thermal, RX, and link helpers implemented mostly in `ixgbe_common.c`, and it centralizes macros for safe MMIO reads/writes and driver logging.

## Important APIs, Types, And Functions
- Public declarations cover generic init/start/stop, counter clearing, PBA string and MAC address reads, bus conversion/info, EEPROM read/write/checksum operations, RAR/MTA/VFTA/VMDq filtering, flow control, SW/FW synchronization, SAN MAC and WWN reads, LED control, anti-spoofing, firmware host-interface commands, thermal sensors, RX enable/disable, and multispeed fiber link setup.
- `ixgbe_mvals_8259X` is declared as a shared register-value table for MAC-specific values.
- Thermal sensor constants define EMC/I2C register addresses used by generic thermal helpers.
- Removed-device sentinels define failed read values for MMIO and PCI config access.
- `ixgbe_removed()`, `ixgbe_write_reg()`, `ixgbe_write_reg64()`, `IXGBE_READ_REG`, `IXGBE_WRITE_REG`, array access macros, and `IXGBE_WRITE_FLUSH` define the main hardware access surface.
- Logging macros map hardware and adapter contexts to `netdev_*`, `dev_*`, and `netif_*` logging APIs.

## Control Flow
Including this header gives chip-specific and adapter-level files access to the generic operation set. Most calls are indirect through operation tables in `struct ixgbe_hw`, but direct callers also use declarations for DCB, SR-IOV, firmware, ethtool, and reset support. The inline write wrappers first read `hw->hw_addr` with `READ_ONCE`, check for a removed adapter, and skip writes if the MMIO base is gone.

## State And Persistence
The header itself stores no runtime state, but its APIs mutate hardware MMIO, EEPROM/NVM, PHY/I2C state, and fields inside `struct ixgbe_hw` and `struct ixgbe_adapter`. The inline MMIO helpers are intentionally defensive against surprise device removal and therefore influence how all callers behave during PCI error removal or hot-unplug handling.

## Dependencies And Integration Points
This header depends on `ixgbe_type.h` for hardware structures, enums, and register constants, and on `ixgbe.h` for adapter-facing types and logging context. It is an integration hub for chip-specific source files, netdev operations, ethtool/debugfs paths, DCB code, firmware-management code, and low-level reset/link paths.

## Risks
- Since register macros are globally used, a mistake in removed-device handling or write ordering can affect nearly every hardware path.
- Function prototype drift between this header and implementations can break operation table assignments at compile time or silently push callers toward wrong generic helpers.
- Logging macros assume `hw->back` points to a valid `struct ixgbe_adapter`; early probe, teardown, or error paths must not call them before that invariant is true.
- `writeq` fallback ordering is low-word then high-word; callers depending on atomic 64-bit writes must be aware of hardware expectations.

## Test Signals
Compile coverage with all ixgbe chip variants enabled is the primary signal. Runtime signals include safe behavior on device removal, no MMIO access faults after hot-unplug/AER, successful reset and link setup using operation-table generic helpers, and expected logs from `hw_dbg`, `hw_err`, and adapter logging macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb.c

## Purpose
`ixgbe_dcb.c` is the generic Data Center Bridging calculation and dispatch layer. It converts ixgbe DCB configuration structures and IEEE ETS inputs into traffic-class credit arrays, PFC masks, bandwidth group IDs, priority types, and priority-to-traffic-class maps, then delegates hardware programming to 82598 or 82599-family implementations.

## Important APIs, Types, And Functions
- `ixgbe_dcb_calculate_tc_credits()` computes CEE-style per-traffic-class refill and max credits from bandwidth group percentages, traffic-class bandwidth, max frame size, and MAC type.
- `ixgbe_ieee_credits()` computes simplified IEEE 802.1Qaz ETS credits directly from per-TC bandwidth percentages.
- Unpack helpers extract fields from `struct ixgbe_dcb_config`: PFC bitmask, refill credits, max credits, bandwidth group IDs, priority types, and UP-to-TC maps.
- `ixgbe_dcb_get_tc_from_up()` and `ixgbe_dcb_unpack_map()` translate user priorities into traffic classes using configured bitmaps.
- `ixgbe_dcb_hw_config()`, `ixgbe_dcb_hw_pfc_config()`, `ixgbe_dcb_hw_ets()`, and `ixgbe_dcb_hw_ets_config()` select the correct 82598 or 82599-family hardware backend.
- `ixgbe_dcb_read_rtrup2tc()` reads hardware UP-to-TC mapping for 82599-family devices.

## Control Flow
CEE configuration starts from `ixgbe_dcb_hw_config()`: unpack the abstract `ixgbe_dcb_config`, then branch on `hw->mac.type`. The 82598 branch calls the 82598 backend without a priority map; the 82599/X540/X550 branches pass `prio_tc` for UP-to-TC register programming. IEEE ETS configuration flows through `ixgbe_dcb_hw_ets()`, which validates TSA values, maps strict and ETS TSAs onto ixgbe priority types, computes refill/max credits, and calls `ixgbe_dcb_hw_ets_config()`.

Credit calculation first determines minimum credit needed for half the max frame in 64-byte quanta, finds the smallest nonzero bandwidth share, derives a multiplier that keeps refill credits above the minimum frame requirement, then writes refill/max credits back into each TC path. For TX on 82598, descriptor max credits are raised to the TSO minimum if needed.

## State And Persistence
This file does not persist state outside memory and hardware. It mutates `struct ixgbe_dcb_config` by filling `link_percent`, `data_credits_refill`, `data_credits_max`, and `desc_credits_max`. Hardware state changes happen indirectly through backend calls that program DCB arbiter and PFC registers. Input configuration is owned by adapter-level DCB netlink setup.

## Dependencies And Integration Points
The file depends on `ixgbe.h`, `ixgbe_type.h`, `ixgbe_dcb.h`, and chip-specific DCB headers. Its callers include `ixgbe_dcb_nl.c`, adapter traffic-class setup paths, and any reset/reconfigure flow that reapplies DCB. It bridges the Linux DCBNL/IEEE concepts into hardware-specific CEE-like credit programming.

## Risks
- `min_percent` must not remain at an invalid value for all-zero bandwidth inputs; callers are expected to validate DCB rules before credit calculation.
- Integer division can collapse small bandwidth shares to zero, so the code has explicit minimum correction. Changes here can skew actual wire bandwidth.
- 82598 TSO credit handling is special; missing that adjustment can cause TX stalls with large TSO frames.
- Hardware dispatch excludes E610 and unsupported MAC types in this source; callers must account for no-op or `-EINVAL` returns.
- Priority map consistency matters for PFC: mismatched ETS and PFC maps can pause the wrong traffic class.

## Test Signals
Tests should cover CEE and IEEE ETS configurations with 1, 4, and 8 TCs; strict and ETS TSA combinations; very small nonzero bandwidth percentages; jumbo MTU and FCoE-sized frames; 82598 TSO traffic under DCB; PFC enable/disable per priority; hardware readback of UP-to-TC maps; and traffic-generator validation that bandwidth ratios and pause behavior match configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb.h

## Purpose
`ixgbe_dcb.h` defines the shared Data Center Bridging configuration model and public DCB helper APIs for ixgbe. It describes DCB support capabilities, traffic-class bandwidth allocation, PFC mode, the aggregate `ixgbe_dcb_config`, error constants, credit limits, and hardware initialization entry points.

## Important APIs, Types, And Functions
- Constants define maximum packet buffers, user priorities, bandwidth groups, TX/RX direction indexes, DCB errors, and capability flags.
- `enum strict_prio_type` distinguishes no strict priority, group strict priority, and link strict priority.
- `struct dcb_support`, `struct tc_bw_alloc`, `struct tc_configuration`, `struct dcb_num_tcs`, and `struct ixgbe_dcb_config` are the main configuration and capability structures.
- `enum dcb_pfc_type` tracks disabled, full, TX-only, and RX-only PFC settings at the traffic-class level.
- Public APIs declare unpack helpers, TC credit calculation, CEE and IEEE hardware configuration, PFC configuration, ETS configuration, and UP-to-TC hardware readback.
- Credit constants define 64-byte quantum, refill/max limits, TSO sizing, and minimum TSO credit requirements.

## Control Flow
Adapter-level DCB setup populates `ixgbe_dcb_config`, then generic DCB code uses the declarations here to calculate credits and unpack arrays for hardware programming. Netlink handlers update either temporary or active instances of these structures before `ixgbe_dcb.c` and chip-specific files apply them to registers.

## State And Persistence
The header defines in-memory state owned by `struct ixgbe_adapter`, especially `adapter->dcb_cfg` and `adapter->temp_dcb_cfg`. This state is runtime configuration and is reapplied to hardware during DCB changes, traffic-class setup, and resets. It is not persisted to disk by the driver.

## Dependencies And Integration Points
The header depends on Linux `dcbnl.h` and ixgbe hardware types. It is included by generic DCB code, chip-specific DCB register programming files, and DCB netlink handlers. Its structures form the contract between user-requested DCBNL settings and MMIO programming.

## Risks
- Array dimensions are fixed at eight TCs/priorities; callers must validate indexes from netlink or hardware before writing arrays.
- Error constants are negative driver-local values, not errno-style for every case; call sites must translate or preserve them intentionally.
- Credit constants encode hardware limits. Changing them can silently create invalid register fields or insufficient credits for jumbo/TSO traffic.
- `dcb_cfg_version` is marked unused, so external consumers should not assume versioned persistence semantics.

## Test Signals
Compile-time coverage of all DCB users, DCBNL set/get round trips, credit calculation tests at boundary bandwidth values, PFC mode transitions, traffic-class count changes, and hardware register readback after CEE/IEEE configuration are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb_82598.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb_82598.c

## Purpose
`ixgbe_dcb_82598.c` programs DCB hardware for the 82598 MAC. It configures receive arbitration, transmit descriptor arbitration, transmit data arbitration, priority flow control, and traffic-class statistics mappings using the register layout and limitations of 82598.

## Important APIs, Types, And Functions
- `ixgbe_dcb_config_rx_arbiter_82598()` enables UP-to-queue mapping, receive recycle/DFP arbitration, writes `RT2CR` credit registers, enables multi-packet-buffer and multi-core receive behavior, and clears descriptor bypass.
- `ixgbe_dcb_config_tx_desc_arbiter_82598()` enables descriptor arbitration, TSO expand behavior, max TSO sizing, and per-TC `TDTQ2TCCR` credits and priority flags.
- `ixgbe_dcb_config_tx_data_arbiter_82598()` enables data-plane DFP/recycle arbitration, writes `TDPT2TCCR` credits/priority flags, and enables TX packet-buffer division.
- `ixgbe_dcb_config_pfc_82598()` switches from 802.3x flow control to priority flow control, enables RX PFC when requested, writes per-TC low/high thresholds, pause timers, and refresh threshold.
- `ixgbe_dcb_config_tc_stats_82598()` maps RX/TX queues to TC statistic counters.
- `ixgbe_dcb_hw_config_82598()` is the aggregate backend called from generic DCB dispatch.

## Control Flow
The aggregate configuration function runs in fixed order: RX arbiter, TX descriptor arbiter, TX data arbiter, PFC, then TC statistics. Each arbiter function reads a control register, clears arbitration-disable bits or sets arbitration mode bits, then iterates over `MAX_TRAFFIC_CLASS` to write per-TC refill/max/BWG/strict-priority fields. PFC configuration iterates over all TCs and either disables thresholds or writes `FCRTL/FCRTH` according to `hw->fc.low_water`, `high_water`, and the PFC enable mask.

## State And Persistence
The file writes only adapter hardware registers. Persistent runtime effects include changed DCB arbitration, queue-statistic mapping, packet-buffer division, PFC receive/transmit mode, and pause timing until reset or later reconfiguration. It reads flow-control watermarks from `struct ixgbe_hw`.

## Dependencies And Integration Points
It depends on generic DCB structures from `ixgbe_dcb.h` and 82598-specific register definitions from `ixgbe_dcb_82598.h`. It is called by `ixgbe_dcb.c` for `ixgbe_mac_82598EB`, and by DCBNL-driven reconfiguration through the generic DCB dispatch path.

## Risks
- 82598 has distinct register names and arbitration semantics from 82599; using 82599-style priority maps here would be wrong.
- PFC uses TC-indexed bits directly, while 82599 PFC maps priorities to TCs; this difference matters when changing shared DCB code.
- TSO max credit and descriptor-plane programming are required to avoid stalls with large TX packets.
- Queue-statistic mappings are hard-coded to the 82598 queue layout and can become wrong if queue allocation changes.

## Test Signals
Use 82598 hardware or emulation to verify DCB enablement, RX/TX arbitration registers, PFC pause behavior per TC, TSO traffic under DCB, queue statistics attribution, reset/reapply behavior, and traffic-generator bandwidth distribution across all configured traffic classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb_82598.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb_82598.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb_82598.h

## Purpose
`ixgbe_dcb_82598.h` declares 82598-specific DCB register bit definitions and function prototypes. It is the hardware contract used by the 82598 DCB implementation to program arbitration, PFC, packet-buffer division, and stats mapping.

## Important APIs, Types, And Functions
- Register constants cover DPMCS, RUPPBMR, RT2CR, RDRXCTL, TDTQ2TCCR, TDPT2TCCR, PDPMCS, DTXCTL, buffer-size defaults, and RDRXCTL receive threshold behavior.
- Prototypes expose PFC configuration, RX arbiter configuration, TX descriptor arbiter configuration, TX data arbiter configuration, and aggregate DCB hardware configuration for 82598.

## Control Flow
Generic DCB dispatch includes this header and calls these functions when `hw->mac.type` is `ixgbe_mac_82598EB`. The `.c` implementation uses the bit shifts and masks here to compose MMIO register values from generic credit and priority arrays.

## State And Persistence
The header defines no state. Its constants describe hardware register fields that persist in the adapter until reset or reprogramming. The prototypes represent direct MMIO-mutating operations.

## Dependencies And Integration Points
This header is paired with `ixgbe_dcb_82598.c` and included by `ixgbe_dcb.c` and `ixgbe_dcb_nl.c`. It depends on generic ixgbe hardware definitions being available through includers.

## Risks
- Incorrect shifts or masks will misprogram hardware credits or priority mode and may cause bandwidth, PFC, or TX/RX stalls.
- Constants with names shared with 82599 headers, such as `IXGBE_RDRXCTL_MPBEN`, must stay compatible with each MAC family or be isolated.
- Function signatures must match the generic dispatch expectations; 82598 lacks `prio_tc` arguments used by 82599-family hardware.

## Test Signals
Build coverage for 82598 DCB paths, register readback after DCB setup, traffic-class bandwidth validation, PFC pause behavior, and reset/reapply testing are appropriate signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb_82598.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb_82599.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb_82599.c

## Purpose
`ixgbe_dcb_82599.c` programs DCB hardware for the 82599-family MACs, including 82599, X540, X550, X550EM_x, and x550em_a. It configures RX/TX packet and descriptor arbiters, UP-to-TC maps, priority flow control, and queue statistics for the newer register layout.

## Important APIs, Types, And Functions
- `ixgbe_dcb_config_rx_arbiter_82599()` disables RX arbitration, programs `RTRUP2TC`, writes `RTRPT4C` per-TC credits/BWG/link-strict bits, then reenables recycle/WSP arbitration.
- `ixgbe_dcb_config_tx_desc_arbiter_82599()` clears per-queue descriptor credits, writes per-TC `RTTDT2C` credits and strict-priority flags, then enables descriptor-plane arbitration.
- `ixgbe_dcb_config_tx_data_arbiter_82599()` disables TX packet arbitration, programs `RTTUP2TC`, writes `RTTPT2C` credits/BWG/strict-priority flags, then reenables SP/recycle arbitration with DCB arbitration delay.
- `ixgbe_dcb_config_pfc_82599()` switches TX flow control to priority mode, configures RX PFC in `MFLCN`, maps priority PFC bits through `prio_tc`, writes per-TC thresholds and pause timers, and clears unused TC thresholds.
- `ixgbe_dcb_config_tc_stats_82599()` maps RX and TX queues to TC statistic counters according to 82599-family queue allocation.
- `ixgbe_dcb_hw_config_82599()` applies the full backend in fixed order.

## Control Flow
The generic DCB layer supplies arrays of refill credits, max credits, bandwidth group IDs, priority types, and priority-to-TC mappings. RX and TX data arbiters first disable their arbiter before changing UP-to-TC and credit registers, then enable arbitration. TX descriptor arbitration clears 128 per-queue credit contexts because DCB uses per-TC registers instead. PFC configuration derives the highest TC from `prio_tc`, checks whether any priority mapped to each TC has PFC enabled, and chooses PFC thresholds or fallback internal-switch high-water thresholds.

## State And Persistence
The file persists no filesystem state. It mutates MMIO state governing DCB arbitration, UP-to-TC mapping, PFC behavior, pause timers, and queue-statistic attribution. Effects last until reset or another DCB reconfiguration. It reads `hw->fc.low_water`, `high_water`, and `pause_time`.

## Dependencies And Integration Points
It depends on `ixgbe_dcb.h` for generic DCB arrays and on `ixgbe_dcb_82599.h` for register masks/shifts. It is selected by `ixgbe_dcb.c` for 82599-family MAC types and used indirectly by DCBNL CEE/IEEE handlers.

## Risks
- UP-to-TC map and PFC enable masks use different domains: PFC enable is priority-indexed while thresholds are TC-indexed. Errors pause the wrong traffic.
- `MFLCN` handling differs for X540/X550, which support per-TC RX priority flow control; older 82599 behavior uses global RPFCE.
- Fallback high-water programming subtracts 24 KiB from RX packet-buffer size to prevent internal switch TX hangs; removing it can regress virtualization/internal-switch loads.
- Queue statistics mapping is hard-coded to the nonuniform TX queue layout and must match queue allocation.
- Arbiter-disable ordering protects against transient inconsistent hardware programming.

## Test Signals
Validate on 82599 and X540/X550-class devices with IEEE ETS and CEE configurations, UP-to-TC readback, per-priority PFC traffic tests, congestion tests with internal switching/SR-IOV enabled, queue-statistics attribution, 8-TC bandwidth distribution, and repeated reset/reapply of DCB configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb_82599.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb_82599.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb_82599.h

## Purpose
`ixgbe_dcb_82599.h` defines 82599-family DCB register masks, shifts, and programming entry points. It covers receive/transmit UP-to-TC mapping, RX and TX packet/descriptor arbitration, PFC-related behavior, and DCB-specific TX buffer inter-frame gap constants.

## Important APIs, Types, And Functions
- Constants cover `RTTDCS`, `RTRUP2TC`, `RTTUP2TC`, `RTRPT4C`, `RDRXCTL`, `RTRPCS`, `RTTDT2C`, `RTTPT2C`, `RTTPCS`, and `SECTXMINIFG` DCB fields.
- Prototypes declare PFC configuration, RX arbiter configuration, TX descriptor arbiter configuration, TX data arbiter configuration, and aggregate DCB hardware configuration for 82599-family devices.
- Function signatures include `prio_tc` where hardware needs priority-to-traffic-class mapping.

## Control Flow
Generic DCB code includes this header and calls its prototypes for 82599, X540, X550, X550EM_x, and x550em_a. The implementation composes MMIO register values from generic credit arrays and priority maps using these masks and shifts.

## State And Persistence
The header itself stores no state. It defines the register-field contract for persistent hardware configuration that remains active until reset or later DCB programming.

## Dependencies And Integration Points
It is paired with `ixgbe_dcb_82599.c` and included by generic DCB and DCBNL sources. It relies on ixgbe register base macros from the broader driver headers.

## Risks
- Bitfield mistakes affect hardware arbitration or PFC behavior globally for 82599-family devices.
- Shared macro names with 82598 headers require attention to include order and matching register semantics.
- The `prio_tc` API difference from 82598 is important for IEEE/CEE DCB correctness.

## Test Signals
Compilation across all 82599-family MAC types, DCB register readback, IEEE ETS and PFC configuration, UP-to-TC map verification, traffic-class bandwidth tests, and reset/reconfigure loops are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb_82599.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb_nl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb_nl.c

## Purpose
`ixgbe_dcb_nl.c` implements ixgbe's Linux DCB netlink operations. It exposes CEE and IEEE DCBX controls to user space, stages configuration in temporary adapter DCB state, applies changed settings to hardware, manages traffic-class resets, handles PFC and ETS set/get operations, and integrates DCB application priority changes with FCoE and SR-IOV defaults.

## Important APIs, Types, And Functions
- `ixgbe_dcbnl_ops` exports the driver's `struct dcbnl_rtnl_ops` callbacks.
- `ixgbe_copy_dcb_cfg()` compares `adapter->temp_dcb_cfg` against `adapter->dcb_cfg`, copies changed PG/PFC settings, and returns a bitmap of affected subsystems.
- CEE callbacks include state, permanent hardware address, PG TX/RX set/get, bandwidth group set/get, PFC set/get, `setall`, capabilities, TC count, PFC state, app get, and DCBX mode get/set.
- `ixgbe_dcbnl_set_all()` applies staged CEE changes: recalculates credits, programs ETS, updates netdev priority-to-TC maps, applies PFC or fallback link flow control, updates RX drop behavior, and resets for app/FCoE changes when needed.
- IEEE callbacks include `ieee_getets`, `ieee_setets`, `ieee_getpfc`, `ieee_setpfc`, `ieee_setapp`, and `ieee_delapp`.
- `ixgbe_dcbnl_devreset()` serializes with `__IXGBE_RESETTING`, stops the netdev if running, rebuilds interrupt scheme, reopens the netdev, and clears reset state.
- `ixgbe_dcbnl_setdcbx()` validates host-managed single-version DCBX modes and initializes ETS/PFC defaults when switching modes.

## Control Flow
CEE configuration is staged by individual setters into `temp_dcb_cfg`. `setall` copies changes into active `dcb_cfg`, determines whether PG, PFC, or app UP changed, then applies only affected hardware paths. PG changes calculate TX/RX credits from current MTU and FCoE jumbo constraints, unpack arrays, call `ixgbe_dcb_hw_ets_config()`, and update `netdev_set_prio_tc_map()`. PFC changes either program DCB PFC or reenable normal link flow control.

IEEE ETS set allocates `adapter->ixgbe_ieee_ets` lazily, initializes unknown UP-to-TC values, optionally reads current hardware map, computes `max_tc`, stores the requested ETS, validates TC count, calls `ixgbe_setup_tc()` when TC count changes or resets when only mapping changes, then programs hardware ETS. IEEE PFC set allocates/copies `ixgbe_ieee_pfc`, derives `prio_tc` from IEEE ETS, applies PFC or normal FC, and updates RX drop behavior. IEEE app add/delete delegates to kernel DCB helpers and then updates FCoE or VF default priority state as needed.

DCBX mode set rejects LLD-managed, mixed CEE+IEEE, and non-host modes. Switching to IEEE installs zeroed ETS/PFC defaults; switching to CEE marks all CEE subsystems changed and calls `setall`; disabling DCBX drops to single-TC mode.

## State And Persistence
State is runtime adapter memory and netdev/DCB core state, not filesystem state. Important fields include `adapter->dcb_cfg`, `temp_dcb_cfg`, `dcb_set_bitmap`, `dcbx_cap`, `ixgbe_ieee_ets`, `ixgbe_ieee_pfc`, `hw_tcs`, `flags`, `state`, FCoE UP, `default_up`, VF `pf_qos`/`pf_vlan`, and DCB app entries stored through kernel DCB helpers. Hardware programming persists until reset/reapply; traffic-class changes may rebuild interrupt schemes.

## Dependencies And Integration Points
The file depends on Linux DCBNL APIs, ixgbe adapter/netdev helpers, chip DCB backends, SR-IOV helpers (`ixgbe_set_vmvir`), traffic-class setup (`ixgbe_setup_tc`), RX drop policy (`ixgbe_set_rx_drop_en`), interrupt scheme management, optional `IXGBE_FCOE`, and kernel DCB app storage helpers (`dcb_getapp`, `dcb_ieee_setapp`, `dcb_ieee_delapp`, `dcb_ieee_getapp_mask`).

## Risks
- `ixgbe_dcbnl_ieee_setpfc()` assumes `adapter->ixgbe_ieee_ets` exists before dereferencing `prio_tc`; mode setup normally creates it, but unusual call ordering is a risk.
- DCBNL operations can trigger netdev stop/open and interrupt scheme rebuilds; locking and `__IXGBE_RESETTING` handling must prevent races with normal reset/service tasks.
- Incorrect change-bit detection can skip needed hardware updates or reset unnecessarily.
- CEE and IEEE state models are separate; mode switching must not leave stale PFC/ETS/app state in hardware.
- FCoE and VF default priority updates depend on app priority masks; regressions can break offload traffic class selection or guest VLAN/QoS programming.
- Capability reporting says fixed 8-TC support and rejects `setnumtcs`; callers need to handle fixed hardware policy.

## Test Signals
Exercise `dcbtool`/`lldptool`/`ip link dcb` CEE and IEEE flows, DCBX mode switching, ETS bandwidth/TSA programming, PFC enable/disable, app add/delete for FCoE and default ethertype priority, VF default UP propagation, reset during DCB changes, netdev open/close around TC changes, `ethtool -S` PFC counters, and error paths for invalid DCBX modes or TC mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb_nl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_debugfs.c

## Purpose
`ixgbe_debugfs.c` provides debugfs controls for ixgbe adapters. It creates a driver-level debugfs directory and per-adapter files that allow privileged users to read/write raw device registers and trigger selected netdev operations such as TX timeout handling.

## Important APIs, Types, And Functions
- `ixgbe_dbg_init()` creates the top-level debugfs directory named after `ixgbe_driver_name`.
- `ixgbe_dbg_adapter_init()` creates a per-adapter directory using `pci_name(adapter->pdev)` and files `reg_ops` and `netdev_ops`.
- `ixgbe_dbg_adapter_exit()` and `ixgbe_dbg_exit()` remove per-adapter and driver-level debugfs trees.
- `ixgbe_dbg_common_ops_read()` formats the last command buffer with the adapter netdev name and returns it as a single non-partial read.
- `ixgbe_dbg_reg_ops_write()` parses `read <reg>` and `write <reg> <value>` commands, performs MMIO access through `IXGBE_READ_REG` and `IXGBE_WRITE_REG`, and logs results.
- `ixgbe_dbg_netdev_ops_write()` parses `tx_timeout` and invokes `ndo_tx_timeout()`.
- `ixgbe_dbg_reg_ops_fops` and `ixgbe_dbg_netdev_ops_fops` wire the debugfs files to simple open/read/write operations.

## Control Flow
Module initialization creates the root directory. Adapter probe/start creates per-device entries with `adapter` as private data. Reads are allowed only from offset zero and allocate a formatted string with `kasprintf`; too-small user buffers return `-ENOSPC`. Writes are also only accepted at offset zero, bounded to 255 bytes plus terminator, copied with `simple_write_to_buffer`, parsed with `strncmp` and `sscanf`, then executed or logged as unknown commands. Adapter or module teardown removes debugfs entries recursively.

## State And Persistence
The file stores `ixgbe_dbg_root` and two static command buffers, `ixgbe_dbg_reg_ops_buf` and `ixgbe_dbg_netdev_ops_buf`. These buffers are global across adapters, so the last command is shared rather than per-adapter. Debugfs entries are runtime kernel objects and do not persist across module unload or reboot. Register writes mutate live hardware state immediately.

## Dependencies And Integration Points
The file depends on Linux debugfs, module file operations, simple buffer helpers, PCI naming, ixgbe adapter structures, netdev operations, and ixgbe MMIO/logging macros. It integrates with driver module init/exit and adapter probe/remove flows.

## Risks
- `reg_ops` exposes raw MMIO reads/writes to privileged debugfs users; incorrect writes can hang or misconfigure hardware.
- Static command buffers are shared among adapters and lack explicit locking, so concurrent debugfs writes can race and produce misleading readback/log messages.
- `tx_timeout` directly invokes the netdev timeout handler and can interfere with normal service/reset paths.
- File permissions are `0600`, but risk remains if debugfs is mounted and accessible to privileged automation.
- Buffer parsing is simple and accepts hex offsets/values without register-range validation.

## Test Signals
Signals include debugfs root and per-adapter file creation/removal, successful non-partial reads, `-ENOSPC` for oversized reads/writes, raw register read returning expected values, controlled write/readback on harmless scratch or documented registers, `tx_timeout` triggering the expected recovery path, teardown with open debugfs files, and concurrency smoke tests across multiple adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_debugfs.c -->
