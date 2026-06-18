# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bridge_stp_mode.sh

Purpose: Tests bridge `stp_mode` netlink attribute behavior for user, kernel, and auto STP modes.

Important APIs/types/functions: Uses `ip link ... type bridge stp_mode/stp_state`, JSON `ip -d -j link show`, `jq`, kselftest `lib.sh` defer cleanup, and test functions listed in `ALL_TESTS`.

Control flow: After verifying iproute2 advertises `stp_mode`, setup creates a namespace. Tests check default `auto`, setting user/kernel/auto modes, rejecting mode changes while STP is active, allowing idempotent active-mode set and simultaneous disable+mode change, user mode in netns producing `stp_state=2`, kernel mode producing `stp_state=1`, auto fallback in netns, atomic mode+state setting, and mode persistence across disable/enable cycles.

State and persistence behavior: Creates temporary bridges inside one namespace and mutates bridge STP attributes. Defer scopes delete bridges and cleanup removes namespace.

Dependencies and integration points: Requires bridge driver support for `IFLA_BR_STP_MODE`, iproute2 support for the option, `jq`, and root namespace operations.

Risks: Exact JSON field names (`stp_mode`, `stp_state`) are iproute2-dependent. Tests assume no userspace `/sbin/bridge-stp` interaction inside non-init netns for auto mode.

Test signals: `log_test` results for nine cases validate mode defaults, transitions, rejection rules, and state mappings.
