
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-fadump.h

Purpose: defines OPAL FADump metadata and HDAT CPU register parsing helpers shared by OPAL FADump and OPAL core export code.

Important APIs/types: `OPAL_FADUMP_MIN_BOOT_MEM` enforces a minimum boot memory boundary. `struct opal_fadump_mem_struct` is the kernel metadata structure registered with firmware and later consumed by a capture kernel. `struct hdat_fadump_thread_hdr` and `struct hdat_fadump_reg_entry` describe firmware-provided CPU state data. Inline helpers `opal_fadump_set_regval_regnum()` and `opal_fadump_read_regs()` translate HDAT register entries into `struct pt_regs`.

Control flow: `opal_fadump_read_regs()` zeroes a `pt_regs`, walks fixed-size register entries, optionally endian-converts register values, and delegates register assignment. GPR entries fill `gpr[0..31]`; selected SPR IDs fill CTR, LR, XER, DAR, DSISR, NIP, MSR, and CCR.

State and persistence: the header describes persistent reserved-memory metadata but does not allocate or write it by itself.

Dependencies and integration points: depends on OPAL MPIPL region structures, FADump limits, `struct pt_regs`, and SPR number definitions. Used by `opal-fadump.c` and `opal-core.c`.

Risks: only known registers are mapped; unknown firmware entries are ignored. The `cpu_endian` parameter is essential because different consumers pass data with different endian expectations. Metadata layout is packed and firmware ABI-sensitive.

Test signals: vmcore and OPAL core register notes showing correct NIP/MSR/GPRs, mixed GPR/SPR HDAT entries, inactive core skipping by callers, and compatibility with newer metadata versions.
