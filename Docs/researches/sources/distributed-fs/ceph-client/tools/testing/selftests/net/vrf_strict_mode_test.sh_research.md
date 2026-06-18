# sources/distributed-fs/ceph-client/tools/testing/selftests/net/vrf_strict_mode_test.sh

Purpose: Tests the `net.vrf.strict_mode` sysctl semantics in the init namespace, a test namespace, and mixed namespace interactions. Strict mode prevents multiple VRFs from sharing a table ID.

Important APIs/functions: uses `modprobe vrf`, `/proc/sys/net/vrf/strict_mode`, `ip link add type vrf table`, `ip -d -o link show type vrf`, and `lib.sh` namespace helpers. Functions read/set strict mode, add/delete/configure VRFs, count VRFs by table ID, and log expected success/failure.

Control flow: validates root, `ip`, and strict_mode sysctl presence. `setup()` creates a test namespace. Default `TESTS="init testns mix"`: init tests add/configure VRFs, enable strict mode, expect duplicate table additions to fail, disable strict mode, add duplicates, and expect enabling to fail while duplicates exist. Testns tests do similar inside a namespace. Mix tests verify sysctl state isolation between init and testns and repeated idempotent enable/disable behavior.

State and persistence: mutates init namespace VRFs `vrf100..102` and test namespace VRFs, plus strict_mode sysctls. `cleanup()` deletes created VRFs/netns and resets init strict_mode to 0.

Dependencies and integration: requires root, VRF module/sysctl, iproute2, and `lib.sh`.

Risks: because it touches init namespace VRFs/sysctl, cleanup is important and failure mid-test could leave local VRFs until cleanup trap or manual removal. Exit code 2 from `ip link add` is expected for duplicate-table rejection and is shell/iproute dependent.

Test signals: logs each expected state transition and final pass/fail counts. SKIP returned when root/ip/VRF sysctl support is missing.
