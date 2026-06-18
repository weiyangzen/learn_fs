## sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/interrupt.c

### Purpose
`interrupt.c` implements PS3 interrupt routing between LV1 hypervisor outlets/plugs and Linux IRQs, including event receive ports, system-bus interrupts, IO IRQs, VUART IRQs, SPE IRQs, IPIs, and irqdomain setup.

### Important APIs, Types, And Functions
Key data structures are per-CPU `struct ps3_private` and `struct ps3_bmp`. Important functions include chip callbacks `ps3_chip_mask()`, `ps3_chip_unmask()`, `ps3_chip_eoi()`, setup/teardown helpers for plugs, event ports, SB events, IO, VUART, SPE, IPI registration, `ps3_get_irq()`, `ps3_init_IRQ()`, and `ps3_shutdown_IRQ()`.

### Control Flow
Init creates a no-map irqdomain, configures each CPU's LV1 interrupt state bitmap, and installs `ppc_md.get_irq`. IRQ setup constructs or receives an LV1 outlet, creates a Linux virq equal to the outlet mapping, stores per-CPU chip data, masks it, and connects the outlet to an LV1 plug. `ps3_get_irq()` intersects status and mask bitmaps, prioritizes debug-break IPIs, finds the leading set plug, EOIs IPIs immediately, and returns the plug as the IRQ.

### State, Persistence, And Dependencies
Per-CPU state includes HV status/mask bitmaps, locks, PPE/thread IDs, and IPI masks. LV1 persists outlet/plug/event-port bindings. Dependencies include irqdomain, fast EOI IRQ handling, LV1 interrupt calls, PS3 LPAR address translation, and SMP hard-thread IDs.

### Integration Points
PS3 system-bus, storage notifications, VUART, SPE, and generic interrupt handling use these exported helpers.

### Risks
Only plug values up to 63 are usable by this bitmap simplification. Mask bit polarity is HV-specific. Some destroy paths must avoid operations from interrupt context during kexec. Missing bitmap deconfiguration can leave LV1 writing stale memory.

### Test Signals
Device IRQ delivery, event-port setup/destroy, VUART IRQs, IPIs/debug breaks, CPU shutdown/kexec, and bitmap debug dumps are useful tests.
