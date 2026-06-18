# sources/distributed-fs/ceph-client/arch/arm64/include/asm/mte-def.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mte-def.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/mte-def.h

### Purpose
`mte-def.h` defines common ARM64 Memory Tagging Extension constants used by MTE, KASAN, and KVM tag code.

### Important APIs, Types, And Functions
It exports constants such as `MTE_GRANULE_SIZE`, `MTE_GRANULE_MASK`, `MTE_TAG_SHIFT`, `MTE_TAG_SIZE`, `MTE_TAG_MASK`, `MTE_PAGE_TAG_STORAGE`, and `__MTE_PREAMBLE`.

### Control Flow
There is no runtime control flow. Inline asm and tag-management helpers include these constants to size granules, masks, and tag-storage buffers.

### State, Persistence, And Dependencies
No state is owned. It depends on generic bit macros and ARM64 assembler support for the memtag extension.

### Integration Points
Used by `mte.h`, `mte-kasan.h`, KVM MTE, and memory-management code handling tagged pages.

### Risks
Wrong granule or tag size breaks tag storage layout and address tag extraction. Assembler preamble mismatch breaks inline MTE instructions.

### Test Signals
Build MTE/KASAN configs; run MTE userspace, KASAN HW tags, and KVM MTE tag-storage tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mte-def.h -->
