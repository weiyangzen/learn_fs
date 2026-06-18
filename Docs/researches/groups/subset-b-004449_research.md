# Research: subset-b-004449

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/82571.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/82571.c

## Purpose

This file is the hardware-specific implementation for Intel e1000e PCIe controllers in the 82571/82572/82573/82574/82583 family. It binds generic e1000e MAC, PHY, and NVM helper code to these devices by initializing operation vectors, applying silicon workarounds, handling shared PHY/NVM semaphores, configuring link media, and publishing the `e1000_info` descriptors consumed by probe-time board selection.

## Important APIs, Types, and Functions

The exported or externally visible entry points are `e1000_check_phy_82574()`, `e1000e_get_laa_state_82571()`, `e1000e_set_laa_state_82571()`, and the constant `e1000_info` instances for `e1000_82571_info`, `e1000_82572_info`, `e1000_82573_info`, `e1000_82574_info`, and `e1000_82583_info`. These descriptors advertise board flags, PBA sizes, max frame sizes, and the MAC/PHY/NVM operation tables.

Probe-time specialization flows through `e1000_get_variants_82571()`, which calls `e1000_init_mac_params_82571()`, `e1000_init_nvm_params_82571()`, and `e1000_init_phy_params_82571()`. The init functions select media type, choose PHY model, install function pointers, derive NVM geometry from `EECD`, verify PHY IDs, tag quad-port cards, and adjust Wake-on-LAN/jumbo-frame capability flags.

Reset and initialization center on `e1000_reset_hw_82571()` and `e1000_init_hw_82571()`. Reset disables PCIe master access, masks interrupts, disables Rx/Tx, acquires MDIO ownership where required, asserts `CTRL.RST`, waits for NVM auto-read, clears stale interrupt causes, installs alternate MAC addresses, and resets SerDes state. Hardware init applies errata bits via `e1000_initialize_hw_bits_82571()`, clears VLAN filters, initializes receive addresses and multicast hash, sets up link, programs transmit descriptor write-back policy, and clears counters.

PHY/NVM arbitration is implemented with `e1000_get_hw_semaphore_82571()`, `e1000_put_hw_semaphore_82571()`, `e1000_get_hw_semaphore_82573()`, and the mutex-protected 82574 wrappers. NVM access is mediated by `e1000_acquire_nvm_82571()`, `e1000_release_nvm_82571()`, `e1000_write_nvm_82571()`, `e1000_write_nvm_eewr_82571()`, `e1000_update_nvm_checksum_82571()`, `e1000_validate_nvm_checksum_82571()`, and `e1000_fix_nvm_checksum_82571()`.

Link setup uses `e1000_setup_link_82571()`, `e1000_setup_copper_link_82571()`, `e1000_setup_fiber_serdes_link_82571()`, and `e1000_check_for_serdes_link_82571()`. The SerDes checker maintains a four-state software state machine: down, autonegotiation in progress, autonegotiation complete, and forced up.

## Control Flow

At device setup, generic netdev probe code selects one of the `e1000_info` records and copies its operation tables into `struct e1000_hw`. `get_variants` refines the generic table for the concrete device ID and port role. Later generic e1000e paths invoke these callbacks for reset, init, link setup, PHY access, NVM access, counter clearing, LED control, VLAN table handling, and MAC address reads.

The reset path is deliberately staged: quiesce DMA and interrupts, coordinate with firmware or the sibling port, assert MAC reset, wait for NVM and PHY configuration, then clean interrupt and address state. The init path assumes reset has made the device quiescent and then writes normal-operation configuration and errata workarounds.

Copper link setup sets `CTRL.SLU`, clears forced speed/duplex, delegates PHY-specific setup for M88/BM/IGP PHYs, then calls the generic copper link flow. Fiber and SerDes setup clears sticky loopback state on 82571/82572 before delegating to generic fiber/SerDes setup. SerDes link checks read `RXCW`, `STATUS`, `TXCW`, and `CTRL`, transitioning between autonegotiated and forced-link states depending on synchronization, invalid code groups, ordered sets, and link-up state.

## State and Persistence Behavior

Persistent hardware state includes NVM contents, checksum words, LED defaults, alternate MAC address words, and firmware-controlled flash update state. Runtime state lives in `struct e1000_hw`: `mac.ops`, `phy.ops`, `nvm.ops`, `phy.type`, `phy.media_type`, `mac.serdes_link_state`, `mac.serdes_has_link`, `dev_spec.e82571.laa_is_present`, and `dev_spec.e82571.smb_counter`. The static `global_quad_port_a` counter tags ports on quad-port adapters, and `swflag_mutex` serializes 82574/82583 software ownership within the driver.

The code modifies registers that survive until reset or power transition, including `CTRL`, `CTRL_EXT`, `SWSM`, `SWSM2`, `EECD`, `TXDCTL`, `TARC`, `RFCTL`, `GCR`, `GCR2`, `VFTA`, `LEDCTL`, `POEMB`, and NVM access registers. NVM writes are checksum-sensitive and may commit to flash using `EECD.FLUPD` after clearing flash-update hazards.

## Dependencies and Integration Points

This file depends on generic e1000e helpers from `mac.c`, `phy.c`, `nvm.c`, and `manage.c`, register definitions from `regs.h`, constants from `defines.h` and `82571.h`, and structures from `e1000.h`/`hw.h`. It integrates with PCI IDs in `hw.h`, netdev state in `struct e1000_adapter`, ethtool paths through operation callbacks and public LAA/PHY helpers, and power management through PHY power-down and low-power link-up callbacks.

## Risks and Edge Cases

The highest-risk areas are hardware semaphore handling, NVM writes, reset ordering, and errata register programming. A missed semaphore release can block PHY/NVM access across ports; an incorrect NVM write or checksum update can persistently misconfigure the adapter; reset changes must preserve firmware/AMT ownership constraints; and the SerDes forced-link fallback can misreport link if ordered-set handling regresses.

Specific risk signals include the workaround for old boot agents leaving `SWSM.SMBI` set, the `smb_counter` shortening future lock waits after repeated timeouts, 82574/82583 mutex pairing around MDIO ownership, `FLAG_RESET_OVERWRITES_LAA` mitigation by copying LAA into the last RAR, and the flash checksum fix that mutates word `0x23`.

## Test Signals

Useful tests are probe/reset smoke tests on each MAC type, PHY ID verification, repeated up/down cycles, NVM read/write/checksum validation, Wake-on-LAN capability checks by port role, VLAN filtering with manageability VLAN preservation, SerDes/fiber autoneg and forced-link tests, copper forced/autoneg speed tests, and ethtool offline diagnostics. Register-level tests in `ethtool.c` cover many of the registers this file programs, while link and loopback tests exercise the installed operation vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/82571.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/82571.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/82571.h

## Purpose

This header contains 82571-family local constants and prototypes needed by the shared e1000e hardware abstraction. It supplements the broad register/bit definitions in `defines.h` with family-specific LED defaults, interrupt register offsets, manageability masks, PHY hang-detection constants, and public helper declarations.

## Important APIs, Types, and Functions

The header declares `e1000_check_phy_82574()`, `e1000e_get_laa_state_82571()`, and `e1000e_set_laa_state_82571()`. These functions are implemented in `82571.c` and used by other driver files that need 82574 PHY hang detection or 82571 locally administered address state.

Important constants include `ID_LED_RESERVED_F746`, `ID_LED_DEFAULT_82573`, `E1000_GCR_L1_ACT_WITHOUT_L0S_RX`, `AN_RETRY_COUNT`, `E1000_EITR_82574(_n)`, `E1000_EIAC_82574`, `E1000_EIAC_MASK_82574`, `E1000_IVAR_INT_ALLOC_VALID`, `E1000_NVM_INIT_CTRL2_MNGM`, `E1000_BASE1000T_STATUS`, `E1000_IDLE_ERROR_COUNT_MASK`, `E1000_RECEIVE_ERROR_COUNTER`, and `E1000_RECEIVE_ERROR_MAX`.

## Control Flow

There is no executable control flow in this file. It influences runtime behavior through constants consumed by reset, interrupt, LED, manageability, SerDes autonegotiation, and PHY health-check logic. The `AN_RETRY_COUNT` macro bounds retry loops in the SerDes link state machine, and the PHY error constants define the comparison used by `e1000_check_phy_82574()`.

## State and Persistence Behavior

The header does not own state. It names register offsets and bit masks that affect persistent or semi-persistent device state when used by implementation files, notably LED configuration derived from NVM, interrupt throttling/autoclear registers on 82574, and NVM manageability mode bits.

## Dependencies and Integration Points

`hw.h` includes this header after defining `struct e1000_hw`, making these prototypes available across the e1000e driver. The constants depend on LED macros from `defines.h`, and callers rely on the include order through `hw.h`.

## Risks and Edge Cases

Changing these values can silently alter hardware programming in other files. The interrupt offsets are hardware ABI values; incorrect values would direct writes to the wrong MMIO registers. The LED defaults are used to repair reserved NVM LED words. The PHY hang constants are exact sentinel values; broadening them could trigger false-positive resets, while narrowing them could miss a wedged PHY.

## Test Signals

Build coverage catches prototype/include regressions. Runtime signals include valid LED behavior on 82573/82574/82583, successful MSI-X interrupt routing on 82574, SerDes link transitions bounded by `AN_RETRY_COUNT`, and correct PHY hang detection when receive and idle error counters saturate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/82571.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/Makefile

## Purpose

This Kbuild file defines how the Intel e1000e driver is compiled as the `e1000e.o` module or built-in object when `CONFIG_E1000E` is enabled. It lists the object files that make up the driver and ensures the local directory is on the include path.

## Important APIs, Types, and Functions

The key Kbuild variables are `ccflags-y += -I$(src)`, `subdir-ccflags-y += -I$(src)`, `obj-$(CONFIG_E1000E) += e1000e.o`, and `e1000e-y := ...`. The object list includes hardware-family files (`82571.o`, `ich8lan.o`, `80003es2lan.o`), common hardware helpers (`mac.o`, `manage.o`, `nvm.o`, `phy.o`), driver integration (`param.o`, `ethtool.o`, `netdev.o`), and time synchronization (`ptp.o`).

## Control Flow

There is no runtime control flow. At build time, Kbuild expands `e1000e-y` into a composite object. Link order matters enough to keep all referenced symbols available in the final driver, though the driver mostly uses explicit function tables and exported internal symbols rather than initcall order within this Makefile.

## State and Persistence Behavior

The file does not store runtime state. Its persistent effect is the build composition: adding or removing an object changes which MAC families, ethtool operations, netdev operations, and PTP support are present.

## Dependencies and Integration Points

It integrates with the kernel Kbuild system and the `CONFIG_E1000E` Kconfig option. The include-path flags support local quoted includes such as `#include "e1000.h"` and trace include resolution for `e1000e_trace.h`.

## Risks and Edge Cases

Omitting a listed object would cause missing symbols or a driver that probes without required hardware support. Removing `-I$(src)` can break local includes, especially for generated trace definitions in loadable-module builds. Adding new source files for this driver requires updating `e1000e-y`.

## Test Signals

The main test signal is a successful kernel/module build with `CONFIG_E1000E=m` and `CONFIG_E1000E=y`. Link-time unresolved-symbol failures point directly at missing object membership. Runtime probe coverage confirms that all board-family operation tables are included.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/defines.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/defines.h

## Purpose

This header is the central bit-field and constant catalog for e1000e hardware programming. It defines descriptor bits, register masks, advertised link modes, interrupt bits, flow-control constants, NVM commands and offsets, PHY IDs, PHY register fields, timeout bounds, power-management flags, timestamping bits, and error codes used by the driver implementation files.

## Important APIs, Types, and Functions

There are no functions or types, only macros. Important groups include descriptor definitions (`E1000_RXD_*`, `E1000_RXDEXT_*`, `E1000_TXD_*`), control/status bits (`E1000_CTRL_*`, `E1000_STATUS_*`, `E1000_RCTL_*`, `E1000_TCTL_*`), flow-control and VLAN masks (`E1000_FCRTH_RTH`, `E1000_FCRTL_RTL`, `E1000_VLAN_FILTER_TBL_SIZE`), interrupt masks (`E1000_ICR_*`, `E1000_IMS_*`, `IMS_ENABLE_MASK`, `IMS_OTHER_MASK`), NVM fields (`E1000_EECD_*`, `NVM_*`, `NVM_SUM`), PHY IDs and registers (`IGP01E1000_I_PHY_ID`, `M88E1111_I_PHY_ID`, `BME1000_E_PHY_ID_R2`, `M88E1000_*`, `GG82563_*`, `E1000_MDIC_*`), and PTP timestamping constants (`E1000_TSYNCTXCTL_*`, `E1000_TSYNCRXCTL_*`, `E1000_TIMINCA_*`).

## Control Flow

The file has no direct control flow, but it shapes almost every hardware branch in the driver. Runtime code tests these masks after MMIO or PHY reads, composes register writes from them, uses timeout macros to bound polling loops, and uses error-code macros for internal helper failures. Several compound masks, such as `E1000_RXD_ERR_FRAME_ERR_MASK`, `PCIE_NO_SNOOP_ALL`, and advertised speed sets, encode reusable policy.

## State and Persistence Behavior

Many macros name persistent or semi-persistent device state. NVM offsets and checksum constants affect EEPROM/flash contents that survive reboot. Wake, power, LED, flow-control, descriptor, and timestamp bits affect hardware register state until reset or reprogramming. The error-code constants are internal status values and are not persisted.

## Dependencies and Integration Points

`hw.h` includes this file after `regs.h`, making the constants globally available through `e1000.h`. Implementation files including `82571.c`, `ethtool.c`, MAC/PHY/NVM helpers, netdev paths, and PTP code depend on these definitions matching the hardware manuals. It also uses common kernel helpers such as `BIT()` and field macros through including contexts.

## Risks and Edge Cases

This file is high blast-radius despite containing no code. A wrong bit mask can produce silent hardware misprogramming, data corruption, interrupt loss, broken power management, invalid NVM checksums, or bad timestamp reporting. Timeout constants balance hardware latency against boot/probe delays. Some values intentionally encode unsupported behavior, such as no 1000 half-duplex advertisement, and should not be generalized.

## Test Signals

Compile coverage catches only syntax and missing macro issues. Stronger signals are ethtool register tests, EEPROM checksum tests, interrupt tests, loopback diagnostics, Wake-on-LAN tests, timestamping validation, speed/autoneg negotiation, VLAN filter tests, and reset/power-cycle stress across multiple e1000e MAC families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/defines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/e1000.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/e1000.h

## Purpose

This is the main Linux e1000e driver header. It connects kernel networking, PCI, DMA, timestamping, workqueue, and hardware abstraction definitions into the central software state used by the driver. It also declares cross-file driver entry points and provides inline wrappers for PHY, NVM, MAC address, and MMIO register access.

## Important APIs, Types, and Functions

Important data structures include `struct e1000_ps_page`, `struct e1000_buffer`, `struct e1000_ring`, `struct e1000_phy_regs`, `struct e1000_adapter`, and `struct e1000_info`. `struct e1000_adapter` is the main netdev-private object and stores timers, work items, descriptor rings, interrupt settings, Tx/Rx counters, hardware state, test rings, WOL state, PTP state, feature flags, and PHY/NVM snapshots. `struct e1000_info` is the probe-time board descriptor that selects MAC type, flags, PBA, frame size, variant callback, and operation tables.

The header declares major driver functions including option parsing, ethtool setup, open/close, up/down, reset, resource allocation/freeing, statistics, interrupt capability management, hardware-control ownership, ITR writes, and PTP init/remove/read helpers.

Inline wrappers include `e1000_phy_hw_reset()`, `e1e_rphy()`, `e1e_rphy_locked()`, `e1e_wphy()`, `e1e_wphy_locked()`, `e1000e_read_mac_addr()`, `e1000_validate_nvm_checksum()`, `e1000e_update_nvm_checksum()`, `e1000_read_nvm()`, `e1000_write_nvm()`, `e1000_get_phy_info()`, `__er32()`, `er32()`, `__ew32()`, `ew32()`, `e1e_flush()`, `E1000_WRITE_REG_ARRAY()`, and `E1000_READ_REG_ARRAY()`.

## Control Flow

This header does not implement large control flows, but it defines the call surface used by all implementation files. Generic code typically retrieves `struct e1000_adapter` from a `net_device`, accesses `adapter->hw`, and dispatches through `hw->mac.ops`, `hw->phy.ops`, or `hw->nvm.ops`. The inline wrappers make that dispatch look like normal function calls while still allowing per-MAC specialization installed from `struct e1000_info`.

## State and Persistence Behavior

`struct e1000_adapter` stores most runtime state: link speed/duplex, active VLAN bitmap, reset/testing/down bits, interrupt throttle settings, ring counts and DMA descriptors, software and hardware statistics, WOL settings, hardware timestamp state, PTP clock state, EEE advertisement, and capability flags. Persistent device information is represented by NVM fields cached in the adapter (`eeprom_vers`, `eeprom_wol`, `pba`) and by `struct e1000_hw`.

The state bit enum defines concurrency gates for testing, resetting, shared-resource access, and down state. The flag and flag2 bitfields encode hardware capabilities and errata workarounds that drive behavior throughout the driver.

## Dependencies and Integration Points

The header includes Linux kernel APIs for netdev, PCI, timers, workqueues, I/O, VLAN, timestamping, PTP, MII/MDIO, mutexes, and PM QoS, then includes `hw.h` for hardware structures. It is included by nearly every e1000e `.c` file and is the primary integration point between generic kernel subsystems and e1000e hardware-specific code.

## Risks and Edge Cases

Because this header defines shared structures, field layout changes affect all driver files and any code using offsets for statistics. The register macros assume a local variable named `hw`, so misuse in a scope without the expected pointer will fail or target the wrong state if shadowed. Operation-pointer wrappers assume the relevant callbacks were initialized for the detected MAC/PHY/NVM combination.

## Test Signals

Compile coverage is important for structure and prototype changes. Runtime signals include successful probe, open/close, reset, ring allocation, ethtool statistics, PTP clock registration, timestamping, VLAN and WOL behavior, and correct operation across MSI/MSI-X/legacy interrupt modes. Static analysis should focus on state-bit synchronization, DMA ring lifetime, and operation-pointer nullability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/e1000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/e1000e_trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/e1000e_trace.h

## Purpose

This header defines an e1000e tracepoint provider for Linux ftrace/perf tracing. It creates the `e1000e_trace` trace system and one event, `e1000e_trace_mac_register`, for reporting a MAC register value.

## Important APIs, Types, and Functions

The key API is `TRACE_EVENT(e1000e_trace_mac_register, ...)`. It takes one `uint32_t reg` argument, stores it in the trace entry, and formats it as a hexadecimal MAC register value. The file also sets `TRACE_SYSTEM`, `TRACE_INCLUDE_PATH`, and `TRACE_INCLUDE_FILE`, then includes `<trace/define_trace.h>` as required for tracepoint generation in a loadable module.

## Control Flow

There is no normal runtime control flow in the header. At compile time, the Linux tracepoint macros generate declarations or definitions depending on include context and `TRACE_HEADER_MULTI_READ`. At runtime, any call site that invokes the generated trace function emits the event if tracing is enabled.

## State and Persistence Behavior

The tracepoint does not own persistent driver state. Trace records are transient kernel tracing data. The only stored field per event is the register value passed by the caller.

## Dependencies and Integration Points

The file depends on `<linux/tracepoint.h>` and the kernel trace generation convention that `TRACE_INCLUDE_FILE` match the header basename. The local include path in the Makefile helps the trace generator find this module-local header.

## Risks and Edge Cases

Trace headers are sensitive to include-order and macro conventions. Moving this file or changing `TRACE_INCLUDE_PATH`/`TRACE_INCLUDE_FILE` can break generated trace definitions. The event currently carries only a raw register value, so it is low overhead but provides limited context unless callers encode meaningful values.

## Test Signals

Build success with tracing enabled is the first signal. Runtime signals are the presence of the `e1000e_trace:e1000e_trace_mac_register` event under tracing facilities and successful event capture when call sites execute.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/e1000e_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/ethtool.c

## Purpose

This file implements the e1000e driver's ethtool interface. It exposes link settings, pause parameters, register dumps, EEPROM access, ring sizing, private flags, coalescing, Wake-on-LAN, LED identification, statistics, RSS hash fields, EEE, timestamp capabilities, and online/offline diagnostics to user space.

## Important APIs, Types, and Functions

The file installs `e1000_ethtool_ops` through `e1000e_set_ethtool_ops()`. Important operation handlers include `e1000_get_link_ksettings()`, `e1000_set_link_ksettings()`, `e1000_get_pauseparam()`, `e1000_set_pauseparam()`, `e1000_get_regs()`, `e1000_get_eeprom()`, `e1000_set_eeprom()`, `e1000_get_ringparam()`, `e1000_set_ringparam()`, `e1000_diag_test()`, `e1000_get_wol()`, `e1000_set_wol()`, `e1000_set_phys_id()`, `e1000_get_coalesce()`, `e1000_set_coalesce()`, `e1000_get_ethtool_stats()`, `e1000_get_rxfh_fields()`, `e1000e_get_eee()`, `e1000e_set_eee()`, `e1000e_get_ts_info()`, `e1000e_get_priv_flags()`, and `e1000e_set_priv_flags()`.

`struct e1000_stats` maps ethtool statistic names to either `struct rtnl_link_stats64` or `struct e1000_adapter` offsets. The private flags are `s0ix-enabled` and `disable-k1`.

Diagnostic helpers include register pattern tests, EEPROM checksum tests, interrupt forcing tests, descriptor-ring setup/free for loopback, PHY/MAC/fiber loopback setup and cleanup, loopback frame creation/verification, and link tests.

## Control Flow

Setters that alter hardware-visible state generally acquire the reset gate by setting `__E1000_RESETTING`, then reset or cycle the interface. Link setting changes validate SoL/IDER reset blocks, MDI/MDI-X restrictions, autonegotiation, speed, and duplex before calling `e1000e_down()`/`e1000e_up()` or `e1000e_reset()`. Pause changes either restore default autonegotiated flow control or force MAC flow control and watermarks.

EEPROM reads compute word ranges around byte offsets, allocate a temporary buffer, read via NVM ops, endian-convert, and copy the requested byte span. EEPROM writes validate magic and read-only flags, preserve partial leading/trailing words with read-modify-write, convert endianness, write through NVM ops, and update checksums when needed.

Ring resizing clamps and aligns descriptor counts, blocks concurrent reset, optionally allocates replacement rings while the interface is down, then swaps resources so MSI-X handlers that reference ring structures remain valid.

Offline diagnostics close the interface if running, run register, EEPROM, interrupt, loopback, and link tests with resets between stages, restore saved autoneg/speed state, and reopen the interface. Online diagnostics only run the link test. Loopback diagnostics allocate test rings, program Tx/Rx descriptors and MAC/PHY loopback mode, transmit recognizable frames, poll Rx buffers for matching markers, then clean up.

## State and Persistence Behavior

The file reads and mutates `struct e1000_adapter` fields including link settings, `fc_autoneg`, `msg_enable`, ring counts, WOL mask, interrupt mode, test interrupt cause, test rings, `itr`/`itr_setting`, `flags2`, `eee_advert`, and saved loopback scratch state. It reads/writes hardware registers, PHY registers, and NVM contents. EEPROM writes and WOL device wake settings can persist beyond the immediate ethtool call.

Diagnostic paths are intentionally disruptive in offline mode: they reset hardware, alter loopback bits, allocate DMA rings, request/free IRQs, and close/reopen the netdev. Cleanup restores loopback state, frees DMA mappings, and clears testing/reset bits.

## Dependencies and Integration Points

This file integrates Linux ethtool, netdev, PCI, DMA, IRQ, PM runtime, MII/MDIO, EEE, and timestamping APIs with e1000e internal helpers from `e1000.h`. It relies on operation vectors initialized by hardware-family files such as `82571.c`, and on constants from `defines.h`, `hw.h`, PHY headers, and register definitions.

## Risks and Edge Cases

Risk concentrates around user-triggered hardware mutation. EEPROM writes can persist bad configuration if validation or checksum handling fails. Offline tests intentionally disrupt traffic. Interrupt tests temporarily force legacy mode when MSI-X is active. Ring resizing must not free structures still referenced by interrupt handlers. Loopback setup has many MAC/PHY-specific paths and requires cleanup to avoid leaving loopback or forced-link state enabled. Setters must consistently clear `__E1000_RESETTING` on all exits.

Input validation is important for unsupported speed/duplex combinations, MDI settings without autonegotiation, unsupported WOL masks, read-only NVM, EEE advertisement limited to 100/1000 full duplex, unsupported S0ix or K1 private flags, and coalescing values outside supported ITR ranges.

## Test Signals

Direct test signals are `ethtool -i`, `-k/-S/-d/-e/-E`, `-g/-G`, `-c/-C`, `-a/-A`, `-s`, `-r`, `-p`, `-t online`, and `-t offline` on representative hardware. Strong automated checks include concurrent reset/ring-setting stress, EEPROM read/write failure injection, WOL suspend/resume, EEE get/set on supported PCH PHYs, timestamp capability reporting on 82574/82583, and loopback cleanup verification after test failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/hw.h

## Purpose

This header defines the e1000e hardware abstraction: PCI device IDs, MAC/PHY/NVM/media enums, descriptor layouts, hardware statistic structures, operation-vector types, per-subsystem state structures, and the top-level `struct e1000_hw`. It is the contract between family-specific hardware files and generic netdev/ethtool/PTP code.

## Important APIs, Types, and Functions

Important enums include `e1000_mac_type`, `e1000_media_type`, `e1000_nvm_type`, `e1000_nvm_override`, `e1000_phy_type`, `e1000_bus_width`, `e1000_1000t_rx_status`, `e1000_rev_polarity`, `e1000_fc_mode`, `e1000_ms_type`, `e1000_smart_speed`, `e1000_serdes_link_state`, and `e1000_ulp_state`.

Important hardware data layouts include `union e1000_rx_desc_extended`, `union e1000_rx_desc_packet_split`, `struct e1000_tx_desc`, `struct e1000_context_desc`, `struct e1000_data_desc`, `struct e1000_hw_stats`, `struct e1000_phy_stats`, and host-management command/cookie structures.

The operation vectors are `struct e1000_mac_operations`, `struct e1000_phy_operations`, and `struct e1000_nvm_operations`. State structures include `struct e1000_mac_info`, `struct e1000_phy_info`, `struct e1000_nvm_info`, `struct e1000_bus_info`, `struct e1000_fc_info`, per-family `dev_spec` structures, and the aggregate `struct e1000_hw`.

## Control Flow

This header has no executable control flow, but it defines the dispatch model used throughout the driver. Probe code identifies a PCI device, selects a MAC type and `e1000_info` descriptor, copies operation tables into `struct e1000_hw`, and later generic paths invoke callbacks through `mac.ops`, `phy.ops`, and `nvm.ops`. The enums and state fields determine branches for media setup, reset behavior, NVM access method, PHY register access, power management, flow control, and SerDes link handling.

## State and Persistence Behavior

`struct e1000_hw` contains the live hardware-facing state: MMIO base pointers, MAC information, flow control settings, PHY state, NVM geometry, bus state, management cookie, and per-family device-specific state. Descriptor structures model DMA memory shared with hardware. `struct e1000_hw_stats` and `struct e1000_phy_stats` cache counters read from clear-on-read hardware registers. NVM and management structures represent persistent EEPROM/flash and firmware-facing command layouts.

## Dependencies and Integration Points

The header includes `regs.h` and `defines.h`, then includes family headers `82571.h`, `80003es2lan.h`, and `ich8lan.h` after `struct e1000_hw` is defined. It also includes `mac.h`, `phy.h`, `nvm.h`, and `manage.h` so operation signatures and helper declarations are available. `e1000.h` includes this file and exposes it to all main driver components.

## Risks and Edge Cases

This is a high-risk shared contract. Changing descriptor layout, endian annotations, operation-vector signatures, enum ordering, or state fields can break DMA interpretation, hardware-family dispatch, stats collection, or per-MAC workarounds. The union `dev_spec` requires each MAC family to use only its own member. Descriptor definitions must match hardware byte layout exactly.

## Test Signals

Build coverage catches many signature and layout reference errors, but hardware validation is required. Useful signals include successful probe for every listed PCI ID family, descriptor Tx/Rx traffic under checksum/TSO/VLAN/timestamp features, stats consistency, NVM access, PHY info reporting, SerDes state transitions, flow-control negotiation, and suspend/resume behavior across families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/hw.h -->
