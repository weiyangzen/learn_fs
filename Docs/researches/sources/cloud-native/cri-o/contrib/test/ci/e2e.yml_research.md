# sources/cloud-native/cri-o/contrib/test/ci/e2e.yml

## Purpose
Default e2e task include that runs the standard Kubernetes node/runtime e2e flow using e2e-base.yml patterns.

## Important APIs, Types, and Functions
YAML playbook/tasks/vars consumed by ansible-playbook; important entries are include_tasks, environment maps, systemd tasks, copy/lineinfile/sysctl/shell tasks, async/poll settings, and variable maps for runtime/test behavior.

## Control Flow
Execution is declarative in Ansible order: top-level playbooks load vars.yml and include task files; setup provisions host dependencies; integration/critest/e2e build CRI-O, start services, tune host networking/cgroups, and run long async test commands.

## State and Persistence
Persists installed packages, cloned/built tools, /etc/crio snippets, /etc/subuid/subgid, sysctls, iptables rules, systemd service states, artifacts under /tmp/artifacts, and test logs/results.

## Dependencies
Depends on Ansible modules, root privileges, GOPATH=/usr/go, CRI-O build task files under contrib/test/ci/build, systemd, yum/package managers, Kubernetes/kubetest/critest, runc/crun/Kata tooling, and host kernel features.

## Integration Points
These files form the CI orchestration layer for validating CRI-O against integration, critest, and Kubernetes e2e suites; vars.yml is shared across all playbooks.

## Risks and Edge Cases
Risks include host mutation, broad package updates, firewall/sysctl changes, async failures hidden until poll, version drift in external repos/tools, and distro-specific conditional gaps. Kata skip injection edits tests in-place.

## Test Signals
Signals are Ansible task success, systemd CRI-O/customcluster readiness, generated artifacts/logs, critest reports, kubetest e2e.log, and make localintegration output.
