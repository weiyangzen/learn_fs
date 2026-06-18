# sources/distributed-fs/ceph-client/include/linux/kasan-enabled.h

## Purpose
Defines the runtime `kasan_enabled()` interface for KASAN modes that may be controlled after boot or by hardware tag state.

## Important APIs, Types, And Functions
When `CONFIG_ARCH_DEFER_KASAN` or `CONFIG_KASAN_HW_TAGS` is set, the header declares `kasan_flag_enabled` as a static key and implements `kasan_enabled()` through `static_branch_likely()`, plus `kasan_enable()` to turn it on. Other builds return `IS_ENABLED(CONFIG_KASAN)` and make `kasan_enable()` a no-op. `kasan_hw_tags_enabled()` returns the runtime KASAN state only for HW tags.

## Control Flow
The runtime-controlled path uses a static branch to keep checks cheap once the mode is known. The compile-time path folds enabled/disabled state at build time.

## State And Persistence
Runtime state is the static key `kasan_flag_enabled`. It is in-memory boot state, not persistent.

## Dependencies And Integration Points
Depends on `linux/static_key.h` and the jump label/static branch subsystem. It gates most public wrappers in `kasan.h`.

## Risks
Calling KASAN hooks before enabling deferred KASAN can skip checks. Static key initialization ordering matters. Non-HW tag code must not infer hardware tag availability from generic `kasan_enabled()`.

## Test Signals
Test deferred and early-enable architectures, HW tag runtime toggling, disabled builds, static key initialization ordering, and wrappers in `kasan.h` that should call runtime hooks only when enabled.
