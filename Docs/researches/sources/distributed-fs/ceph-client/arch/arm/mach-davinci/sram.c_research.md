# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/sram.c

Purpose: exposes Davinci SRAM allocation helpers backed by a `gen_pool`.

Important APIs/types/functions: `sram_get_gen_pool()`, exported `sram_alloc()`, exported `sram_free()`, and `sram_init()` core initcall.

Control flow: `sram_init()` locates an `mmio-sram` node, obtains its gen_pool, and caches it. Callers allocate/free SRAM regions and optionally receive DMA/physical addresses.

State and persistence: global `sram_pool` persists after core init; allocations remain until freed by callers.

Dependencies and integration: used by Davinci PM to copy suspend assembly; depends on OF platform SRAM provider and genalloc.

Risks: if SRAM provider probes too late or is absent, suspend allocation fails. Exported allocation helpers need callers to free with the same length.

Test signals: core init log absence of errors, `sram_alloc()` success in PM init, and gen_pool leak checks around users.
