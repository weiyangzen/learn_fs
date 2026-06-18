# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_broadcast.sh

Purpose: tests directed broadcast forwarding behavior across a three-interface IPv4 router. It verifies local broadcast replies, forwarded directed broadcasts, and drops for same-subnet or all-hosts broadcast cases under `bc_forwarding`.

Important functions are `bc_forwarding_disable`, `bc_forwarding_enable`, `bc_forwarding_restore`, `ping_test_from`, and `ping_ipv4`. Host setup creates three VRFs and static routes through router interfaces `$rp1`, `$rp2`, and `$rp3`. `ping_test_from` runs `$PING -b` inside the source VRF, greps for the expected reply source, and uses `check_err_fail` for expected success/failure.

Control flow disables `icmp_echo_ignore_broadcasts`, tests with `net.ipv4.conf.*.bc_forwarding=0`, restores, enables forwarding on `all`, `$rp1`, and `$rp2`, and retests expected forwarding and dropping. State is kernel VRF/interface/address/route state and sysctl state saved through `sysctl_set`/`sysctl_restore`. Risks include sysctl leakage on early failure, broadcast ping behavior varying by kernel configuration, and grep-based reply-source assertions. Test signals are many `log_test` entries documenting expected responder: router itself when forwarding is disabled, remote host when enabled, and no reply for same-interface directed broadcasts.
