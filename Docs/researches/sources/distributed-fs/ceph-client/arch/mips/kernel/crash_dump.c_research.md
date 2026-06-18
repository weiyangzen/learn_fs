<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/crash_dump.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/crash_dump.c

### Purpose
`crash_dump.c` implements old-memory page copying for MIPS crash dump readers.

### Important APIs, Types, And Functions
It defines `copy_oldmem_page(struct iov_iter *iter, unsigned long pfn, size_t csize, unsigned long offset)`.

### Control Flow
If `csize` is zero, it returns immediately. Otherwise it maps the old page frame with `kmap_local_pfn()`, copies the requested range to the iterator with `copy_to_iter()`, unmaps, and returns the copied byte count.

### State, Persistence, And Dependencies
There is no persistent state in this file. It depends on highmem local mapping, crash dump infrastructure, and `iov_iter` copying.

### Integration Points
Kdump `/proc/vmcore` or equivalent crash dump readers use this architecture hook to extract pages from the crashed kernel memory image.

### Risks
Bounds are expected to be validated by callers; this function trusts `offset` and `csize` for the mapped page. Partial iterator copies return short counts.

### Test Signals
Kdump vmcore read tests, highmem PFN reads, zero-length reads, offset reads, and short iov iterator behavior validate this path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/crash_dump.c -->
