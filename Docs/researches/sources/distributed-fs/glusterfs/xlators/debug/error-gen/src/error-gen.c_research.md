# sources/distributed-fs/glusterfs/xlators/debug/error-gen/src/error-gen.c

## Purpose
Implements the GlusterFS `debug/error-gen` translator. It sits in a one-child xlator graph and injects synthetic failures into selected filesystem operations so higher layers, clients, and tests can exercise error handling. It supports a controlled percentage failure mode, a legacy `random-failure` mode, optional fixed errno injection, per-FOP enable lists, short-write simulation for `writev`, statedump reporting, and runtime option reconfiguration.

## Important APIs, types, and functions
`error_no_list[]` maps `GF_FOP_*` operation numbers to realistic errno candidates. `generate_rand_no()` chooses an index in the errno list for a FOP. `conv_errno_to_int()` converts option strings such as `ENOENT`, `EIO`, and the pseudo error `GF_ERROR_SHORT_WRITE` to integer codes, defaulting unknown names to `EAGAIN`. `error_gen()` is the decision engine: it checks `eg_t` state, decides whether the current operation should fail, and returns either a configured errno or a random FOP-specific errno.

The many `error_gen_*` FOP handlers all follow the same pattern: read `egp->enable[GF_FOP_*]`, call `error_gen()` when enabled, unwind the stack with `op_ret = -1` and the chosen `op_errno` on failure, or tail-wind to the child xlator on success. Notable wrappers include `error_gen_writev()`, which recognizes `GF_ERROR_SHORT_WRITE` by duplicating a one-element iovec and halving its length before winding, and lookup/create/directory wrappers that must supply the right strict-unwind argument shape.

Lifecycle and integration functions are `init()`, `reconfigure()`, `fini()`, `mem_acct_init()`, and `error_gen_priv_dump()`. The exported `fops`, `dumpops`, `cbks`, `options`, and `xlator_api` tables register this translator as identifier `error-gen`, category `GF_TECH_PREVIEW`.

## Control flow
Initialization validates that there is exactly one subvolume, allocates `eg_t`, initializes its lock, parses `error-no`, `failure`, `enable`/`error-fops`, and `random-failure`, assigns `this->private`, and seeds `rand()` with `gf_time()`.

For each intercepted FOP, the fast path is: start in the `error_gen_*` wrapper, check whether that FOP is enabled, call `error_gen()` if so, and either return an immediate synthetic error through `STACK_UNWIND_STRICT()` or pass the request to `FIRST_CHILD(this)` with `STACK_WIND_TAIL()`. Normal controlled-probability mode compares `rand() % FAILURE_GRANULARITY` against `egp->failure_iter_no`, which is a numerator derived from the configured percentage. Legacy `random-failure` mode locks `eg_t`, increments `op_count`, injects when the count reaches `failure_iter_no`, then resets the count and chooses the next interval as `3 + rand() % GF_UNIVERSAL_ANSWER`.

Reconfiguration repeats option parsing against the existing private object. It updates the fixed errno, random-failure flag, enabled FOP bitmap, and failure numerator without replacing the xlator instance.

## State and persistence behavior
State is process-local only. `eg_t` stores enabled FOP bits, operation count, failure numerator or legacy interval, optional fixed errno, random-failure flag, and a lock. There is no durable persistence; option changes come from the volfile/management plane and live in memory. Statedump exposes `op_count`, `failure_iter_no`, `error_no_int`, and `random_failure` under `xlator.debug.error-gen.<name>.priv`.

The only protected mutable state in `error_gen()` is the legacy random-failure counter path. In normal probability mode, reads of `failure_iter_no`, `error_no_int`, and `enable[]` are lockless, so reconfiguration can race with active FOPs in the usual xlator-option style.

## Dependencies and integration points
Depends on GlusterFS xlator APIs, strict unwind/wind macros, FOP enums and names, memory accounting, statedump, locks, `gf_fop_int()`, `gf_time()`, and the `error-gen.h`/`error-gen-mem-types.h` declarations. It integrates as a pass-through debug xlator above exactly one child translator and relies on the child FOP vector for all non-injected work.

## Risks and test signals
Risk areas include the use of process-global `rand()`/`srand()` in multi-threaded graphs, lockless normal-mode option reads during reconfigure, realistic errno tables that may miss newer FOPs, unknown `error-no` values silently becoming `EAGAIN`, and strict-unwind argument mismatches when FOP signatures evolve. `error_gen_writev()` frees the shortened iovec immediately after `STACK_WIND_TAIL()`, so tests should verify that the downstream stack does not retain that temporary vector beyond the call path.

Useful tests include configuring each supported errno, enabling a subset of FOPs, forcing 0 percent and 100 percent failure, exercising legacy `random-failure`, validating short-write behavior on multi-vector writes, reconfiguring while load is active, confirming all disabled FOPs pass through, and checking statedump output after injected operations.
