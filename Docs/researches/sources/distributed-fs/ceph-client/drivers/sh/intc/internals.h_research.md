# sources/distributed-fs/ceph-client/drivers/sh/intc/internals.h

Purpose: private ABI for the SH INTC implementation. It defines encoded-handle macros, internal descriptor structures, SMP register-bank helpers, and cross-object prototypes.

Important types and macros: `_INTC_MK` packs function, mode, register indexes, field width, and shift into one word; `_INTC_*` macros decode it. `INTC_REG` and `SMP_NR` resolve per-CPU register addresses when SMP metadata is present. `struct intc_desc_int` holds controller runtime state including device, radix tree, raw lock, register arrays, priority/sense lists, windows, irqdomain, irq chip, and suspend flag. `struct intc_map_entry` and `struct intc_subgroup_entry` back enum-to-IRQ and subgroup mappings.

Control flow support: all INTC `.c` files include this header to share helper prototypes and optional feature stubs. `get_intc_desc` recovers controller state from the installed `irq_chip`.

State and dependencies: no standalone runtime state, but it shapes all internal state. Dependencies include IRQ core, irqdomain, radix tree, device model, and `linux/sh_intc.h`. Risks are bitfield width limits, 8-bit register index limits, container lookup assuming chip object embedding, and ABI fragility across all INTC objects. Test signals are compile/link across SMP and non-SMP, optional feature builds, and successful handle decoding under all register widths.
