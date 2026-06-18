# sources/distributed-fs/ceph-client/mm/usercopy.c

## Purpose

`usercopy.c` implements the hardened usercopy object-size validator used by `copy_to_user()` and `copy_from_user()` paths. It rejects kernel text exposure, bogus addresses, invalid stack ranges, and heap/slab/vmalloc ranges that exceed allocator-owned objects or explicit slab usercopy whitelists. It also wires the runtime `hardened_usercopy=` boot option into the `validate_usercopy_range` static key.

## Important APIs, Types, and Functions

- `DEFINE_STATIC_KEY_MAYBE_RO(CONFIG_HARDENED_USERCOPY_DEFAULT_ON, validate_usercopy_range)` exports the static branch controlling whether call sites perform object validation.
- `__check_object_size(const void *ptr, unsigned long n, bool to_user)` is the exported validator. It is the public integration point for usercopy range checks.
- `usercopy_abort(...)` logs the attempted exposure or overwrite and ends execution with `BUG()`.
- `check_stack_object()` classifies a range as `NOT_STACK`, `GOOD_FRAME`, `GOOD_STACK`, or `BAD_STACK` using `task_stack_page(current)`, `THREAD_SIZE`, `arch_within_stack_frames()`, and optionally `current_stack_pointer`.
- `check_heap_object()` validates kmap, vmalloc, slab, and compound-page allocations. Slab allocations are delegated to `__check_heap_object()`.
- `check_kernel_text_object()` rejects overlap with `_stext.._etext` and the linear alias returned by `lm_alias()`.
- `parse_hardened_usercopy()` and `set_hardened_usercopy()` parse the boot parameter and enable/disable the static branch at `late_initcall`.

## Control Flow

`__check_object_size()` first returns immediately for zero-length copies. It then rejects wrapped or null/zero-size addresses via `check_bogus_address()`. Stack ranges are checked before heap ranges: a valid stack frame/range returns successfully, while a partial or below-current-stack object aborts. Non-stack ranges proceed to heap validation, where kmap objects must stay in one page, vmalloc objects must stay inside a live vmap area when page faults are enabled, slab objects are checked against allocator metadata, and compound page allocations must stay inside the compound allocation. Finally, the range is checked against kernel text and linear text aliases.

## State and Persistence

There is no durable per-object state. Runtime state consists of the read-mostly static key `validate_usercopy_range` and the `__initdata` `enable_checks` boot-parameter value. The rest of the logic derives state from current task stack metadata, vmap metadata, slab/page metadata, and linker section symbols.

## Dependencies and Integration Points

This file depends on scheduler/task stack APIs, architecture stack-frame helpers, vmalloc/vmap lookup, slab internals through `slab.h`, highmem/kmap predicates, linker section symbols, `lm_alias()`, static keys, and boot parameter parsing. Its exported symbols are consumed by hardened usercopy call sites in architecture and generic uaccess code.

## Risks

- False negatives are possible for non-compound page allocations because the allocator cannot reliably know whether a multi-page non-compound allocation is being crossed.
- vmalloc checking is skipped while page faults are disabled, so callers must not assume vmalloc bounds are always enforced in atomic contexts.
- `usercopy_abort()` uses `BUG()`, so any false positive is fatal.
- Correctness depends on architecture implementations of stack frame introspection and linear text aliasing.

## Test Signals

Useful signals include hardened usercopy LKDTM tests, slab usercopy whitelist tests, stack copy boundary tests, vmalloc/kmap range tests, booting with `hardened_usercopy=on/off`, and observing that invalid copies produce the expected emergency log and BUG while valid stack/slab/vmalloc copies proceed.
