# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/atomics.c

Purpose: validates classic BPF atomic operations outside arena memory using a light skeleton, covering add, sub, and/or/xor, compare-and-exchange, and exchange.

Important APIs/types/functions: uses `atomics.lskel.h`. Helpers `test_add`, `test_sub`, `test_and`, `test_or`, `test_xor`, `test_cmpxchg`, and `test_xchg` run individual programs directly by FD and inspect `data` and `bss` fields.

Control flow: `test_atomics` opens the light skeleton, sets `keyring_id`, loads it, skips if `.data->skip_tests` reports missing compiler support, sets PID, then dispatches subtests. Each subtest calls `bpf_prog_test_run_opts`, requires zero retval, and checks exact pre/post atomic result fields.

State and persistence behavior: `.data` holds mutable test variables for some atomics while `.bss` stores results and stack-copy observations. State is per skeleton instance and cleaned up at the end.

Dependencies and integration points: depends on BPF atomics compiler support, light skeleton generation, session keyring setting, and `test_progs.h`.

Risks: skipped on environments without `ENABLE_ATOMICS_TESTS` or Clang support. Field-level assertions are tightly coupled to the paired BPF program's global layout.

Test signals: exact value/result assertions for each atomic operation, plus explicit skip when atomics support is unavailable.
