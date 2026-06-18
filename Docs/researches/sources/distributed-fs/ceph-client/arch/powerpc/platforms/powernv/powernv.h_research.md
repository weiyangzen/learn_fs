## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/powernv.h

### Purpose
`powernv.h` is a local platform header for PowerNV internals that need to be shared across architecture files without becoming general public API.

### Important APIs, Types, And Functions
It includes `<asm/powernv.h>` and declares or stubs `pnv_smp_init()`, `pnv_platform_error_reboot()`, `pnv_pci_init()`, `pnv_pci_shutdown()`, `pnv_get_supported_cpuidle_states()`, `pnv_lpc_init()`, `opal_handle_events()`, `opal_have_pending_events()`, `opal_event_shutdown()`, `cpu_core_split_required()`, memcons helpers, and `pnv_rng_init()`.

### Control Flow
The header has no runtime flow. Conditional compilation provides no-op PCI/SMP functions when those subsystems are disabled, allowing common platform code to call them unconditionally.

### State, Persistence, And Dependencies
It declares access to state owned by other files, such as OPAL event state, PCI controller state, and memcons pointers. Dependencies include PowerPC platform types, `struct pt_regs`, `struct device_node`, and `struct memcons` forward declarations.

### Integration Points
`opal-irqchip.c`, `opal-msglog.c`, and other PowerNV platform files include this header for cross-file prototypes. The declarations connect platform init/shutdown, OPAL event polling, PCI setup, LPC setup, and memory console helpers.

### Risks
Because this is an internal header, prototype drift can silently affect multiple architecture files at once. Stubbed functions must preserve call-site expectations when optional configs are disabled.

### Test Signals
Build matrix coverage with and without `CONFIG_SMP` and `CONFIG_PCI` is the main signal. Runtime checks should confirm callers tolerate stubbed PCI/SMP paths and that OPAL event/memcons declarations match their implementations.
