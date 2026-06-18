<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/kasan-tags.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/kasan-tags.h

## Purpose
`kasan-tags.h` supplies memory-tag constants shared with kernel-style KASAN code.

## APIs And Flow
It defines `KASAN_TAG_KERNEL`, `KASAN_TAG_INVALID`, `KASAN_TAG_MAX`, and `KASAN_TAG_MIN`. There are no functions or branches.

## State, Dependencies, Risks, Tests
There is no state and no dependencies beyond integer macro use. Integration is through allocation and pointer-tagging code that wants the same tag vocabulary as the kernel. Risks are value drift from kernel KASAN definitions and misuse on tools builds that do not actually implement tag checking. Test signals are compile-time assertions against the kernel copy and builds of allocators that include KASAN flag handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/kasan-tags.h -->
