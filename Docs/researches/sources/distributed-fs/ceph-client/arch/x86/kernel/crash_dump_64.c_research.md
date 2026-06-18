# sources/distributed-fs/ceph-client/arch/x86/kernel/crash_dump_64.c

## Purpose
Implements 64-bit kdump old-memory and elfcorehdr reads, including encrypted-memory mappings for SME/confidential guests.

## Important APIs, Types, And Functions
`__copy_oldmem_page()` maps a physical page with either `ioremap_cache()` or `ioremap_encrypted()`. `copy_oldmem_page()` reads normal old memory. `copy_oldmem_page_encrypted()` reads encrypted old memory. `elfcorehdr_read()` reads through `read_from_oldmem()` using guest memory encryption state.

## Control Flow
Zero-length copies return 0. The helper maps the PFN as a full page, copies from `offset` to the iterator, unmaps, and returns copied bytes or `-ENOMEM` on map failure. `elfcorehdr_read()` wraps a kernel buffer in a `kvec` iterator and chooses encrypted reads when `CC_ATTR_GUEST_MEM_ENCRYPT` is active.

## State, Persistence, And Dependencies
No persistent state is introduced. It depends on ioremap attributes, confidential-computing platform flags, `iov_iter`, and crash dump old-memory helpers.

## Integration Points
Supports `/proc/vmcore`, crash ELF header reading, and encrypted-memory dump capture on x86_64.

## Risks
Using the wrong encryption attribute produces unreadable or corrupt dumps. Mapping failures must propagate. Offsets and sizes are assumed page-bounded by callers.

## Test Signals
kdump should read vmcore pages and elfcorehdr correctly on normal, SME, and guest-encrypted systems, with encrypted and unencrypted paths producing expected data.
