# sources/distributed-fs/ceph-client/drivers/misc/lkdtm/bugs.c

## Purpose
`lkdtm/bugs.c` registers LKDTM crash types that exercise generic logic bugs and hardening features: panics, BUG/WARN, exceptions, lockups, stack exhaustion/corruption/reporting, unaligned access, integer overflow, bounds checking, list hardening, VMAP stack guard pages, SMEP pinning, x86 double fault, and arm64 PAC corruption.

## Important APIs, types, and functions
Initialization uses `lkdtm_bugs_init` for recursion depth. Each `lkdtm_*` function implements a crash type listed in the `crashtypes` array and exported through `bugs_crashtypes`. Notable helpers are `recursive_loop`, hrtimer callbacks for hardirq panic/BUG, stop-machine panic helper, stack canary scanner, SMP call lockup helper, and list corruption simulations.

## Control flow
LKDTM core invokes selected crash functions by name. Many functions intentionally never return or deliberately crash. Others perform a within-bounds operation first, then an out-of-bounds or corrupted operation to verify a mitigation traps. At the end, each crash type is registered with `CRASHTYPE(...)` entries and a category descriptor.

## State and persistence
File-scope state tracks recursion depth, a spinlock intentionally left locked, warning count, panic/BUG wait flags, stack offset/canary observations, and volatile integer values used to prevent compiler optimization. State persists within the module and can affect repeated tests, such as `SPINLOCKUP` requiring two invocations.

## Dependencies and integration points
The file depends on LKDTM core macros, scheduler/task stack APIs, stop_machine, hrtimers, list APIs, slab allocation, uaccess, CPU hotplug read locks, architecture-specific x86 and arm64 helpers, UBSAN/list/stack hardening configs, and mitigation reporting helpers such as `pr_expected_config`.

## Risks
Every crash type is intentionally dangerous. Some tests leave the system hung or unstable if the intended mitigation is absent. Architecture-specific code must be guarded correctly. Compiler optimizations are actively resisted with `volatile`, `noinline`, explicit memory clearing, and special build flags elsewhere.

## Test signals
Expected signals are architecture/config-dependent crashes or `XFAIL`/`FAIL` messages. Coverage should include list hardening, UBSAN bounds, counted-by support, pointer member bounds, stack protector, VMAP stack, lockup detectors, SMEP pinning on x86_64, double fault on x86_32, and PAC corruption on arm64.
