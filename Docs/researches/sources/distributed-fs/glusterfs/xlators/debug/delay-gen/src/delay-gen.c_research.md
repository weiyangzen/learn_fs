# sources/distributed-fs/glusterfs/xlators/debug/delay-gen/src/delay-gen.c

## Purpose
This debug translator probabilistically delays selected FOPs before forwarding them to the default child implementation. It is meant for timing, latency, and race-condition testing.

## Important APIs, Types, And Functions
`delay_gen()` checks whether a FOP is enabled and whether the configured probability hits; if so it sleeps for `delay_duration` microseconds using `gf_nanosleep()`. Macro `DG_FOP()` wraps each FOP implementation by calling `delay_gen()` and then `default_<fop>()`. The file defines wrappers for a broad set of FOPs including lookup, read, write, locks, xattrs, directory operations, allocation, discard, seek, lease, active-lock migration, and IPC. Lifecycle functions are `init()`, `fini()`, `mem_acct_init()`, `reconfigure()`, and `notify()`.

`delay_gen_parse_fill_fops()` parses the `enable` option. An empty string enables all FOPs from `GF_FOP_NULL + 1` to `GF_FOP_MAXVALUE - 1`; otherwise it treats the string as comma-separated FOP names and maps them through `gf_fop_int()`. `delay_gen_set_delay_ppm()` converts a user percentage into a threshold over `DELAY_GRANULARITY`.

## Control Flow
Initialization validates exactly one child translator, allocates `dg_t`, reads `delay-percentage`, `enable`, and `delay-duration`, computes the probability threshold, populates the enabled FOP bitmap, and stores `this->private`. Each FOP wrapper is synchronous: it may sleep in the caller's execution path, then forwards to the default stack implementation. `notify()` simply delegates to `default_notify()`. `reconfigure()` is a stub and does not update settings at runtime.

## State And Persistence Behavior
Runtime state is only `dg_t`: `delay_ppm`, `delay_duration`, and the `enable[]` bitmap. There is no persistent state and no per-inode/fd context. `rand()` is used without local seeding or locking in this file.

## Dependencies And Integration Points
The translator depends on GlusterFS defaults, FOP name mapping, option parsing, memory accounting, and the default pass-through xlator helpers. It is registered as a debug xlator with identifier `delay-gen` and tech-preview category.

## Risks
Because delay is injected synchronously before forwarding, it can block event or worker threads and amplify timing-sensitive deadlocks. `reconfigure()` doing nothing may surprise users who set options dynamically. The use of `rand()` gives process-global pseudo-random behavior and may not be thread-ideal. The wrapper list must track FOP table evolution or new FOPs will not be delayed.

## Test Signals
Tests should verify one-child validation, option parsing for empty and named FOP lists, invalid FOP names, probability extremes (`0%` and `100%`), approximate delay duration, pass-through correctness for representative FOPs, and that dynamic reconfigure currently has no effect.
