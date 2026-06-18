## sources/distributed-fs/ceph-client/include/linux/cookie.h

Purpose: This header defines a fast monotonically unique-ish cookie generator with per-CPU batching and recursion handling.

Important APIs, types, and functions: `struct pcpu_gen_cookie` stores per-CPU nesting and last value, aligned to 16 bytes. `struct gen_cookie` stores a per-CPU local pointer plus atomic forward and reverse counters. `COOKIE_LOCAL_BATCH` is 4096. `DEFINE_COOKIE(name)` creates per-CPU local storage and a `struct gen_cookie`. `gen_cookie_next(struct gen_cookie *gc)` returns the next cookie.

Control flow: On non-recursive calls, `gen_cookie_next()` increments local nesting, uses the per-CPU cached `last`, and periodically reserves a forward batch from `forward_last` on SMP when the local low bits reach a batch boundary. Recursive calls avoid corrupting the local forward stream by decrementing `reverse_last` atomically and returning negative/reverse-space values. Nesting is decremented before return.

State and persistence: State is in per-CPU `last`/`nesting` and two global atomic64 counters. Cookies persist only as values handed to callers; generator state persists for the lifetime of the static `gen_cookie` object.

Dependencies and integration points: It depends on local atomics, percpu storage, `atomic64_t`, `likely/unlikely`, and `CONFIG_SMP`.

Risks and test signals: Risks include recursion returning values from a different range than callers expect, overflow after long runtimes, per-CPU batch misuse on CPU hotplug, and assuming strict global monotonicity across CPUs. Test signals include concurrent generation stress, recursive generation tests, SMP and UP builds, uniqueness checks, and wraparound reasoning in long-duration tests.
