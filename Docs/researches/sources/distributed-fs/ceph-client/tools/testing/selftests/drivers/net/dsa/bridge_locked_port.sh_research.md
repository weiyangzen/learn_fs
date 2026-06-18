# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/dsa/bridge_locked_port.sh

Purpose: DSA wrapper for the shared `bridge_locked_port.sh` forwarding selftest.

Important APIs/functions: Resolves `libdir`, derives `testname`, sources `forwarding.config`, changes directory to `../../../net/forwarding/`, and sources the matching forwarding script with passed arguments.

Control flow: No local test logic beyond selecting config and delegating to the shared forwarding test.

State and persistence: Runtime state is created by the delegated forwarding script using DSA topology settings from `forwarding.config`.

Dependencies and integration points: Requires the forwarding script of the same basename and DSA config. Integrates DSA hardware/switch topology with generic locked-port bridge validation.

Risks and test signals: Failures may originate in shared bridge locked-port logic, DSA hardware behavior, or local config resolution.
