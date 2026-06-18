# sources/distributed-fs/ceph-client/drivers/misc/lkdtm/fortify.c

## Purpose
`fortify.c` provides LKDTM tests for fortified string and memory helpers. It intentionally performs runtime-detected overflows against whole objects and struct members to validate `CONFIG_FORTIFY_SOURCE`.

## Important APIs, Types, and Functions
The exported category is `fortify_crashtypes`. Test functions are `lkdtm_FORTIFY_STR_MEMBER()`, `lkdtm_FORTIFY_MEM_OBJECT()`, `lkdtm_FORTIFY_MEM_MEMBER()`, and `lkdtm_FORTIFY_STRSCPY()`. It uses `strscpy()`, `memcpy()`, `strlen()`, `strncmp()`, `strcmp()`, `kmalloc()`, `kstrdup()`, and the LKDTM `pr_expected_config()` macro.

## Control Flow
Each crashtype prepares a destination object whose bounds should be known to fortified helpers, hides the copy length with a volatile variable where needed to avoid compile-time diagnostics, performs a copy that crosses a member or object boundary, and reports failure only if the fortify check did not stop execution. `FORTIFY_STRSCPY` also validates normal `strscpy()` return values before the final overflowing copy.

## State and Persistence
There is no durable state. `fortify_scratch_space` is a volatile global used to keep copied data observable so the compiler does not eliminate the tested operations.

## Dependencies and Integration Points
Integrates with LKDTM through the crashtype category table and relies on kernel fortified string/memory wrappers from `<linux/string.h>`. Expected behavior depends on compiler object-size analysis and `CONFIG_FORTIFY_SOURCE`.

## Risks
The tests are designed to trap or panic. Optimizer changes can accidentally convert runtime checks into build-time failures or remove code unless volatile guards remain. A passing bad copy means a hardening regression.

## Test Signals
Signals include expected fortify reports on member/object overflow, correct `strscpy()` `-E2BIG` and byte-count behavior, preservation of the union-source edge case, and `FAIL` messages only when fortify did not intercept the overflow.
