## sources/distributed-fs/ceph-client/arch/arm64/kernel/crash_dump.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/crash_dump.c` supplies the ARM64 kdump hooks
for reading memory from a crashed kernel and reading the crash ELF core header. It supports
kexec-based crash dump collection.

### Important APIs, Types, And Functions
`copy_oldmem_page()` maps one old-memory PFN with `memremap(..., MEMREMAP_WB)`, copies a requested
range into an `iov_iter`, and unmaps it. `elfcorehdr_read()` copies bytes from the crash kernel's
mapped ELF core header using `phys_to_virt()` and advances the caller's physical position pointer.

### Control Flow
`copy_oldmem_page()` exits immediately for zero-length reads, maps the requested PFN for one page,
copies `csize` bytes from `offset` into the iterator, then unmaps before returning the copied byte
count. `elfcorehdr_read()` is a straight physical-to-virtual memcpy from the crash header address.

### State, Persistence, And Dependencies
The file keeps no long-lived state. It depends on crash dump core code, `iov_iter`, memremap,
physical-to-virtual address translation, and ARM64 page sizing. Persistence is the crashed kernel's
RAM image and ELF core metadata, not local filesystem state.

### Integration Points
Generic kdump and `/proc/vmcore` paths call these architecture hooks to extract pages and the ELF
header. The output is eventually consumed by crash analysis tools. For Ceph deployments this matters
operationally because kernel panics in filesystem, networking, or block paths must leave usable
vmcore data.

### Risks
Bad PFNs or mapping failures return short/error results. Incorrect cache attributes could read stale
or corrupted old memory. Offset/size validation is delegated to callers, so callers must not request
cross-page ranges through the one-page mapping. `elfcorehdr_read()` assumes the header is directly
mapped and valid.

### Test Signals
Boot a crash kernel, collect `/proc/vmcore`, validate ELF headers with crash tools, test sparse and
high-memory PFNs, inject mapping failures, and compare copied ranges against known memory patterns.
