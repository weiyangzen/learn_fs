# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx.c

Purpose: Main SFC PCI/netdev driver entry for non-EF100 PCI IDs, plus shared module initialization that registers both legacy SFC and EF100 PCI drivers. It orchestrates NIC probe/remove, netdev operations, port lifecycle, XDP attachment, stats, PM, SR-IOV configure dispatch, and device association.

Important APIs and functions: Exports `efx_net_open()`, `efx_net_stop()`, and `efx_update_sw_stats()`. Defines `efx_netdev_ops`, queue stat ops, PCI probe/remove, PM callbacks, PCI device table, module init/exit, port/NIC probe/remove helpers, XDP setup/xmit helpers, netdev registration, and SR-IOV PCI configure bridge.

Control flow: PCI probe allocates `efx_probe_data` and `net_device`, initializes common struct and IO mappings, runs `efx_pci_probe_post_io()` with retries, registers devlink/netdev, probes optional MTDs, and pushes UDP tunnel ports. Main probe creates NIC resources, port, vswitching, filters, channels, NAPI, hardware init, port init, interrupts, and affinity. Open checks disabled/special/reboot states, reports link, starts all datapath components, and marks NET_UP. Stop calls `efx_stop_all()`. Remove dissociates, closes the netdev, disables interrupts, finalizes SR-IOV/devlink/netdev/MTD, removes all resources, unmaps IO, and frees memory.

State and persistence: Manages `efx->state`, channel counts, VPD serial, primary/secondary association lists, netdev feature flags, carrier, XDP program pointer, MTD names, PCI drvdata, and PM freeze/thaw state. Hardware, PCI, and netdev registrations persist until explicit unregister/remove.

Dependencies and integration points: Integrates with `efx_common.c` for reset/start/stop/io/common ops, `efx_channels.c` for interrupts and queues, RX/TX common code, NIC-type callbacks, MCDI port/common code, selftests, SR-IOV wrappers, devlink, PTP, filters, ethtool, and Linux PCI/netdev/PM frameworks.

Risks: Probe has many staged resources and must unwind in reverse order. Reset scheduling during probe aborts netdev registration. XDP MTU constraints and program lifetime require RTNL/RCU discipline. Association lists depend on VPD serial matching. PM thaw/resume must re-enable interrupts and hardware in the right order. SR-IOV configure is available only when the NIC type supplies it.

Test signals: PCI probe/remove, probe retry after reset, module load/unload, netdev open/close, PM suspend/resume/freeze/thaw, XDP attach/xmit, device rename, MTD creation failure tolerance, SR-IOV configure dispatch, queue stat reporting, and error unwinds at every probe stage.
