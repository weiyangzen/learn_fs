# sources/distributed-fs/ceph-client/arch/mips/include/asm/setup.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/setup.h

### Purpose
`setup.h` declares MIPS early setup hooks for PROM output, early printk, exception/vector installation, per-CPU trap setup, cache/TLB initialization, relocation, and hardware capability globals.

### Important APIs, Types, And Functions
Exports include `prom_putchar`, `setup_early_printk`, optional `setup_8250_early_printk_port`, `set_handler`, `set_uncached_handler`, `vi_handler_t`, `set_vi_handler`, `set_except_vector`, globals `ebase` and `hwrena`, `per_cpu_trap_init`, `cpu_cache_init`, `tlb_init`, optional `relocate_kernel`, and `plat_post_relocation`.

### Control Flow
Early boot configures console output, installs exception handlers/vectored interrupt handlers, initializes per-CPU traps, cache, and TLB, and optionally relocates the kernel before platform post-relocation callbacks.

### State, Persistence, Dependencies, And Integration
State is exception-vector memory, EBase, HWREna, early console port setup, cache/TLB state, and relocated kernel address state. Dependencies include init/types headers and UAPI setup constants. Integration is with boot code, trap handlers, early printk, CPU bring-up, and relocatable kernel support.

### Risks
Handlers are copied into low-level exception memory; wrong offsets or lengths can brick early boot. Early 8250 setup is a no-op unless configured. Relocation callbacks must run before references to old addresses become invalid.

### Test Signals
Build early printk and relocatable variants, boot with exceptions and interrupts enabled, verify early console output, run TLB/cache init smoke tests, and exercise secondary CPU trap init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/setup.h -->
