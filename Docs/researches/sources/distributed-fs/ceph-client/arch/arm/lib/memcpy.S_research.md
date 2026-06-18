# sources/distributed-fs/ceph-client/arch/arm/lib/memcpy.S

Purpose: implements `__memcpy`, weak `memcpy`, and `mmiocpy` using the shared optimized forward-copy template.

Control flow supplies plain kernel load/store macros to `copy_template.S`, which handles alignment, unrolled copies, and tails. It preserves the original destination pointer as the return value. There is no fault handling or overlap support; callers must use `memmove` for overlaps. Dependencies include `copy_template.S`, assembler helpers, and weak symbol resolution. Risks are overlap misuse, alignment path bugs, and template macro regressions affecting multiple copy APIs. Test signals include memcpy tests over lengths and alignments and mmiocpy users on MMIO-like mappings.
