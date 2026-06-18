# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/asm-prototypes.h

This header exposes C prototypes for assembly helpers that need modversion or C-visible declarations. It includes spinlock, checksum, console, page, string, uaccess, and generic asm prototypes, then declares Alpha division/remainder helpers and `__udiv_qrnnd`.

The important APIs are `__divl`, `__reml`, `__divq`, `__remq`, unsigned variants, and `__udiv_qrnnd`. There is no runtime control flow in the header; it coordinates symbol typing between assembly implementations and C/generated metadata.

Risks are missing prototypes causing modversion mismatches or incorrect calling conventions for compiler-emitted division calls. Test signals are successful Alpha allmodconfig/module builds and no unresolved arithmetic helper symbols.
