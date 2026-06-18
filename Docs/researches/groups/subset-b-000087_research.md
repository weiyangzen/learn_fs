# Research Group subset-b-000087

Grouped research report for CRI-O subset B item subset-b-000087. Each section preserves the original source path and is bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/kube-local/kube-local -->

# sources/cloud-native/cri-o/contrib/kube-local/kube-local

## Purpose
Interactive/auto-install Bash utility for building a local CRI-O plus Kubernetes development cluster, running optional kubectl commands, and uninstalling generated runtime/orchestration assets.

## Important APIs, Types, and Functions
Functions include print_msg, question_with_answer_yes_no, exec_cmd, detect_system, detect_cgroupv1, install_golang, install_project, install_runtime, install_container_network_plugin, install_container_orchestration, load_local_up_cluster, kubectl_retry, kubectl_exec, cleanup/execute_cleanup, load_profile, and usage. It relies heavily on profile variables such as runtime versions, paths, package lists, and auto-install flags.

## Control Flow
Main control loads a profile, parses getopt flags, mutates runtime/orchestration versions or autoinstall options, then start() detects distro, confirms risk, updates packages, forces cgroup v1, installs Go, CRI-O/crictl/conmon/CNI, builds Kubernetes, starts local-up-cluster, optionally runs a kubectl command, and optionally tears down. Uninstall enters detect_system then cleanup.

## State and Persistence
Persists shell exports in GO_ENV_VARS between kube-local section markers, clones/builds repositories under GOPATH, installs Go under GOLANG_DIR_PATH, installs packages/services, writes logs to LOG_FILE, creates output files with environment metadata, changes profile AUTOINSTALL via sed, and removes runtime, CNI, Go, Kubernetes, logs, and services during cleanup.

## Dependencies
Depends on sudo, distro package managers, rpm/dpkg tools, git, wget, tar, sha256sum, make, systemctl, grubby, CNI plugin build scripts, Kubernetes local-up-cluster, CRI-O build targets, crictl, conmon, and profile-defined package/version constants.

## Integration Points
Integrates with developer host OS, systemd crio service, Kubernetes hack/local-up-cluster.sh, /etc/os-release, /proc/cmdline, /etc/profile-like Go env file, package repositories, and kubectl scripts.

## Risks and Edge Cases
High privilege and destructive behavior: package updates/removals, profile mutation, cgroup kernel argument changes/reboot, forced process kills, sudo rm -rf, branch checkout, and command construction through variable-expanded strings. It assumes older cgroup v1 requirements and has fragile shell quoting in several commands.

## Test Signals
No local tests in file; operational signals are printed/logged command success, kubectl_retry cluster readiness, sha256 validation for Go tarball, and cleanup/uninstall paths. Shellcheck disables indicate known quoting/expansion tradeoffs.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/kube-local/kube-local -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/metrics-exporter/Containerfile -->

# sources/cloud-native/cri-o/contrib/metrics-exporter/Containerfile

## Purpose
Minimal container image definition for the metrics exporter binary.

## Important APIs, Types, and Functions
FROM scratch, COPY bin/metrics-exporter /metrics-exporter, ENTRYPOINT /metrics-exporter.

## Control Flow
Build output must place a statically runnable metrics-exporter at bin/metrics-exporter; container starts the binary directly.

## State and Persistence
No mutable state in image; runtime state is whatever the binary writes to Kubernetes ConfigMaps or serves over HTTP.

## Dependencies
Depends on container build context containing bin/metrics-exporter and on the binary being suitable for scratch.

## Integration Points
Used with cluster.yaml Deployment image quay.io/crio/metrics-exporter:latest.

## Risks and Edge Cases
No shell, CA bundle, or debug tooling in scratch image; binary must include all runtime needs. Tagging latest in deployment can obscure provenance.

## Test Signals
No direct tests; successful build/run and exporter HTTP readiness are the practical signals.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/metrics-exporter/Containerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/metrics-exporter/cluster.yaml -->

# sources/cloud-native/cri-o/contrib/metrics-exporter/cluster.yaml

## Purpose
Kubernetes manifest deploying cri-o-metrics-exporter with namespace, service account, RBAC, deployment, and service.

## Important APIs, Types, and Functions
Defines Namespace, ServiceAccount, ClusterRole for listing nodes, ClusterRoleBinding, namespace Role for ConfigMap get/create/update, RoleBinding, Deployment with CRIO_METRICS_PORT and POD_NAMESPACE env, and Service on port 80 to targetPort 8080.

## Control Flow
Apply creates the namespace/RBAC first, starts one exporter pod, lets main.go list nodes and update a ConfigMap, then exposes the exporter through a ClusterIP Service.

## State and Persistence
Persists Prometheus scrape configuration into a ConfigMap named after namespace/service; Deployment has no volumes and relies on env/in-cluster service account token.

## Dependencies
Depends on Kubernetes RBAC APIs, apps/v1 Deployment, exporter image quay.io/crio/metrics-exporter:latest, node list permission, and ConfigMap write permission.

## Integration Points
Tied to main.go default namespace/service/configMap names and Prometheus consuming the generated ConfigMap/service target.

## Risks and Edge Cases
RBAC permits cluster-wide node listing; imagePullPolicy Always plus latest risks non-reproducible rollout; no probes or securityContext are defined; node address selection in code assumes usable first node address.

## Test Signals
Manifest validation and pod logs are test signals; exporter should create/update ConfigMap and serve per-node proxy endpoints.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/metrics-exporter/cluster.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/metrics-exporter/dashboard.json -->

# sources/cloud-native/cri-o/contrib/metrics-exporter/dashboard.json

## Purpose
Grafana dashboard JSON for visualizing CRI-O Prometheus metrics per selected node.

## Important APIs, Types, and Functions
Dashboard inputs require Prometheus datasource; panels graph rates for container_runtime_crio_operations_total, operations_errors_total, and operations_latency_seconds_total_count; templating variable node is derived from container_runtime_crio_operations instance labels.

## Control Flow
Grafana imports JSON, user selects nodes, repeated panels query Prometheus over last 6h with configurable refresh intervals.

## State and Persistence
Dashboard itself is persisted by Grafana import; no application state beyond datasource and variable selection.

## Dependencies
Depends on Grafana schemaVersion 22, Prometheus datasource, and CRI-O metrics names/labels populated by the exporter/runtime.

## Integration Points
Complements metrics-exporter/cluster.yaml and main.go by consuming the instance labels generated in scrape configs.

## Risks and Edge Cases
Queries can break if metric names or labels change; latency panel uses a count-rate metric and may not represent duration; legacy Grafana panel schema may need migration.

## Test Signals
Import success and populated Prometheus queries are primary signals; empty node variable indicates scrape/exporter mismatch.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/metrics-exporter/dashboard.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/metrics-exporter/main.go -->

# sources/cloud-native/cri-o/contrib/metrics-exporter/main.go

## Purpose
In-cluster Go HTTP proxy that discovers Kubernetes nodes, writes Prometheus scrape config, and proxies per-node CRI-O metrics endpoints.

## Important APIs, Types, and Functions
main calls run. run builds in-cluster client, lists nodes, registers http.Handle("/nodeName") per node, generates jobConfig YAML, creates or updates a ConfigMap key config, and listens on :8080. handler.ServeHTTP builds http://nodeIP:CRIO_METRICS_PORT/metrics and copies 200 responses.

## Control Flow
Startup is one-shot discovery/config generation followed by serving HTTP. Each request proxies synchronously to a node CRI-O metrics endpoint using request context; non-200 status is propagated and transport/read/write errors are logged.

## State and Persistence
Kubernetes ConfigMap is persistent state. Process keeps node handlers in global http.DefaultServeMux; node list is not refreshed after startup.

## Dependencies
Depends on client-go in-cluster config, env.Default helper, logrus, net/http, Kubernetes nodes API, ConfigMaps API, and CRI-O metrics port default 9090.

## Integration Points
Runs under cluster.yaml service account/RBAC and service; Prometheus can scrape service paths created in ConfigMap.

## Risks and Edge Cases
Uses node.Status.Addresses[0] without type or length checks; startup fails outside cluster; config update treats any Get error as create path and can mask permission/transient errors; no timeouts on DefaultClient; handlers stale if nodes change.

## Test Signals
No unit tests visible; deployment smoke test is ConfigMap creation plus HTTP proxy success for each node endpoint.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/metrics-exporter/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/systemd/crio-wipe.service -->

# sources/cloud-native/cri-o/contrib/systemd/crio-wipe.service

## Purpose
Systemd oneshot unit that invokes crio wipe during boot to clean stale runtime/container state before CRI-O starts.

## Important APIs, Types, and Functions
Unit has DefaultDependencies=false, Before=crio.service, Wants=local-fs.target, After=local-fs.target, ConditionPathExists=!/etc/crio/crio.conf, ExecStart=/usr/local/bin/crio wipe.

## Control Flow
When enabled, systemd runs the oneshot before crio.service if condition passes, then remains after exit due to RemainAfterExit=yes.

## State and Persistence
Mutates CRI-O storage/runtime state through crio wipe; systemd unit state remains active after completion.

## Dependencies
Depends on /usr/local/bin/crio and local filesystems; condition references /etc/crio/crio.conf.

## Integration Points
Pairs with crio.service ordering so cleanup occurs before daemon start.

## Risks and Edge Cases
ConditionPathExists negation means wipe may be skipped when config exists; wipe is destructive by design; failures can block dependent startup depending systemd behavior.

## Test Signals
Operational signal is systemctl status/journal for crio-wipe and subsequent CRI-O clean start.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/systemd/crio-wipe.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/systemd/crio.service -->

# sources/cloud-native/cri-o/contrib/systemd/crio.service

## Purpose
Systemd service unit for running CRI-O as a long-lived container runtime daemon.

## Important APIs, Types, and Functions
ExecStart=/usr/local/bin/crio, ExecReload=/bin/kill -s HUP $MAINPID, Type=notify, KillMode=process, Restart=on-failure, OOMScoreAdjust=-999, Delegate=yes, LimitNOFILE/LimitNPROC/LimitCORE=infinity, TasksMax=infinity.

## Control Flow
Starts after network-online.target and crio-wipe.service, notifies systemd readiness, reloads via SIGHUP, restarts on failure.

## State and Persistence
CRI-O persists state under its configured storage/run paths; systemd tracks service lifecycle and cgroup delegation.

## Dependencies
Depends on systemd notify support, /usr/local/bin/crio, crio-wipe.service, and kernel cgroup delegation.

## Integration Points
Main service target for kubelet/container workloads and for kube-local/CI playbooks.

## Risks and Edge Cases
KillMode=process leaves child process handling to daemon; high limits and OOMScoreAdjust make daemon durable but privileged; wrong binary path breaks packaged installs.

## Test Signals
Test signals are systemctl start/status, readiness notification, reload behavior, and runtime socket availability.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/systemd/crio.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/ansible.cfg -->

# sources/cloud-native/cri-o/contrib/test/ci/ansible.cfg

## Purpose
Ansible configuration tuned for CRI-O CI playbooks.

## Important APIs, Types, and Functions
Sets callbacks, forks=10, smart gathering with network subset, host_key_checking=false, root remote_user, log_path=$ARTIFACTS/main.log, static includes, suppressed warnings/skipped output, retry_files disabled, SSH ControlPersist and pipelining.

## Control Flow
Ansible reads this config before playbooks, shaping connection, logging, callback, and fact behavior.

## State and Persistence
Persists logs under ARTIFACTS/main.log; no other direct state.

## Dependencies
Depends on Ansible version accepting legacy static include and callback_whitelist settings.

## Integration Points
Used by contrib/test/ci playbooks during local/remote CI execution.

## Risks and Edge Cases
Disabling host key checking and warnings favors CI speed over security/diagnostics; deprecated options may drift with Ansible versions; log path requires ARTIFACTS.

## Test Signals
Ansible startup and playbook verbosity/log placement validate this file.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/ansible.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/critest-images.yaml -->

# sources/cloud-native/cri-o/contrib/test/ci/critest-images.yaml

## Purpose
Default critest image mirror configuration.

## Important APIs, Types, and Functions
Maps defaultTestContainerImage to quay.io/crio/busybox:1 and webServerTestImage to quay.io/crio/nginx:1.18.

## Control Flow
critest reads this YAML to avoid upstream image defaults.

## State and Persistence
No state.

## Dependencies
Depends on cri-tools critest image config schema and quay.io/crio images.

## Integration Points
Used or regenerated by critest.yml for CRI validation.

## Risks and Edge Cases
Images/tags must exist and match test expectations.

## Test Signals
critest pull/use success is the signal.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/critest-images.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/critest-main.yml -->

# sources/cloud-native/cri-o/contrib/test/ci/critest-main.yml

## Purpose
Top-level Ansible playbook for running CRI conformance/critest validation and fixing artifact permissions.

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

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/critest-main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/critest.yml -->

# sources/cloud-native/cri-o/contrib/test/ci/critest.yml

## Purpose
Task include that builds CRI-O, configures cgroupfs for critest, starts CRI-O, prepares networking/artifacts, writes critest image config, and runs critest asynchronously.

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

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/critest.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/e2e-base.yml -->

# sources/cloud-native/cri-o/contrib/test/ci/e2e-base.yml

## Purpose
Shared Kubernetes e2e base setup for CRI-O CI, including CRI-O install/start, runtime handler injection, SSH keys, custom cluster start, readiness wait, and bridge networking sysctls.

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

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/e2e-base.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/e2e-features.yml -->

# sources/cloud-native/cri-o/contrib/test/ci/e2e-features.yml

## Purpose
Focused Kubernetes feature e2e task set built on e2e-base.yml with kubetest command construction for selected NodeFeature/Feature suites.

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

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/e2e-features.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/e2e-main.yml -->

# sources/cloud-native/cri-o/contrib/test/ci/e2e-main.yml

## Purpose
Top-level Ansible playbook for CRI-O Kubernetes e2e execution.

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

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/e2e-main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/e2e.yml -->

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

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/e2e.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/integration-main.yml -->

# sources/cloud-native/cri-o/contrib/test/ci/integration-main.yml

## Purpose
Top-level Ansible playbook for CRI-O integration tests, optionally installing Kata, building CRI-O, starting service, running integration tasks, and relaxing artifact permissions.

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

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/integration-main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/integration.yml -->

# sources/cloud-native/cri-o/contrib/test/ci/integration.yml

## Purpose
Integration test task include that patches Kubernetes test verbosity, configures subuid/subgid/user namespaces, applies optional crun/Kata environments and skips, then runs make localintegration.

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

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/integration.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/setup-main.yml -->

# sources/cloud-native/cri-o/contrib/test/ci/setup-main.yml

## Purpose
Top-level setup playbook that includes setup.yml under GOPATH=/usr/go with setup tag.

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

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/setup-main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/setup.yml -->

# sources/cloud-native/cri-o/contrib/test/ci/setup.yml

## Purpose
Setup task list that installs OS packages, Go tools, BATS, cri-tools, runtimes, Kubernetes, CNI plugins, conmon/conmon-rs, jq, kubetest, CRI-O config snippets, and parallel build support.

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

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/setup.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/system-packages.yml -->

# sources/cloud-native/cri-o/contrib/test/ci/system-packages.yml

## Purpose
System package installation playbook for CI hosts across Fedora/RHEL/CentOS variants.

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

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/system-packages.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/system.yml -->

# sources/cloud-native/cri-o/contrib/test/ci/system.yml

## Purpose
System tuning playbook for CI hosts, creating CNI dirs, sysctl/network settings, quota kernel flags, SELinux cgroup boolean, storage config cleanup, and CRI-O storage dir.

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

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/system.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/vars.yml -->

# sources/cloud-native/cri-o/contrib/test/ci/vars.yml

## Purpose
Central Ansible variable file controlling CI runtime selection, SELinux toggles, artifact paths, test environments, image mirrors, and Kata-specific skips/configuration.

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

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/test/ci/vars.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/crictl.yaml -->

# sources/cloud-native/cri-o/crictl.yaml

## Purpose
crictl client endpoint configuration for using CRI-O over its Unix socket.

## Important APIs, Types, and Functions
runtime-endpoint and image-endpoint both point at unix:///var/run/crio/crio.sock; timeout is 10.

## Control Flow
crictl reads this YAML and directs runtime/image RPCs to CRI-O.

## State and Persistence
No persistent state beyond config file.

## Dependencies
Depends on crictl schema and CRI-O socket path.

## Integration Points
Used by operators/tests invoking crictl against local CRI-O.

## Risks and Edge Cases
Socket path differs from some newer /run paths; stale config causes failed diagnostics.

## Test Signals
crictl info/images/ps against CRI-O validates it.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/crictl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/crio-umount.conf -->

# sources/cloud-native/cri-o/crio-umount.conf

## Purpose
tmpfiles/systemd-umount style configuration for unmounting CRI-O storage/run mounts during cleanup/shutdown.

## Important APIs, Types, and Functions
Contains path/action entries targeting CRI-O storage and runtime mount locations.

## Control Flow
Consumed by systemd-tmpfiles or distro packaging hook to perform unmount cleanup.

## State and Persistence
Mutates mount namespace/state by unmounting configured paths; no application state.

## Dependencies
Depends on systemd tmpfiles semantics and CRI-O path conventions.

## Integration Points
Complements crio-wipe/service packaging cleanup.

## Risks and Edge Cases
Unmounting active paths can disrupt running containers; path drift makes it ineffective.

## Test Signals
Packaging/install tests and shutdown cleanup validate it.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/crio-umount.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/dependencies.yaml -->

# sources/cloud-native/cri-o/dependencies.yaml

## Purpose
Dependency metadata listing CRI-O component versions and external source dependencies for build/release automation.

## Important APIs, Types, and Functions
YAML entries define dependencies, names, versions/commits, and source locations used by automation.

## Control Flow
Tools parse the file to resolve or report dependency versions.

## State and Persistence
No runtime state; source of truth for dependency tracking.

## Dependencies
Depends on repository-specific dependency parser and upstream component availability.

## Integration Points
Integrates with release, CI, and update workflows needing synchronized component versions.

## Risks and Edge Cases
Stale pins, unavailable upstream refs, or schema drift can break automated dependency updates.

## Test Signals
Validation is parser success and build/release jobs using declared versions.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/dependencies.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/hack/apparmor_tag.sh -->

# sources/cloud-native/cri-o/hack/apparmor_tag.sh

## Purpose
Small build/test helper that emits a Go build tag or validation signal based on host capability or repository policy.

## Important APIs, Types, and Functions
Shell script using pkg-config, cc preprocessor checks, grep, or make/config validation depending on file.

## Control Flow
Runs quickly in build/test discovery; prints a tag such as apparmor, exclude_graphdriver_btrfs, btrfs_noversion, libsubid/openpgp/seccomp/selinux capability, or fails when policy is violated.

## State and Persistence
No persistent state.

## Dependencies
Depends on shell plus relevant system headers/pkg-config packages or repository files.

## Integration Points
Used by Makefile/go test build tag selection and validation jobs.

## Risks and Edge Cases
Host-dependent output can change build coverage; missing headers silently exclude features.

## Test Signals
Signal is stdout tag or non-zero validation exit.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/hack/apparmor_tag.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/hack/btrfs_installed_tag.sh -->

# sources/cloud-native/cri-o/hack/btrfs_installed_tag.sh

## Purpose
Small build/test helper that emits a Go build tag or validation signal based on host capability or repository policy.

## Important APIs, Types, and Functions
Shell script using pkg-config, cc preprocessor checks, grep, or make/config validation depending on file.

## Control Flow
Runs quickly in build/test discovery; prints a tag such as apparmor, exclude_graphdriver_btrfs, btrfs_noversion, libsubid/openpgp/seccomp/selinux capability, or fails when policy is violated.

## State and Persistence
No persistent state.

## Dependencies
Depends on shell plus relevant system headers/pkg-config packages or repository files.

## Integration Points
Used by Makefile/go test build tag selection and validation jobs.

## Risks and Edge Cases
Host-dependent output can change build coverage; missing headers silently exclude features.

## Test Signals
Signal is stdout tag or non-zero validation exit.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/hack/btrfs_installed_tag.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/hack/btrfs_tag.sh -->

# sources/cloud-native/cri-o/hack/btrfs_tag.sh

## Purpose
Small build/test helper that emits a Go build tag or validation signal based on host capability or repository policy.

## Important APIs, Types, and Functions
Shell script using pkg-config, cc preprocessor checks, grep, or make/config validation depending on file.

## Control Flow
Runs quickly in build/test discovery; prints a tag such as apparmor, exclude_graphdriver_btrfs, btrfs_noversion, libsubid/openpgp/seccomp/selinux capability, or fails when policy is violated.

## State and Persistence
No persistent state.

## Dependencies
Depends on shell plus relevant system headers/pkg-config packages or repository files.

## Integration Points
Used by Makefile/go test build tag selection and validation jobs.

## Risks and Edge Cases
Host-dependent output can change build coverage; missing headers silently exclude features.

## Test Signals
Signal is stdout tag or non-zero validation exit.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/hack/btrfs_tag.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/hack/build-rpms.sh -->

# sources/cloud-native/cri-o/hack/build-rpms.sh

## Purpose
Release helper that builds CRI-O RPM/SRPM artifacts and a local yum/dnf repository.

## Important APIs, Types, and Functions
Sources hack/lib/init.sh, requires rpmbuild and createrepo, calls RPM version helpers, rpmspec, dnf builddep, Go download, rpmbuild, make clean, and createrepo.

## Control Flow
Creates rpm temp SOURCES, archives repo plus CI data, optionally forces yum IPv4, installs builddeps/latest Go, runs rpmbuild with version/release/commit defines, moves artifacts to _output/local/releases/rpms, creates repo metadata and .repo files.

## State and Persistence
Writes rpm temp tree, _output release/RPM directories, .commit marker, repo metadata, and may edit /etc/yum.conf.

## Dependencies
Depends on RPM toolchain, dnf, curl, go.dev availability, spec file, Makefile clean, and hack/lib build helpers.

## Integration Points
Used by release/CI jobs to create local installable RPM repositories.

## Risks and Edge Cases
Network-dependent Go download, privileged host package changes, best-effort builddep, /etc/yum.conf mutation, and destructive make clean.

## Test Signals
Successful rpmbuild, RPM files, SRPM, createrepo metadata, and local-release.repo are output signals.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/hack/build-rpms.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/hack/check-nri-bats-tests.sh -->

# sources/cloud-native/cri-o/hack/check-nri-bats-tests.sh

## Purpose
Consistency check ensuring every Go NRI test case is represented in the NRI BATS wrapper.

## Important APIs, Types, and Functions
Runs test/nri/nri.test -test.list Test and greps test/nri.bats for matching -test.run invocations.

## Control Flow
Iterates listed tests, reports missing cases, accumulates status, exits non-zero if any are absent.

## State and Persistence
No state.

## Dependencies
Depends on built nri.test binary, grep, realpath, and NRI BATS file naming.

## Integration Points
Used by validation/CI to keep Go and BATS NRI coverage synchronized.

## Risks and Edge Cases
Pattern matching can miss renamed or parameterized invocations; requires binary built before running.

## Test Signals
Non-zero exit and missing-test messages are the signal.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/hack/check-nri-bats-tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/hack/go-install.sh -->

# sources/cloud-native/cri-o/hack/go-install.sh

## Purpose
Helper to either copy an existing tool binary into a destination or install it with go install.

## Important APIs, Types, and Functions
Arguments DEST_DIR CMD GO_INSTALL_LOCATION; uses command -v, mkdir, cp, and GOBIN=DEST_DIR go install.

## Control Flow
Validates three args; if CMD exists on PATH copy it, otherwise install requested module into destination.

## State and Persistence
Writes DEST_DIR/CMD binary.

## Dependencies
Depends on Go toolchain for missing binaries and shell coreutils.

## Integration Points
Used by build scripts to materialize required Go tools reproducibly while reusing installed tools.

## Risks and Edge Cases
Existing PATH binary may be wrong version; go install is network/module-cache dependent.

## Test Signals
Destination binary existence and version output validate it.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/hack/go-install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/hack/govulncheck.sh -->

# sources/cloud-native/cri-o/hack/govulncheck.sh

## Purpose
Vulnerability scanning helper that installs govulncheck, emits OpenVEX, and optionally fails on module dependency vulnerabilities.

## Important APIs, Types, and Functions
Uses apt-get to install native deps, go install golang.org/x/vuln/cmd/govulncheck@v1.1.4, govulncheck -format openvex/json -tags=test ./..., jq parsing, VEX_ONLY flag.

## Control Flow
Installs dependencies/tool, writes build/cri-o.openvex.json, optionally exits if VEX_ONLY, otherwise generates JSON report, prints stdlib/module vuln summaries, and exits 1 for module vulnerabilities.

## State and Persistence
Writes build/cri-o.openvex.json and temp JSON report.

## Dependencies
Depends on Debian apt packages, Go, module download, jq, and govulncheck schema.

## Integration Points
CI security scan lane for CRI-O.

## Risks and Edge Cases
Runs apt-get on host, version may lag supported Go, JSON query assumes schema, stdlib vulnerabilities are printed but do not fail.

## Test Signals
OpenVEX output and exit status are the scan signals.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/hack/govulncheck.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/hack/lib/constants.sh -->

# sources/cloud-native/cri-o/hack/lib/constants.sh

## Purpose
Reusable Bash library for CRI-O hack scripts.

## Important APIs, Types, and Functions
Defines os:: namespaced functions/constants for init, logging, stack traces, system monitoring, environment/PATH/tempdir setup, binary lookup, text coloring, command traps, and ensure helpers.

## Control Flow
hack/lib/init.sh sets strict mode, finds OS_ROOT, sources all hack/lib scripts, installs ERR stacktrace, updates PATH, and initializes temp dirs; leaf libraries provide callable helpers.

## State and Persistence
Exports OS_ROOT, OS_SCRIPT_START_TIME, output/temp variables, writes optional logs/system metric data, and registers traps/cleanup.

## Dependencies
Depends on Bash, find, date, tput/terminal capabilities, OS tools such as ps/top/free depending on system logging, and repository layout.

## Integration Points
Sourced by hack/build-rpms.sh and other CRI-O automation scripts.

## Risks and Edge Cases
Sourcing all libraries can collide with readonly names; strict mode makes unset vars fatal; system logging helpers can create background processes/log files.

## Test Signals
Scripts using init.sh, shellcheck, and CI build helpers validate behavior.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/hack/lib/constants.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/hack/lib/init.sh -->

# sources/cloud-native/cri-o/hack/lib/init.sh

## Purpose
Reusable Bash library for CRI-O hack scripts.

## Important APIs, Types, and Functions
Defines os:: namespaced functions/constants for init, logging, stack traces, system monitoring, environment/PATH/tempdir setup, binary lookup, text coloring, command traps, and ensure helpers.

## Control Flow
hack/lib/init.sh sets strict mode, finds OS_ROOT, sources all hack/lib scripts, installs ERR stacktrace, updates PATH, and initializes temp dirs; leaf libraries provide callable helpers.

## State and Persistence
Exports OS_ROOT, OS_SCRIPT_START_TIME, output/temp variables, writes optional logs/system metric data, and registers traps/cleanup.

## Dependencies
Depends on Bash, find, date, tput/terminal capabilities, OS tools such as ps/top/free depending on system logging, and repository layout.

## Integration Points
Sourced by hack/build-rpms.sh and other CRI-O automation scripts.

## Risks and Edge Cases
Sourcing all libraries can collide with readonly names; strict mode makes unset vars fatal; system logging helpers can create background processes/log files.

## Test Signals
Scripts using init.sh, shellcheck, and CI build helpers validate behavior.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/hack/lib/init.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/hack/lib/log/output.sh -->

# sources/cloud-native/cri-o/hack/lib/log/output.sh

## Purpose
Reusable Bash library for CRI-O hack scripts.

## Important APIs, Types, and Functions
Defines os:: namespaced functions/constants for init, logging, stack traces, system monitoring, environment/PATH/tempdir setup, binary lookup, text coloring, command traps, and ensure helpers.

## Control Flow
hack/lib/init.sh sets strict mode, finds OS_ROOT, sources all hack/lib scripts, installs ERR stacktrace, updates PATH, and initializes temp dirs; leaf libraries provide callable helpers.

## State and Persistence
Exports OS_ROOT, OS_SCRIPT_START_TIME, output/temp variables, writes optional logs/system metric data, and registers traps/cleanup.

## Dependencies
Depends on Bash, find, date, tput/terminal capabilities, OS tools such as ps/top/free depending on system logging, and repository layout.

## Integration Points
Sourced by hack/build-rpms.sh and other CRI-O automation scripts.

## Risks and Edge Cases
Sourcing all libraries can collide with readonly names; strict mode makes unset vars fatal; system logging helpers can create background processes/log files.

## Test Signals
Scripts using init.sh, shellcheck, and CI build helpers validate behavior.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/hack/lib/log/output.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/hack/lib/log/stacktrace.sh -->

# sources/cloud-native/cri-o/hack/lib/log/stacktrace.sh

## Purpose
Reusable Bash library for CRI-O hack scripts.

## Important APIs, Types, and Functions
Defines os:: namespaced functions/constants for init, logging, stack traces, system monitoring, environment/PATH/tempdir setup, binary lookup, text coloring, command traps, and ensure helpers.

## Control Flow
hack/lib/init.sh sets strict mode, finds OS_ROOT, sources all hack/lib scripts, installs ERR stacktrace, updates PATH, and initializes temp dirs; leaf libraries provide callable helpers.

## State and Persistence
Exports OS_ROOT, OS_SCRIPT_START_TIME, output/temp variables, writes optional logs/system metric data, and registers traps/cleanup.

## Dependencies
Depends on Bash, find, date, tput/terminal capabilities, OS tools such as ps/top/free depending on system logging, and repository layout.

## Integration Points
Sourced by hack/build-rpms.sh and other CRI-O automation scripts.

## Risks and Edge Cases
Sourcing all libraries can collide with readonly names; strict mode makes unset vars fatal; system logging helpers can create background processes/log files.

## Test Signals
Scripts using init.sh, shellcheck, and CI build helpers validate behavior.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/hack/lib/log/stacktrace.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/hack/lib/log/system.sh -->

# sources/cloud-native/cri-o/hack/lib/log/system.sh

## Purpose
Reusable Bash library for CRI-O hack scripts.

## Important APIs, Types, and Functions
Defines os:: namespaced functions/constants for init, logging, stack traces, system monitoring, environment/PATH/tempdir setup, binary lookup, text coloring, command traps, and ensure helpers.

## Control Flow
hack/lib/init.sh sets strict mode, finds OS_ROOT, sources all hack/lib scripts, installs ERR stacktrace, updates PATH, and initializes temp dirs; leaf libraries provide callable helpers.

## State and Persistence
Exports OS_ROOT, OS_SCRIPT_START_TIME, output/temp variables, writes optional logs/system metric data, and registers traps/cleanup.

## Dependencies
Depends on Bash, find, date, tput/terminal capabilities, OS tools such as ps/top/free depending on system logging, and repository layout.

## Integration Points
Sourced by hack/build-rpms.sh and other CRI-O automation scripts.

## Risks and Edge Cases
Sourcing all libraries can collide with readonly names; strict mode makes unset vars fatal; system logging helpers can create background processes/log files.

## Test Signals
Scripts using init.sh, shellcheck, and CI build helpers validate behavior.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/hack/lib/log/system.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/hack/lib/util/ensure.sh -->

# sources/cloud-native/cri-o/hack/lib/util/ensure.sh

## Purpose
Reusable Bash library for CRI-O hack scripts.

## Important APIs, Types, and Functions
Defines os:: namespaced functions/constants for init, logging, stack traces, system monitoring, environment/PATH/tempdir setup, binary lookup, text coloring, command traps, and ensure helpers.

## Control Flow
hack/lib/init.sh sets strict mode, finds OS_ROOT, sources all hack/lib scripts, installs ERR stacktrace, updates PATH, and initializes temp dirs; leaf libraries provide callable helpers.

## State and Persistence
Exports OS_ROOT, OS_SCRIPT_START_TIME, output/temp variables, writes optional logs/system metric data, and registers traps/cleanup.

## Dependencies
Depends on Bash, find, date, tput/terminal capabilities, OS tools such as ps/top/free depending on system logging, and repository layout.

## Integration Points
Sourced by hack/build-rpms.sh and other CRI-O automation scripts.

## Risks and Edge Cases
Sourcing all libraries can collide with readonly names; strict mode makes unset vars fatal; system logging helpers can create background processes/log files.

## Test Signals
Scripts using init.sh, shellcheck, and CI build helpers validate behavior.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/hack/lib/util/ensure.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/hack/lib/util/environment.sh -->

# sources/cloud-native/cri-o/hack/lib/util/environment.sh

## Purpose
Reusable Bash library for CRI-O hack scripts.

## Important APIs, Types, and Functions
Defines os:: namespaced functions/constants for init, logging, stack traces, system monitoring, environment/PATH/tempdir setup, binary lookup, text coloring, command traps, and ensure helpers.

## Control Flow
hack/lib/init.sh sets strict mode, finds OS_ROOT, sources all hack/lib scripts, installs ERR stacktrace, updates PATH, and initializes temp dirs; leaf libraries provide callable helpers.

## State and Persistence
Exports OS_ROOT, OS_SCRIPT_START_TIME, output/temp variables, writes optional logs/system metric data, and registers traps/cleanup.

## Dependencies
Depends on Bash, find, date, tput/terminal capabilities, OS tools such as ps/top/free depending on system logging, and repository layout.

## Integration Points
Sourced by hack/build-rpms.sh and other CRI-O automation scripts.

## Risks and Edge Cases
Sourcing all libraries can collide with readonly names; strict mode makes unset vars fatal; system logging helpers can create background processes/log files.

## Test Signals
Scripts using init.sh, shellcheck, and CI build helpers validate behavior.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/hack/lib/util/environment.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/hack/lib/util/find.sh -->

# sources/cloud-native/cri-o/hack/lib/util/find.sh

## Purpose
Reusable Bash library for CRI-O hack scripts.

## Important APIs, Types, and Functions
Defines os:: namespaced functions/constants for init, logging, stack traces, system monitoring, environment/PATH/tempdir setup, binary lookup, text coloring, command traps, and ensure helpers.

## Control Flow
hack/lib/init.sh sets strict mode, finds OS_ROOT, sources all hack/lib scripts, installs ERR stacktrace, updates PATH, and initializes temp dirs; leaf libraries provide callable helpers.

## State and Persistence
Exports OS_ROOT, OS_SCRIPT_START_TIME, output/temp variables, writes optional logs/system metric data, and registers traps/cleanup.

## Dependencies
Depends on Bash, find, date, tput/terminal capabilities, OS tools such as ps/top/free depending on system logging, and repository layout.

## Integration Points
Sourced by hack/build-rpms.sh and other CRI-O automation scripts.

## Risks and Edge Cases
Sourcing all libraries can collide with readonly names; strict mode makes unset vars fatal; system logging helpers can create background processes/log files.

## Test Signals
Scripts using init.sh, shellcheck, and CI build helpers validate behavior.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/hack/lib/util/find.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/hack/lib/util/misc.sh -->

# sources/cloud-native/cri-o/hack/lib/util/misc.sh

## Purpose
Reusable Bash library for CRI-O hack scripts.

## Important APIs, Types, and Functions
Defines os:: namespaced functions/constants for init, logging, stack traces, system monitoring, environment/PATH/tempdir setup, binary lookup, text coloring, command traps, and ensure helpers.

## Control Flow
hack/lib/init.sh sets strict mode, finds OS_ROOT, sources all hack/lib scripts, installs ERR stacktrace, updates PATH, and initializes temp dirs; leaf libraries provide callable helpers.

## State and Persistence
Exports OS_ROOT, OS_SCRIPT_START_TIME, output/temp variables, writes optional logs/system metric data, and registers traps/cleanup.

## Dependencies
Depends on Bash, find, date, tput/terminal capabilities, OS tools such as ps/top/free depending on system logging, and repository layout.

## Integration Points
Sourced by hack/build-rpms.sh and other CRI-O automation scripts.

## Risks and Edge Cases
Sourcing all libraries can collide with readonly names; strict mode makes unset vars fatal; system logging helpers can create background processes/log files.

## Test Signals
Scripts using init.sh, shellcheck, and CI build helpers validate behavior.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/hack/lib/util/misc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/hack/lib/util/text.sh -->

# sources/cloud-native/cri-o/hack/lib/util/text.sh

## Purpose
Reusable Bash library for CRI-O hack scripts.

## Important APIs, Types, and Functions
Defines os:: namespaced functions/constants for init, logging, stack traces, system monitoring, environment/PATH/tempdir setup, binary lookup, text coloring, command traps, and ensure helpers.

## Control Flow
hack/lib/init.sh sets strict mode, finds OS_ROOT, sources all hack/lib scripts, installs ERR stacktrace, updates PATH, and initializes temp dirs; leaf libraries provide callable helpers.

## State and Persistence
Exports OS_ROOT, OS_SCRIPT_START_TIME, output/temp variables, writes optional logs/system metric data, and registers traps/cleanup.

## Dependencies
Depends on Bash, find, date, tput/terminal capabilities, OS tools such as ps/top/free depending on system logging, and repository layout.

## Integration Points
Sourced by hack/build-rpms.sh and other CRI-O automation scripts.

## Risks and Edge Cases
Sourcing all libraries can collide with readonly names; strict mode makes unset vars fatal; system logging helpers can create background processes/log files.

## Test Signals
Scripts using init.sh, shellcheck, and CI build helpers validate behavior.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/hack/lib/util/text.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/hack/lib/util/trap.sh -->

# sources/cloud-native/cri-o/hack/lib/util/trap.sh

## Purpose
Reusable Bash library for CRI-O hack scripts.

## Important APIs, Types, and Functions
Defines os:: namespaced functions/constants for init, logging, stack traces, system monitoring, environment/PATH/tempdir setup, binary lookup, text coloring, command traps, and ensure helpers.

## Control Flow
hack/lib/init.sh sets strict mode, finds OS_ROOT, sources all hack/lib scripts, installs ERR stacktrace, updates PATH, and initializes temp dirs; leaf libraries provide callable helpers.

## State and Persistence
Exports OS_ROOT, OS_SCRIPT_START_TIME, output/temp variables, writes optional logs/system metric data, and registers traps/cleanup.

## Dependencies
Depends on Bash, find, date, tput/terminal capabilities, OS tools such as ps/top/free depending on system logging, and repository layout.

## Integration Points
Sourced by hack/build-rpms.sh and other CRI-O automation scripts.

## Risks and Edge Cases
Sourcing all libraries can collide with readonly names; strict mode makes unset vars fatal; system logging helpers can create background processes/log files.

## Test Signals
Scripts using init.sh, shellcheck, and CI build helpers validate behavior.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/hack/lib/util/trap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/hack/libsubid_tag.sh -->

# sources/cloud-native/cri-o/hack/libsubid_tag.sh

## Purpose
Small build/test helper that emits a Go build tag or validation signal based on host capability or repository policy.

## Important APIs, Types, and Functions
Shell script using pkg-config, cc preprocessor checks, grep, or make/config validation depending on file.

## Control Flow
Runs quickly in build/test discovery; prints a tag such as apparmor, exclude_graphdriver_btrfs, btrfs_noversion, libsubid/openpgp/seccomp/selinux capability, or fails when policy is violated.

## State and Persistence
No persistent state.

## Dependencies
Depends on shell plus relevant system headers/pkg-config packages or repository files.

## Integration Points
Used by Makefile/go test build tag selection and validation jobs.

## Risks and Edge Cases
Host-dependent output can change build coverage; missing headers silently exclude features.

## Test Signals
Signal is stdout tag or non-zero validation exit.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/hack/libsubid_tag.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/hack/log-capitalized.sh -->

# sources/cloud-native/cri-o/hack/log-capitalized.sh

## Purpose
Small build/test helper that emits a Go build tag or validation signal based on host capability or repository policy.

## Important APIs, Types, and Functions
Shell script using pkg-config, cc preprocessor checks, grep, or make/config validation depending on file.

## Control Flow
Runs quickly in build/test discovery; prints a tag such as apparmor, exclude_graphdriver_btrfs, btrfs_noversion, libsubid/openpgp/seccomp/selinux capability, or fails when policy is violated.

## State and Persistence
No persistent state.

## Dependencies
Depends on shell plus relevant system headers/pkg-config packages or repository files.

## Integration Points
Used by Makefile/go test build tag selection and validation jobs.

## Risks and Edge Cases
Host-dependent output can change build coverage; missing headers silently exclude features.

## Test Signals
Signal is stdout tag or non-zero validation exit.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/hack/log-capitalized.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/hack/openpgp_tag.sh -->

# sources/cloud-native/cri-o/hack/openpgp_tag.sh

## Purpose
Small build/test helper that emits a Go build tag or validation signal based on host capability or repository policy.

## Important APIs, Types, and Functions
Shell script using pkg-config, cc preprocessor checks, grep, or make/config validation depending on file.

## Control Flow
Runs quickly in build/test discovery; prints a tag such as apparmor, exclude_graphdriver_btrfs, btrfs_noversion, libsubid/openpgp/seccomp/selinux capability, or fails when policy is violated.

## State and Persistence
No persistent state.

## Dependencies
Depends on shell plus relevant system headers/pkg-config packages or repository files.

## Integration Points
Used by Makefile/go test build tag selection and validation jobs.

## Risks and Edge Cases
Host-dependent output can change build coverage; missing headers silently exclude features.

## Test Signals
Signal is stdout tag or non-zero validation exit.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/hack/openpgp_tag.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/hack/seccomp_tag.sh -->

# sources/cloud-native/cri-o/hack/seccomp_tag.sh

## Purpose
Small build/test helper that emits a Go build tag or validation signal based on host capability or repository policy.

## Important APIs, Types, and Functions
Shell script using pkg-config, cc preprocessor checks, grep, or make/config validation depending on file.

## Control Flow
Runs quickly in build/test discovery; prints a tag such as apparmor, exclude_graphdriver_btrfs, btrfs_noversion, libsubid/openpgp/seccomp/selinux capability, or fails when policy is violated.

## State and Persistence
No persistent state.

## Dependencies
Depends on shell plus relevant system headers/pkg-config packages or repository files.

## Integration Points
Used by Makefile/go test build tag selection and validation jobs.

## Risks and Edge Cases
Host-dependent output can change build coverage; missing headers silently exclude features.

## Test Signals
Signal is stdout tag or non-zero validation exit.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/hack/seccomp_tag.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/hack/selinux_tag.sh -->

# sources/cloud-native/cri-o/hack/selinux_tag.sh

## Purpose
Small build/test helper that emits a Go build tag or validation signal based on host capability or repository policy.

## Important APIs, Types, and Functions
Shell script using pkg-config, cc preprocessor checks, grep, or make/config validation depending on file.

## Control Flow
Runs quickly in build/test discovery; prints a tag such as apparmor, exclude_graphdriver_btrfs, btrfs_noversion, libsubid/openpgp/seccomp/selinux capability, or fails when policy is violated.

## State and Persistence
No persistent state.

## Dependencies
Depends on shell plus relevant system headers/pkg-config packages or repository files.

## Integration Points
Used by Makefile/go test build tag selection and validation jobs.

## Risks and Edge Cases
Host-dependent output can change build coverage; missing headers silently exclude features.

## Test Signals
Signal is stdout tag or non-zero validation exit.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/hack/selinux_tag.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/hack/tree_status.sh -->

# sources/cloud-native/cri-o/hack/tree_status.sh

## Purpose
CRI-O hack helper script.

## Important APIs, Types, and Functions
Shell commands and repo helper functions.

## Control Flow
Runs as a small validation/build step.

## State and Persistence
Minimal or no state.

## Dependencies
Shell and repository tooling.

## Integration Points
Used by make/CI.

## Risks and Edge Cases
Host/tooling dependent.

## Test Signals
Exit status is the signal.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/hack/tree_status.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/hack/validate-config.sh -->

# sources/cloud-native/cri-o/hack/validate-config.sh

## Purpose
Small build/test helper that emits a Go build tag or validation signal based on host capability or repository policy.

## Important APIs, Types, and Functions
Shell script using pkg-config, cc preprocessor checks, grep, or make/config validation depending on file.

## Control Flow
Runs quickly in build/test discovery; prints a tag such as apparmor, exclude_graphdriver_btrfs, btrfs_noversion, libsubid/openpgp/seccomp/selinux capability, or fails when policy is violated.

## State and Persistence
No persistent state.

## Dependencies
Depends on shell plus relevant system headers/pkg-config packages or repository files.

## Integration Points
Used by Makefile/go test build tag selection and validation jobs.

## Risks and Edge Cases
Host-dependent output can change build coverage; missing headers silently exclude features.

## Test Signals
Signal is stdout tag or non-zero validation exit.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/hack/validate-config.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/annotations/annotations.go -->

# sources/cloud-native/cri-o/internal/annotations/annotations.go

## Purpose
Central constants package for CRI-O runtime annotations stored on containers/sandboxes.

## Important APIs, Types, and Functions
Exports string constants for Kubernetes/CRI-O metadata such as ContainerID, ContainerName, ContainerType, image refs/names/digests, pod namespace/name, paths, runtime handler, IO flags, volumes, host network, CNI result, and ContainerManager; also ContainerTypeSandbox/ContainerTypeContainer and ContainerManagerLibpod.

## Control Flow
No runtime control flow; importing packages use the constants to set/read annotations consistently.

## State and Persistence
Annotations are persisted in OCI/runtime metadata by callers; this file itself has no state.

## Dependencies
No external deps.

## Integration Points
Integrates container creation, restore, checkpoint, inspection, and metadata consumers across CRI-O.

## Risks and Edge Cases
Changing constants breaks compatibility with stored containers and external tools.

## Test Signals
Compile-time usage; tests are indirect through runtime metadata behavior.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/annotations/annotations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/annotations/checkpoint.go -->

# sources/cloud-native/cri-o/internal/annotations/checkpoint.go

## Purpose
Constants for annotations embedded in container checkpoint images.

## Important APIs, Types, and Functions
Exports CheckpointAnnotationName, RawImageName, RootfsImageID, RootfsImageName, CRIOVersion, and CriuVersion.

## Control Flow
No control flow.

## State and Persistence
Values are persisted in checkpoint image metadata by checkpoint code.

## Dependencies
No external deps.

## Integration Points
Used by checkpoint/restore image creation and consumers.

## Risks and Edge Cases
Renaming breaks checkpoint compatibility.

## Test Signals
Indirect checkpoint/restore tests validate it.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/annotations/checkpoint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/cert/cert.go -->

# sources/cloud-native/cri-o/internal/cert/cert.go

## Purpose
TLS certificate configuration and hot-reload support for CRI-O metrics/streaming endpoints.

## Important APIs, Types, and Functions
Config holds tls.Config under RWMutex plus cert/key/CA paths, min TLS version, ciphers. NewCertConfig loads certs, creates fsnotify watcher, reloads on file events, closes on doneChan. GetConfigForClient returns current config. reload validates key pair dates and optional client CA mTLS. GenerateSelfSignedCertKey creates cert/key if both absent.

## Control Flow
Initial load must succeed; watcher goroutines monitor cert/key/CA files and swap tls.Config atomically on successful reload while retaining previous config on errors. Self-signed generation only occurs when both cert and key are missing.

## State and Persistence
Persists generated cert/key files with 0700 dirs and 0600 files; in-memory tls.Config is protected by mutex.

## Dependencies
Depends on crypto/tls/x509, fsnotify, client-go cert.GenerateSelfSignedCertKey, filesystem, internal log.

## Integration Points
Integrated with CRI-O TLS-enabled metrics/streaming server via GetConfigForClient callback.

## Risks and Edge Cases
Fatal on watcher.Add failures inside goroutine; CA AppendCertsFromPEM return is not checked; if only one of cert/key missing generation does nothing; reload on every fs event can duplicate work.

## Test Signals
Signals are successful config load, cert date logs, fsnotify reload logs, and TLS client/server behavior; direct tests not in subset.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/cert/cert.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/client/client.go -->

# sources/cloud-native/cri-o/internal/client/client.go

## Purpose
HTTP client for CRI-O daemon debug/info endpoints over a Unix socket.

## Important APIs, Types, and Functions
CrioClient interface exposes DaemonInfo, ContainerInfo, ConfigInfo, GoRoutinesInfo, HeapInfo. New configures http.Transport DialContext to unix socket with path length check. doGetRequest issues GET and reads response. Methods target server info/config/goroutines/heap/container paths and JSON-decode typed results where needed.

## Control Flow
Caller creates client for socket path, each method builds GET request with context, reads body, checks status, and decodes or returns strings/bytes.

## State and Persistence
No persistent state except reusable http.Client and socket path.

## Dependencies
Depends on net/http over Unix sockets, syscall path size, pkg/types, server endpoint constants.

## Integration Points
Used by crio status/debug tooling and tests needing daemon introspection.

## Risks and Edge Cases
No response size limits; no client timeout except dial timeout; path length limit is platform-specific; errors include raw body/status behavior depending implementation.

## Test Signals
Indirect tests through CLI/debug endpoint usage; socket path validation is a direct signal.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/client/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/apparmor/apparmor_linux.go -->

# sources/cloud-native/cri-o/internal/config/apparmor/apparmor_linux.go

## Purpose
Linux AppArmor configuration helper for loading and applying CRI-O AppArmor profiles.

## Important APIs, Types, and Functions
Config has default profile state. New initializes DefaultProfile. LoadProfile loads named profile, handles default reload via reloadDefaultProfile, and tracks disabled/enabled. IsEnabled reports host support. Apply maps CRI security context profile strings to OCI AppArmor profile output, including runtime/default/unconfined semantics.

## Control Flow
On startup/config load it checks host AppArmor support and loads configured profile; per-container Apply evaluates security context and returns profile name or empty string.

## State and Persistence
Kernel AppArmor profile state is mutated by loading/reloading; Config holds enabled/profile values.

## Dependencies
Depends on apparmor parser/library, runtimeapi LinuxContainerSecurityContext, host AppArmor filesystem.

## Integration Points
Integrated with CRI-O config and container spec generation.

## Risks and Edge Cases
Host support and parser availability drive behavior; unsupported profiles fail container setup; default reload can affect global host policy.

## Test Signals
apparmor_test.go covers enabled/disabled/load/apply cases on supported platforms.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/apparmor/apparmor_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/apparmor/apparmor_test.go -->

# sources/cloud-native/cri-o/internal/config/apparmor/apparmor_test.go

## Purpose
Ginkgo/Gomega tests for Linux AppArmor config behavior.

## Important APIs, Types, and Functions
Specs exercise New, LoadProfile, IsEnabled, and Apply behavior for default, localhost, runtime/default, unconfined, and invalid profiles.

## Control Flow
Test framework creates temp fixtures and asserts returned profile/errors.

## State and Persistence
Uses temporary files and host AppArmor availability assumptions through package behavior.

## Dependencies
Depends on Ginkgo/Gomega and CRI-O test framework.

## Integration Points
Validates apparmor_linux.go behavior.

## Risks and Edge Cases
Tests may be host-feature-sensitive if AppArmor is absent.

## Test Signals
RunFrameworkSpecs suite is the signal.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/apparmor/apparmor_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/apparmor/apparmor_unsupported.go -->

# sources/cloud-native/cri-o/internal/config/apparmor/apparmor_unsupported.go

## Purpose
Unsupported-platform AppArmor stub.

## Important APIs, Types, and Functions
Defines DefaultProfile, Config, New, LoadProfile and likely no-op/disabled behavior for non-Linux or no_apparmor builds.

## Control Flow
Calls return disabled/no-op behavior so callers can compile without AppArmor.

## State and Persistence
No state beyond Config fields.

## Dependencies
Build tags select this file when Linux AppArmor implementation is unavailable.

## Integration Points
Keeps config package portable.

## Risks and Edge Cases
Feature silently unavailable on unsupported builds.

## Test Signals
Compile-only/unsupported platform tests validate it.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/apparmor/apparmor_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/apparmor/suite_test.go -->

# sources/cloud-native/cri-o/internal/config/apparmor/suite_test.go

## Purpose
Ginkgo suite bootstrap for AppArmor config tests.

## Important APIs, Types, and Functions
TestLibConfig registers fail handler and RunFrameworkSpecs; BeforeSuite creates TestFramework; AfterSuite tears down.

## Control Flow
Standard suite lifecycle.

## State and Persistence
Temporary test framework state.

## Dependencies
Depends on test/framework, Ginkgo, Gomega.

## Integration Points
Supports apparmor_test.go.

## Risks and Edge Cases
Failures in setup affect all specs.

## Test Signals
go test invokes suite.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/apparmor/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/blockio/blockio.go -->

# sources/cloud-native/cri-o/internal/config/blockio/blockio.go

## Purpose
BlockIO config loader wrapping Intel goresctrl blockio configuration.

## Important APIs, Types, and Functions
Config tracks enabled, reload flag, cleaned path, and *blockio.Config. New initializes empty config. Enabled, SetReload, ReloadRequired are accessors. Reload reads YAML path, unmarshals into blockio.Config, calls blockio.SetConfig(tmpCfg,true), and stores it. Load resets state, cleans path, reloads, logs, and enables.

## Control Flow
Load with empty path disables blockio. Load with path reads/validates/applies immediately. Reload re-reads stored path and rescans devices.

## State and Persistence
Holds in-memory config/path/reload flags; blockio.SetConfig mutates global goresctrl blockio state and scans host devices.

## Dependencies
Depends on os, sigs.k8s.io/yaml, github.com/intel/goresctrl/pkg/blockio, logrus.

## Integration Points
Integrated with CRI-O config reload and workload class assignment.

## Risks and Edge Cases
Invalid YAML leaves enabled false; Reload after path set can partially affect global blockio before error depending library; host device topology matters.

## Test Signals
blockio_test.go covers empty/new, missing file, invalid schema, and valid config.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/blockio/blockio.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/blockio/blockio_test.go -->

# sources/cloud-native/cri-o/internal/config/blockio/blockio_test.go

## Purpose
Tests for BlockIO config Load/New behavior.

## Important APIs, Types, and Functions
tempFileWithData helper; specs assert New disabled, missing file errors/disabled, invalid format errors/disabled, valid classes enable config.

## Control Flow
Creates temp files then calls Config.Load.

## State and Persistence
Writes temp YAML files.

## Dependencies
Depends on Ginkgo/Gomega/test framework and goresctrl validation.

## Integration Points
Validates blockio.go core paths.

## Risks and Edge Cases
Valid config test may depend on library schema compatibility.

## Test Signals
go test suite is signal.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/blockio/blockio_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/blockio/suite_test.go -->

# sources/cloud-native/cri-o/internal/config/blockio/suite_test.go

## Purpose
Ginkgo suite bootstrap for BlockIO tests.

## Important APIs, Types, and Functions
Registers fail handler, RunFrameworkSpecs, BeforeSuite/AfterSuite TestFramework.

## Control Flow
Standard test lifecycle.

## State and Persistence
Temp framework state.

## Dependencies
Depends on test/framework.

## Integration Points
Supports blockio_test.go.

## Risks and Edge Cases
Setup failure fails suite.

## Test Signals
go test invokes suite.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/blockio/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/capabilities/capabilities_linux.go -->

# sources/cloud-native/cri-o/internal/config/capabilities/capabilities_linux.go

## Purpose
Linux default capability list and validator.

## Important APIs, Types, and Functions
Capabilities []string type, Default returns baseline CHOWN, DAC_OVERRIDE, FSETID, FOWNER, SETGID, SETUID, SETPCAP, NET_BIND_SERVICE, KILL. Validate uppercases/prefixes CAP_ and calls common.ValidateCapabilities.

## Control Flow
Callers get defaults or validate configured list before runtime use.

## State and Persistence
No persistent state.

## Dependencies
Depends on go.podman.io/common/pkg/capabilities and logrus.

## Integration Points
Integrated with CRI-O runtime default capabilities config.

## Risks and Edge Cases
Kernel/libcap support and spelling drive validation; logging shows normalized CAP_ names.

## Test Signals
capabilities_test.go covers default and validation behavior.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/capabilities/capabilities_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/capabilities/capabilities_test.go -->

# sources/cloud-native/cri-o/internal/config/capabilities/capabilities_test.go

## Purpose
Tests for capabilities defaults and validation.

## Important APIs, Types, and Functions
Ginkgo specs assert default list and Validate success/failure for known/unknown capabilities.

## Control Flow
Calls package functions directly.

## State and Persistence
No state.

## Dependencies
Depends on Ginkgo/Gomega and host/common capabilities validator.

## Integration Points
Validates capabilities_linux.go.

## Risks and Edge Cases
Unknown capabilities should fail consistently; host capability set may vary in edge cases.

## Test Signals
go test suite is signal.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/capabilities/capabilities_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/capabilities/capabilities_unsupported.go -->

# sources/cloud-native/cri-o/internal/config/capabilities/capabilities_unsupported.go

## Purpose
Unsupported-platform capabilities stub.

## Important APIs, Types, and Functions
Defines Capabilities, Default, and Validate with reduced/no-op behavior for unsupported builds.

## Control Flow
Lets callers compile when Linux capability validation is unavailable.

## State and Persistence
No state.

## Dependencies
Build tags select it off Linux or without capabilities support.

## Integration Points
Keeps config package portable.

## Risks and Edge Cases
May accept fewer validations on unsupported platforms.

## Test Signals
Compile tests validate it.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/capabilities/capabilities_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/capabilities/suite_test.go -->

# sources/cloud-native/cri-o/internal/config/capabilities/suite_test.go

## Purpose
Ginkgo suite bootstrap for capabilities tests.

## Important APIs, Types, and Functions
Registers fail handler and TestFramework lifecycle.

## Control Flow
Standard suite lifecycle.

## State and Persistence
Temp framework state.

## Dependencies
Depends on Ginkgo/Gomega/test framework.

## Integration Points
Supports capabilities_test.go.

## Risks and Edge Cases
Setup failure affects specs.

## Test Signals
go test invokes suite.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/capabilities/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/cgmgr/cgmgr_linux.go -->

# sources/cloud-native/cri-o/internal/config/cgmgr/cgmgr_linux.go

## Purpose
Linux cgroup manager abstraction and shared helpers for CRI-O cgroupfs/systemd support.

## Important APIs, Types, and Functions
Defines CgroupManager interface, constants for manager names/defaults/memory paths, New, SetCgroupManager, verifyCgroupHasEnoughMemory, VerifyMemoryIsEnough, MoveProcessToContainerCgroup, create/removeSandboxCgroup, containerCgroupPath, LibctrManager, crunContainerCgroupManager, execCgroupManager.

## Control Flow
Startup selects systemd by default or cgroupfs; helpers create libcontainer managers, verify memory limits, move exec processes, create empty sandbox cgroups, account for crun child cgroups, and build exec cgroups for cgroup v2.

## State and Persistence
Caches/manages cgroups indirectly via libcontainer; writes cgroup.procs and cpuset.sched_load_balance; reads memory limit files.

## Dependencies
Depends on opencontainers/cgroups manager/systemd, runtime-spec resources, node cgroup detection, internal stats, filesystem under /sys/fs/cgroup.

## Integration Points
Core integration point between CRI-O server, conmon placement, runtime specs, cAdvisor/pod metrics, and exec CgroupFD support.

## Risks and Edge Cases
Cgroup v1/v2 differences, systemd/cgroupfs path conversion, memory file absence, crun hardcoded child path, and direct /proc writes are high-risk compatibility areas.

## Test Signals
cgmgr_test.go covers selection/path helpers; runtime/e2e tests validate real cgroup behavior.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/cgmgr/cgmgr_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/cgmgr/cgmgr_test.go -->

# sources/cloud-native/cri-o/internal/config/cgmgr/cgmgr_test.go

## Purpose
Tests for cgroup manager selection, naming, paths, memory validation, and manager behavior.

## Important APIs, Types, and Functions
Ginkgo specs create default/systemd/cgroupfs managers and assert SetCgroupManager, Name, cgroup paths, sandbox path validation, memory minimum checks, and unsupported inputs.

## Control Flow
Direct unit-style calls into cgmgr package.

## State and Persistence
May touch temp paths or rely on host cgroup mode for selected branches.

## Dependencies
Depends on Ginkgo/Gomega and cgmgr package.

## Integration Points
Validates cgmgr_linux.go plus manager implementations.

## Risks and Edge Cases
Host cgroup version can affect expectations; tests focus on deterministic helper behavior where possible.

## Test Signals
go test suite is signal.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/cgmgr/cgmgr_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/cgmgr/cgmgr_unsupported.go -->

# sources/cloud-native/cri-o/internal/config/cgmgr/cgmgr_unsupported.go

## Purpose
Unsupported-platform cgroup manager stub.

## Important APIs, Types, and Functions
Defines CgroupManager interface subset, NullCgroupManager, Set/New, MoveProcessToContainerCgroup, VerifyMemoryIsEnough and no-op methods for unsupported builds.

## Control Flow
Unsupported builds return null manager behavior or unsupported errors.

## State and Persistence
No real cgroup state.

## Dependencies
Build tags select this file outside Linux.

## Integration Points
Allows non-Linux compilation of packages that reference cgmgr.

## Risks and Edge Cases
Runtime cgroup functionality unavailable; method signatures must match Linux interface expectations.

## Test Signals
Compile tests on unsupported platforms are signal.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/cgmgr/cgmgr_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/cgmgr/cgroupfs_linux.go -->

# sources/cloud-native/cri-o/internal/config/cgmgr/cgroupfs_linux.go

## Purpose
cgroupfs implementation of CgroupManager.

## Important APIs, Types, and Functions
CgroupfsManager stores memory path/file, v1 container/sandbox manager caches, mutex. Implements Name, IsSystemd, ContainerCgroupPath/AbsolutePath/Manager/Stats/Remove, SandboxCgroupPath/Manager/Stats/Remove, MoveConmonToCgroup, applyWorkloadSettings, Create/RemoveSandboxCgroup, PodAndContainerCgroupManagers, ExecCgroupManager.

## Control Flow
Builds cgroupfs paths under /crio or provided parent, rejects systemd slices, verifies memory, caches v1 managers, applies conmon CPU resources via libcontainer, creates/removes sandbox cgroups, returns pod/container managers plus optional crun child, and creates exec cgroup on v2.

## State and Persistence
Mutates cgroupfs hierarchy, cgroup manager caches, and conmon process placement; reads cgroup memory files.

## Dependencies
Depends on opencontainers/cgroups, storage unshare, runtime-spec resources, node cgroup mode, utils.PodCgroupName.

## Integration Points
Used when CRI-O configured with cgroup_manager=cgroupfs, including critest.yml.

## Risks and Edge Cases
Path handling prepends slashes intentionally; v1 cache invalidation must be called; exec cgroup unsupported on v1; conmonCgroup accepts only pod/empty.

## Test Signals
Validated indirectly by cgmgr tests and integration/critest cgroupfs runs.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/cgmgr/cgroupfs_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/cgmgr/stats_linux.go -->

# sources/cloud-native/cri-o/internal/config/cgmgr/stats_linux.go

## Purpose
Process/cgroup stats conversion helpers.

## Important APIs, Types, and Functions
statsFromLibctrMgr obtains libcontainer stats and converts to internal stats. cgroupProcessStats aggregates pid count, file descriptor count, socket count, and ulimit count. addFdsForProcess reads /proc/<pid>/fd links and counts sockets; addUlimitsForProcess parses /proc/<pid>/limits.

## Control Flow
Stats path calls manager.GetStats, iterates pids, reads proc files, and builds CRI-O stats structures.

## State and Persistence
Reads /proc and cgroup stats; no persistence.

## Dependencies
Depends on opencontainers/cgroups stats and internal/lib/stats structures, os/readlink parsing.

## Integration Points
Feeds CRI-O metrics/status reporting for pod/container cgroups.

## Risks and Edge Cases
Processes can exit while reading; permission errors or proc races may undercount; parsing /proc/limits is format-sensitive.

## Test Signals
Runtime metrics tests and stats consumers validate behavior.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/cgmgr/stats_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/cgmgr/suite_test.go -->

# sources/cloud-native/cri-o/internal/config/cgmgr/suite_test.go

## Purpose
Ginkgo suite bootstrap for cgmgr tests.

## Important APIs, Types, and Functions
Registers fail handler and TestFramework lifecycle.

## Control Flow
Standard suite lifecycle.

## State and Persistence
Temp framework state.

## Dependencies
Depends on Ginkgo/Gomega/test framework.

## Integration Points
Supports cgmgr_test.go.

## Risks and Edge Cases
Setup failure affects specs.

## Test Signals
go test invokes suite.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/cgmgr/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/cgmgr/systemd_linux.go -->

# sources/cloud-native/cri-o/internal/config/cgmgr/systemd_linux.go

## Purpose
systemd implementation of CgroupManager.

## Important APIs, Types, and Functions
SystemdManager stores memory path/file, v1 caches, dbus manager, mutex. Implements Name, IsSystemd, ContainerCgroupPath/AbsolutePath/Manager/Stats/Remove, MoveConmonToCgroup, SandboxCgroupPath/Manager/Stats/Remove, sandboxCgroupAbsolutePath, convertCgroupFsNameToSystemd, Create/RemoveSandboxCgroup, PodAndContainerCgroupManagers, ExecCgroupManager.

## Control Flow
Builds systemd scope paths of form slice:crio:id, expands slices for filesystem paths, runs conmon under systemd scope with KillSignal/After and CPU properties, verifies memory, caches v1 managers, creates cgroupfs child sandbox cgroups for dropped infra/cAdvisor needs, and translates systemd cgroup path for exec cgroup v2.

## State and Persistence
Mutates systemd units/scopes over D-Bus and cgroupfs children, caches v1 managers, reads memory files.

## Dependencies
Depends on go-systemd/dbus, opencontainers cgroups/systemd, dbusmgr, node feature detection, unshare/rootless mode, runtime-spec resources.

## Integration Points
Default CRI-O cgroup manager and main bridge to kubelet systemd slice parents and conmon lifecycle.

## Risks and Edge Cases
Requires valid .slice parent; systemd AllowedCPUs support is conditional; D-Bus/rootless behavior can fail; child cgroup creation deliberately bypasses systemd ownership.

## Test Signals
cgmgr tests and e2e/runtime tests validate behavior.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/cgmgr/systemd_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/cnimgr/cnimgr.go -->

# sources/cloud-native/cri-o/internal/config/cnimgr/cnimgr.go

## Purpose
CNI manager that gates pod networking on CNI plugin readiness, monitors health, notifies waiters, and defers GC until ready.

## Important APIs, Types, and Functions
Types: PodNetworkLister, CNIManager, errShutdown. New initializes ocicni plugin and poll goroutine. pollUntilReady, pollContinuously, statusPollFunc handle startup and continuous status. ReadyOrError, Plugin, AddWatcher, Shutdown, GC, doGC expose readiness/plugin lifecycle.

## Control Flow
Startup polls every 500ms until StatusWithContext succeeds, then clears lastError, runs deferred GC, and notifies watchers. Optional continuous monitoring polls every 5s and applies gracePeriod before marking unhealthy. Shutdown cancels context and notifies pending watchers false. GC stores validPodList and runs immediately only when ready.

## State and Persistence
In-memory mutable state protected by RWMutex: lastError, watcher channels, firstFailureTime, validPodList. External state is CNI plugin resources cleaned by GC.

## Dependencies
Depends on github.com/cri-o/ocicni, Kubernetes wait utilities, context/time, logrus.

## Integration Points
Used by CRI-O server to report NetworkReady, block pod creation until CNI ready, expose plugin operations, and clean stale pod network resources.

## Risks and Edge Cases
Watcher channels can receive true right before shutdown by design; continuous monitoring disabled when gracePeriod<=0; health depends on plugin StatusWithContext implementation; GC valid list errors defer cleanup failure.

## Test Signals
cnimgr_test.go exists outside this subset and covers status polling, watchers, shutdown, GC, and grace period behavior.

<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/cnimgr/cnimgr.go -->
