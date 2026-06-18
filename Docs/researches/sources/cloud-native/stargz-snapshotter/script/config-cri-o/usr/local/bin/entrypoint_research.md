# sources/cloud-native/stargz-snapshotter/script/config-cri-o/usr/local/bin/entrypoint

Purpose: Entrypoint for privileged CRI-O test containers using systemd.
Important APIs/types/functions: cgroup-v2 setup block, sysctl/iptables host tweaks, and generated `demo.target`.
Control flow: enables nested cgroups, configures loopback NAT needed by CRI-O tests, writes a systemd target wanting stargz-store and CRI-O, then execs `/sbin/init` for that target.
State and persistence: writes `/lib/systemd/system/demo.target` and mutates sysctl/iptables inside the privileged container.
Dependencies and integration points: integrates Docker-in-Docker style cgroup setup, CRI-O, systemd, and stargz-store service.
Risks: requires privileged container permissions; iptables/sysctl changes are test-environment-specific.
Test signals: used by CRI-O test images built in `script/cri-o/test.sh`.
