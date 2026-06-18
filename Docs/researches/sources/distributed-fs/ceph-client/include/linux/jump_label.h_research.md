# sources/distributed-fs/ceph-client/include/linux/jump_label.h

## Purpose
Defines the static key and static branch API used to patch rarely changing branches into near-zero-overhead fast paths. With architecture support, branch sites are recorded in the jump table and patched between NOP and jump instructions at runtime.

## Important APIs, Types, And Functions
Core types include `struct static_key`, `struct jump_entry`, `struct static_key_true`, and `struct static_key_false`. Definition macros include `DEFINE_STATIC_KEY_TRUE/FALSE`, array variants, read-only variants, and config-dependent `DEFINE_STATIC_KEY_MAYBE`. Runtime APIs include `static_branch_likely()`, `static_branch_unlikely()`, `static_branch_enable/disable()`, `static_branch_inc/dec()`, `static_key_count()`, `jump_label_init()`, transform hooks, text reservation checks, and lock guards.

## Control Flow
At compile time, static branch macros emit architecture static-branch sequences and jump table entries. At runtime, enabling or disabling a key updates the atomic count and, when the branch direction changes, patches text through architecture transform hooks. Without `CONFIG_JUMP_LABEL`, the same API falls back to ordinary conditional branches on the atomic count.

## State And Persistence
State is an atomic enabled count plus jump label metadata. For enabled builds, low bits encode initial true/false and linked state in key metadata; jump entries encode branch polarity and init state. State is in-memory and reset at boot/module load.

## Dependencies And Integration Points
Depends on architecture `asm/jump_label.h`, atomics, compiler type checks, static branch generation, module handling, text patching, and optional relative jump entries. It integrates with tracepoints, feature flags, sched/debug controls, and other hot-path conditionals.

## Risks
Branch patching is a machine-wide slow path and should not be driven at high frequency. Direct `struct static_key` usage is deprecated in favor of typed wrappers. Using keys before `jump_label_init()` warns. Incorrect type use intentionally calls `____wrong_branch_error()`.

## Test Signals
Signals include boot-time jump label init, module load/unload with static keys, lockdep/text reservation checks, static branch truth-table tests for initially true/false keys and likely/unlikely forms, fallback builds without jump labels, and stress tests for refcounted enable/disable.
