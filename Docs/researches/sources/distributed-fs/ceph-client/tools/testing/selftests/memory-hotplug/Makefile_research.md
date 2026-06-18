# sources/distributed-fs/ceph-client/tools/testing/selftests/memory-hotplug/Makefile

Purpose: kselftest Makefile for memory hotplug shell testing.

Important APIs/types/functions: empty `all`, includes `../lib.mk`, declares `TEST_PROGS := mem-on-off-test.sh`, and provides `run_full_test` wrapper running `mem-on-off-test.sh -r 10`.

Control flow: runtime is delegated to the shell script; `run_full_test` prints pass/fail based on script status.

State and persistence: none at build level.

Dependencies and integration points: kselftest `lib.mk` and the hotplug script.

Risks: `run_full_test` converts result to printed text rather than kselftest TAP.

Test signals: script registered as a kselftest program.
