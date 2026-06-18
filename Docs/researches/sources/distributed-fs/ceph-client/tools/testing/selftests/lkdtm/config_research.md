# sources/distributed-fs/ceph-client/tools/testing/selftests/lkdtm/config

Purpose: kernel configuration fragment for LKDTM hardening/regression selftests.

Important APIs/types/functions: requests `CONFIG_LKDTM`, debug list checks, slab freelist hardening, fortify, kernel stack erase/randomization, hardened usercopy, init-on-free/alloc, UBSAN bounds, strong stack protector, and SLUB debug.

Control flow: none; consumed by kselftest/kconfig tooling.

State and persistence: no runtime state. It influences kernel build-time and boot-time hardening features that LKDTM probes.

Dependencies and integration points: ties the `lkdtm` tests to kernel debug/hardening options and `/sys/kernel/debug/provoke-crash`.

Risks: enabling these options can change performance and debugging behavior; missing options often cause runtime skips rather than failures.

Test signals: a kernel matching this fragment should expose the trigger and expected hardening behaviors used by `run.sh` and `stack-entropy.sh`.
