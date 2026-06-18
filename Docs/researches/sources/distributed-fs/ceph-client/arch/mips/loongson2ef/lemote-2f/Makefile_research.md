<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/Makefile

Purpose: Builds Lemote Loongson2F family board support.

Important APIs/types/functions: Always includes `clock.o`, `machtype.o`, `irq.o`, `reset.o`, `dma.o`, and `ec_kb3310b.o`; conditionally includes `pm.o` for `CONFIG_SUSPEND`.

Control flow: Build-time object selection wires the common Loongson2EF hooks to Lemote 2F implementations.

State and persistence: No runtime state; controls compilation.

Dependencies and integration: Supplies machine-type, EC, reset, DMA, IRQ, and optional suspend support.

Risks: Suspend hooks are absent unless `CONFIG_SUSPEND` is enabled.

Test signals: Lemote 2F builds should resolve EC and board hook symbols; suspend builds should include `pm.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/Makefile -->
