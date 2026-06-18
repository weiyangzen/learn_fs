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
