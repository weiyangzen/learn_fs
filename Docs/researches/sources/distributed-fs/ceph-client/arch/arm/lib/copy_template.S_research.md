# sources/distributed-fs/ceph-client/arch/arm/lib/copy_template.S

Purpose: shared optimized forward-copy assembly template included by `memcpy`, `copy_to_user`, and `copy_from_user`. Including files provide load/store, entry/exit, and fault-abort macros.

Control flow handles small copies, destination alignment, source alignment, 32-byte and larger unrolled loops, prefetching, byte tails, and three unaligned-source shift cases. It also defines abort-preamble/end macros that including uaccess files use to unwind registers. State is entirely caller-provided registers/memory. Dependencies are include-time macros such as `ldr1w`, `str8w`, `enter`, `exit`, `LDR1W_SHIFT`, `STR1W_SHIFT`, and optional `CALGN`/`PLD`. Risks are any include macro mismatch, PC-relative computed branches, and subtle off-by-one tail handling. Test signals include memcpy and uaccess copy suites across all alignments, sizes around 0..128, and faulting user pages.
