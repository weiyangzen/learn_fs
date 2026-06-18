# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_main.c

## Purpose

`qlcnic_main.c` is the central PCI and netdev lifecycle implementation for the qlcnic driver. It declares module parameters and device IDs, registers the PCI driver, probes/removes adapters, selects 82xx/83xx/VF hardware operation tables, configures BAR mappings, firmware startup, interrupt topology, queue counts, netdev features, eSwitch/NPAR policy, open/close attach/detach, reset and firmware health work, PCI AER recovery, power management, VLAN/IP address notifications, and statistics/timeout handling.

## Important APIs, Types, And Functions

- Module parameters: `qlcnic_mac_learn`, `qlcnic_use_msi`, `qlcnic_use_msi_x`, `qlcnic_auto_fw_reset`, `qlcnic_load_fw_file`.
- `qlcnic_pci_tbl[]` lists supported physical and VF PCI IDs.
- `qlcnic_reg_tbl[]` maps shared register enum indexes to 82xx offsets.
- `qlcnic_netdev_ops` binds Linux netdev operations to qlcnic handlers.
- `qlcnic_ops`, `qlcnic_vf_ops`, and `qlcnic_hw_ops` bind generic driver calls to concrete implementations.
- Interrupt helpers configure MSI-X/MSI/legacy interrupts and queue counts.
- PCI/adapter helpers set up BAR0, hardware contexts, VF/privilege mode, eSwitch mode, and netdev features.
- Lifecycle helpers include `qlcnic_probe()`, `qlcnic_remove()`, `qlcnic_attach()`, `qlcnic_detach()`, `__qlcnic_up()`, `__qlcnic_down()`, `qlcnic_open()`, and `qlcnic_close()`.
- Firmware/reset helpers include `qlcnic_82xx_start_firmware()`, `qlcnic_can_start_firmware()`, delayed work handlers, and `qlcnic_check_health()`.
- AER/PM helpers implement PCI error recovery, suspend/resume, and shutdown.
- IPv4 notifier helpers restore and update firmware IP address state for base and VLAN devices.

## Control Flow

Module init registers notifiers and the PCI driver. Probe enables PCI, requests regions, maps BAR0, allocates netdev/adapter/hardware context, selects chip-specific operations, creates a workqueue, initializes resources, starts firmware, reads MAC/port identity, configures DCB and interrupts, discovers PCI/eSwitch information, sets netdev features and queue counts, registers the netdev, starts firmware polling, and registers sysfs/hwmon.

82xx firmware startup uses shared device state to decide whether this function owns initialization. It may load external firmware or validate flash firmware, preinitialize hardware from ROM, write firmware into adapter memory, wait for PEG readiness, set device ready, configure eSwitch/management state, and update board/options.

Open calls attach and up. Attach adds NAPI, allocates software/hardware rings, requests IRQs, and creates sysfs entries. Up applies eSwitch config, creates firmware contexts, posts RX buffers, configures MAC filters, MTU, RSS, coalescing, LRO, enables NAPI/interrupts, requests link events, and starts TX queues.

Down clears device-up state, disables carrier/TX, frees MAC and learned filters, disables NAPI, destroys firmware contexts, resets RX lists, and releases TX buffers. Detach removes sysfs, frees hardware resources, releases RX buffers, frees IRQs, deletes NAPI, and frees software resources.

Firmware health polling monitors temperature, reset requests, device state, heartbeat, and context reset state. On hang/reset, it schedules detach/reinit work or takes dumps. Detach work quiesces the interface and acknowledges reset/quiesce. Firmware init work reloads or waits for firmware readiness, then attach work restores the interface and IP address state.

Interrupt setup prefers MSI-X, can reduce ring counts on vector shortage, and falls back to MSI or legacy. Request/free IRQ mirrors whether RX and TX interrupts are shared or split.

AER recovery detaches and disables the device, then slot reset re-enables PCI, restarts firmware, rebuilds interrupts, reattaches the netdev, and resumes polling.

## State And Persistence Behavior

Driver state includes adapter state bits, flags, queue counts, ring arrays, firmware version, port number, MAC address, DCB state, NPAR/eSwitch tables, VLAN bitmap, learned filter hashes, delayed work, and stats. Device coordination persists in shared CRB registers for driver active references, reset/quiesce acknowledgements, device state, NPAR state, IDC version, heartbeat, PEG halt status, firmware version, and operation mode.

Resource ownership is layered: probe/remove own PCI and netdev resources; attach/detach own NAPI, IRQs, and rings; up/down own firmware contexts, posted buffers, link events, and TX queues.

## Dependencies And Integration Points

This file integrates with `qlcnic_hw.c`, `qlcnic_init.c`, `qlcnic_io.c`, 83xx-specific code, SR-IOV, DCB, ethtool, sysfs, hwmon, firmware dump logic, Linux PCI/PM/AER, netdevice, notifier, VLAN, VXLAN UDP tunnel, DMA, interrupt, and workqueue APIs.

Function-pointer tables are the main abstraction boundary: probe chooses concrete operations, while the rest of the driver calls generic wrappers.

## Risks

- Multi-function firmware reset coordination is timing-sensitive; bad shared-state updates can strand other functions.
- MSI-X fallback changes active ring counts, so code must use final counts after interrupt setup.
- Probe and maintenance-mode fallback have complex cleanup ordering.
- MAC-learning allocation can partially initialize hash tables.
- `qlcnic_setup_rings()` has early failure paths that require care around device attach/reset state.
- Health polling, AER, suspend/resume, TX timeout, and ring changes all interact with reset serialization bits.
- Netdev features depend on firmware capabilities initialized earlier.

## Test Signals

Exercise probe/remove for supported PF/VF IDs, open/close cycles, MSI-X/MSI/legacy interrupt modes, ring-count changes, DCB, eSwitch/NPAR operations, VLAN/FDB, VXLAN tunnel notification, suspend/resume, AER recovery, firmware health reset, TX timeout recovery, maintenance-mode registration, and module unload. Watch logs for device state transitions, IDC mismatch, NPAR timeout, vector allocation fallback, IRQ failures, firmware hang/PEG halt, temperature alerts, and stats updates.
