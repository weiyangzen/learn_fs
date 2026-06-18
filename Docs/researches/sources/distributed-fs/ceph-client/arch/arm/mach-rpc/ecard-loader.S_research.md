# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/ecard-loader.S

Purpose: assembly helpers that execute expansion-card loader bytecode in a RISC OS-like environment.

Important APIs/types/functions: provides `ecard_loader_reset()` and `ecard_loader_read()` called from `ecard.c`.

Control flow: the helpers set up expected register state, call into card-supplied loader code, and return reset/read results to the kernel ecard daemon.

State and persistence: mutates CPU registers and executes untrusted firmware-provided code; no kernel data persistence except returned values.

Dependencies and integration points: called only from the `kecardd` context after page-table mappings are prepared by `ecard_init_pgtables()`.

Risks: this deliberately trusts expansion-card loader code and runs it with kernel privilege. Calling convention and mapped virtual addresses must match old RISC OS assumptions.

Test signals: card chunk reads that require loaders, reset-on-shutdown behavior, and regression tests with cards on the quirk/loader paths.
