<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/run_afpackettests -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/run_afpackettests

## Purpose

`run_afpackettests` is a small shell runner for AF_PACKET selftests. It gates on root privileges and executes `psock_fanout`, `psock_tpacket`, and `txring_overwrite` inside network namespaces.

## Important APIs, Types, and Functions

The file is a POSIX shell script using `id -u`, `echo`, and `./in_netns.sh`. It defines the kselftest skip exit code `ksft_skip=4` and accumulates failures in `ret`. `psock_tpacket` is additionally gated on `/proc/kallsyms`.

## Control Flow

After root validation, the script prints a banner for each AF_PACKET executable, runs it through `in_netns.sh`, and emits `[PASS]`, `[FAIL]`, or `[SKIP]`. It exits nonzero if any non-skipped test fails.

## State and Persistence Behavior

State is limited to namespaces created by `in_netns.sh` and any transient packet sockets or links created by the invoked binaries. This wrapper does not persist files or mutate global state except through its children.

## Dependencies and Integration Points

It integrates with compiled AF_PACKET test binaries and the shared namespace wrapper. `psock_tpacket` depends on kallsyms visibility because it inspects kernel symbol-related behavior.

## Risks and Edge Cases

The script assumes it is run from the directory containing `in_netns.sh` and the compiled test binaries. Missing root exits with skip, while missing executables would surface as command failures. The variable `msg` in the root error path is not initialized, so the diagnostic can be sparse.

## Test Signals

Useful signals are the printed per-test PASS/FAIL/SKIP lines and final exit status. A successful run exercises packet fanout, tpacket behavior when kallsyms is available, and TX ring overwrite coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/run_afpackettests -->
