<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netns-sysctl.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netns-sysctl.sh

## Purpose
This test verifies selected network core buffer sysctls are visible in network namespaces, reflect the init namespace value, and are read-only from inside non-init netns.

## Important APIs, Types, And Functions
It uses `lib.sh`, `setup_ns`, `cleanup_ns`, `sysctl`, `/proc/sys/net/core`, `ip netns exec`, and local `cleanup()`/`fail()` helpers. The sysctls under test are `rmem_default`, `rmem_max`, `wmem_default`, and `wmem_max`.

## Control Flow
The script creates one test namespace. For each sysctl, it checks write permission in the init namespace, writes value `300000`, checks that the test namespace reads the same value, and verifies the file is not writable from inside the test namespace.

## State, Persistence, And Dependencies
State includes one namespace and host-level sysctl values modified to `300000`; the script does not save/restore original values. It depends on procfs sysctl exposure, namespace execution, and root privileges.

## Integration Points
This is a net namespace/sysctl regression test for shared read-only core memory settings. It validates the expected relationship between init-net writable knobs and per-netns read visibility.

## Risks
The lack of restoration can affect later tests that assume default socket buffer sysctl values. The `-e` shell mode exits immediately on unexpected command failure, so diagnostics may be limited outside explicit `fail()` calls.

## Test Signals
Success prints `Test passed OK`. Failures identify missing init-net write permission, failed write, namespace value mismatch, or unexpected writeability inside the namespace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netns-sysctl.sh -->
