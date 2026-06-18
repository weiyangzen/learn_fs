<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/testutils/networking/firewall.go -->
# sources/cloud-native/moby/integration/internal/testutils/networking/firewall.go

Purpose: supplies firewall helpers for Moby integration tests that need to modify or observe host firewall state around daemon networking behavior.

Important APIs/types/functions: `SetFilterForwardPolicies` reads and temporarily changes `iptables` and `ip6tables` `FORWARD` chain policies. `FirewalldRunning` probes `firewall-cmd --state`. `FirewalldReload` triggers a firewalld reload and polls a daemon-reported reload timestamp until it changes.

Control flow: `SetFilterForwardPolicies` extracts the current policy with `rePolicy`, skips commands already at the desired policy, changes others with `-P FORWARD`, and registers `t.Cleanup` to restore originals. `FirewalldReload` exits early if firewalld is not running, captures `d.FirewallReloadedAt`, runs `firewall-cmd --reload`, then polls until the daemon reports a new non-empty reload time.

State/persistence: directly mutates host IPv4/IPv6 filter policies and relies on cleanup to restore them. `FirewalldReload` mutates firewalld runtime state and observes daemon state through the test daemon helper.

Dependencies/integration: uses `os/exec`, `icmd`, `poll`, gotest assertions, and `internal/testutil/daemon`. Bridge tests use these helpers to create controlled FORWARD-policy and firewalld reload scenarios.

Risks: requires privileged firewall tools and assumes English iptables output containing `policy WORD`. Cleanup logs but does not fail if restoration fails, so later tests can inherit bad firewall policy. Firewalld reload behavior is asynchronous and can be flaky if daemon reload tracking is delayed.

Test signals: consumers verify policies are set/restored, firewalld reloads complete, and deleted-network firewall rules do not return after reload. There are no direct unit tests for regex parsing or restore failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/testutils/networking/firewall.go -->
