# sources/distributed-fs/ceph-client/arch/arc/include/asm/vmalloc.h

Empty ARC vmalloc hook header. It supplies the include guard expected by generic code but defines no arch-specific vmalloc behavior. Control flow and state are owned by processor.h VMALLOC_* constants and generic vmalloc. Dependencies are include compatibility. Risks are low, but future arch vmalloc constraints could be missed if added elsewhere. Test signals are vmalloc/module/ioremap allocations and compile coverage.
