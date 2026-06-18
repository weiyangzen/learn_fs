<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic_msgr.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic_msgr.c

Purpose: Provides a platform driver and exported API for Freescale MPIC message registers used as inter-device or inter-core message sources.

Important APIs/types/functions: Exports `mpic_msgr_get()`, `mpic_msgr_put()`, `mpic_msgr_enable()`, and `mpic_msgr_disable()`. Driver entry points include `mpic_msgr_probe()` and `mpic_msgr_init()`. Internal helpers count alias-defined blocks and derive block ordering.

Control flow: On first probe the driver counts `mpic-msgr-blockN` aliases to size the global register-pointer array. Each block maps its register resource, resolves its alias index, reads `mpic-msgr-receive-mask`, allocates four `struct mpic_msgr` objects, parses IRQs for receive-capable registers, disables each register, and stores it in the global array. Clients reserve a register with `mpic_msgr_get()`, enable/disable through MER bits, and release via `mpic_msgr_put()`.

State and persistence: Persistent state includes global `mpic_msgrs`, `mpic_msgr_count`, global allocation lock, per-message-register MMIO base/MER pointer, IRQ number, in-use flag, register number, and per-register lock.

Dependencies and integration points: Depends on OF aliases, platform devices, MPIC message-register bindings, irq parsing, big-endian MMIO, and `asm/mpic_msgr.h` client structures.

Risks: `mpic_msgr_get()` initializes `msgr` to `ERR_PTR(-EBUSY)` but unconditionally assigns `mpic_msgrs[reg_num]`; if a sparse slot was never probed, callers can receive NULL. Probe failures after partial allocation do not clean up earlier registers. Alias ordering is mandatory.

Test signals: Device-tree alias order tests, receive-mask/IRQ parsing, concurrent get/put, MER bit enable/disable verification, sparse/missing alias behavior, and client interrupt delivery.

Source read size: 285 lines, 6943 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic_msgr.c -->
