# sources/distributed-fs/ceph-client/arch/x86/kernel/crash_dump_32.c

## Purpose
Implements 32-bit kdump old-memory page copying with PAE safety checks.

## Important APIs, Types, And Functions
`is_crashed_pfn_valid()` rejects PFNs that cannot round-trip through a PTE on non-PAE kernels. `copy_oldmem_page()` maps a crashed-kernel PFN with `kmap_local_pfn()`, copies data to an `iov_iter`, and unmaps it.

## Control Flow
Zero-length copies return immediately. Non-PAE kernels validate the PFN to avoid address truncation when a non-PAE dump kernel reads memory from a PAE crashed kernel. Valid pages are locally mapped, copied from `offset` for `csize`, then unmapped.

## State, Persistence, And Dependencies
No persistent state is introduced. It depends on highmem local PFN mappings, `iov_iter`, PTE encoding, and crash dump read paths.

## Integration Points
Used by `/proc/vmcore` and crash dump infrastructure to read physical memory from the previous kernel on 32-bit x86.

## Risks
Invalid PFNs must be rejected to avoid aliasing high physical memory into low addresses. The caller must supply sane offsets and sizes within a page.

## Test Signals
32-bit kdump reads should return exact page data; non-PAE dump kernels should reject unrepresentable PFNs with `-EFAULT`; zero-size reads should return 0.
