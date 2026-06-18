# sources/cloud-native/cri-o/test/helpers.bash

## Purpose
Primary BATS integration-test harness for launching isolated CRI-O instances, managing images, network config, runtime helpers, cleanup, feature skips, and common assertions.

## Important APIs, Types, And Functions
Key functions include `setup_test`, `crio`, `crictl`, `runtime`, `retry`, `wait_until_reachable`, `copyimg`, `setup_img`, `setup_crio`, `check_images`, `start_crio_no_setup`, `start_crio`, `cleanup_*`, `stop_crio`, `restart_crio`, `cleanup_test`, `prepare_network_conf`, `pod_ip`, `ping_pod`, `wait_for_log`, `replace_config`, runtime/workload config creators, cgroup helpers, `has_criu`, `prepare_cni_plugin`, `contains`, and `annotations_equal`.

## Control Flow
`setup_test` creates a per-test root, config/log/socket directories, NRI config, isolated CNI plugin directory, crictl config, and SELinux labeling when needed. `setup_crio` preloads images, writes default/custom CRI-O config, removes `nodev` mount options, and writes a default CNI conflist. `start_crio` launches CRI-O and verifies image availability. Cleanup tears down containers, pods, CRI-O, networks, mounts, temp directories, and optional kata processes; failure mode can preserve test artifacts. Helper functions gate tests on kernel, crictl, SELinux, AppArmor, CRIU, Buildah, cgroup version, runtime type, and CPU/memory topology.

## State And Persistence
Creates extensive per-test filesystem state under `$TESTDIR`, including CRI-O storage, runroot, config, logs, CNI configs, hooks, sockets, and crictl config. Also uses `.artifacts` image caches from `common.sh` and may touch system cgroups, AppArmor profiles, pinned namespaces, and journal logs.

## Dependencies And Integration Points
Integrates BATS, CRI-O, crictl, conmon, runtime binaries, CNI plugins, jq, Python, netstat, systemd, AppArmor/SELinux, CRIU, buildah, pinns, copyimg, and host kernel interfaces.

## Risks And Test Signals
This is high-blast-radius test infrastructure. Shell globals are heavily shared, so ordering and sourcing matter. Cleanup assumes mount paths under `$TESTDIR` and may fail if commands hang or require privileges. `wait_for_log` uses polling and regex extraction, making timing/log format flakes possible. Despite risk, it is the strongest integration signal for real CRI-O lifecycle behavior.
