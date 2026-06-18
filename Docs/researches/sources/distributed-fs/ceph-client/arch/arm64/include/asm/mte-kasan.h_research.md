# sources/distributed-fs/ceph-client/arch/arm64/include/asm/mte-kasan.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mte-kasan.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/mte-kasan.h

### Purpose
`mte-kasan.h` implements low-level ARM64 MTE primitives used by hardware-tag KASAN: tag check override control, random tag generation, tag load/store, range tagging, and kernel MTE modes.

### Important APIs, Types, And Functions
It exports `system_uses_mte_async_or_asymm_mode()`, `mte_disable_tco()`, `mte_enable_tco()`, async TCO helpers, `mte_get_ptr_tag()`, `mte_get_mem_tag()`, `mte_get_random_tag()`, `mte_set_mem_tag_range()`, `SET_MEMTAG_RANGE`, and kernel mode functions `mte_enable_kernel_sync/async/asymm/store_only()`, with non-MTE stubs.

### Control Flow
KASAN and MTE setup enable kernel tag-check modes, then allocation/free/page operations call inline assembly helpers to set or read allocation tags over memory ranges.

### State, Persistence, And Dependencies
State is CPU MTE control registers, tags stored in memory tag storage, and the static key `mte_async_or_asymm_mode`. It depends on `asm/compiler.h`, `asm/cputype.h`, `asm/mte-def.h`, and MTE CPU support.

### Integration Points
Used by hardware-tag KASAN, allocator tagging, page clearing, and kernel entry/exit tag-check control.

### Risks
Tag range loops must align and size ranges correctly. TCO toggling affects whether faults are detected. Async/asymm modes change fault timing and diagnostics.

### Test Signals
Run KASAN HW_TAGS tests, MTE sync/async/asymm boot modes, allocator fault injection, and tag range stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mte-kasan.h -->
