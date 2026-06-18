# sources/distributed-fs/ceph-client/drivers/misc/lkdtm/usercopy.c

## Purpose
`usercopy.c` provides LKDTM tests for hardened `copy_to_user()` and `copy_from_user()` checks over slab object bounds, slab usercopy whitelists, stack frame boundaries, kernel text, vmalloc memory, and folio page spans.

## Important APIs, Types, and Functions
Core helpers are `do_usercopy_stack()`, `do_usercopy_slab_size()`, `do_usercopy_slab_whitelist()`, and `do_usercopy_page_span()`. Crashtypes include slab size/whitelist to/from tests, stack frame/beyond tests, `USERCOPY_KERNEL`, `USERCOPY_VMALLOC`, and `USERCOPY_FOLIO`. Init/exit manage `whitelist_cache`.

## Control Flow
Tests allocate user memory with `vm_mmap()`, prepare valid kernel buffers, perform a good copy, then perform a copy that should violate hardened usercopy constraints. Stack tests distinguish current-frame buffers, caller-frame buffers, and addresses beyond the stack. Slab whitelist tests use `kmem_cache_create_usercopy()` with a narrow allowed window. Page-span tests copy from halfway through a page-sized allocation and then attempt an over-span copy.

## State and Persistence
`unconst` and `cache_size` force runtime-sized checks. `whitelist_cache` persists from LKDTM init to exit and defines the permitted usercopy subrange.

## Dependencies and Integration Points
Depends on hardened usercopy, slab, vmalloc, folio allocation, user mappings, task stack helpers, and LKDTM expected-config diagnostics.

## Risks
The bad copies intentionally test fatal hardening paths. Without hardening, stack or heap memory may be corrupted. Compiler optimization is deliberately obscured to keep copies on runtime validation paths.

## Test Signals
Signals include good copies succeeding, bad copies faulting or oopsing, no final `FAIL: bad usercopy not detected`, correct whitelist enforcement, stack-frame rejection, kernel-text copy rejection, and vmalloc/folio page-span detection.
