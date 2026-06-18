# sources/distributed-fs/ceph-client/include/linux/kasan-checks.h

## Purpose
Provides explicit KASAN access-check helpers for code that needs to validate memory accesses outside normal compiler instrumentation.

## Important APIs, Types, And Functions
The low-level always-available helpers are `__kasan_check_read()` and `__kasan_check_write()` when generic or software-tag KASAN is enabled, otherwise no-op true-returning stubs. Header-safe helpers are `kasan_check_read()` and `kasan_check_write()`, which call the low-level functions only when the current compilation unit has `__SANITIZE_ADDRESS__`.

## Control Flow
Compile-time config and compiler instrumentation decide whether checks call KASAN runtime or fold to `true`. Hardware tag-based KASAN is intentionally excluded here; callers that need byte validation across modes should use `kasan_check_byte()` from `kasan.h`.

## State And Persistence
No local state is stored. Checks query KASAN runtime/shadow state when active.

## Dependencies And Integration Points
Depends on `linux/types.h` and KASAN runtime implementation. Integrates with low-level accessors and code compiled with selective sanitizer instrumentation.

## Risks
The header warns not to use `__kasan_check_*` in headers because it bypasses compilation-unit instrumentation selection. Using these helpers for hardware tag KASAN expectations is wrong because they optimize away in that mode.

## Test Signals
Signals include generic and software-tag KASAN reports for explicit checks, no-op behavior when disabled, compilation units with and without `__SANITIZE_ADDRESS__`, and coverage that hardware-tag checks use `kasan_check_byte()` instead.
