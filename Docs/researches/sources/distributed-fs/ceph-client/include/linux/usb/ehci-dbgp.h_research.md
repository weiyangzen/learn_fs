<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ehci-dbgp.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/ehci-dbgp.h

Purpose: declares EHCI debug-port register layout and optional early-printk/Xen integration hooks.

Important APIs and types: `struct ehci_dbg_port` maps debug-port control, PID, data, and address registers. Bit macros describe ownership, enable/done/in-use/error/go/out/length fields, error codes, PID packing, and endpoint address packing. Optional APIs include `early_dbgp_init`, `early_dbgp_console`, `dbgp_reset_prep()`, `dbgp_external_startup()`, and Xen-specific reset/startup hooks with stubs when configs are disabled.

Control flow: early console/debug code initializes the EHCI debug port, takes ownership, sends/receives debug packets through the register block, and EHCI host reset/startup paths call debug prep hooks so debug-port use survives controller initialization where possible.

State and persistence: hardware debug-port registers hold transient transfer state. Early console state is owned by the debug driver; the header stores none.

Dependencies and integration points: depends on console/types, `struct usb_hcd`, EHCI host driver reset paths, `CONFIG_EARLY_PRINTK_DBGP`, and Xen dom0 hooks.

Risks and test signals: risks include conflicting ownership with EHCI driver, early-boot MMIO access before mapping is stable, wrong non-config stubs, and Xen handoff differences. Test early printk over EHCI debug devices, EHCI reset with debug enabled, Xen dom0 paths, and builds with configs disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ehci-dbgp.h -->
