# sources/cloud-native/containerd/.github/workflows/node-e2e.yml

## Purpose
This reusable workflow runs Kubernetes node e2e tests against a freshly built containerd.

## Important APIs, Types, And Functions
It is invoked with `workflow_call` and optional `k8s_version` defaulting to `master`. It checks out containerd and Kubernetes, installs Go, installs seccomp/runc/CNI, builds and installs containerd, writes a CRI config, starts systemd `containerd`, then runs `make test-e2e-node` with focused/skipped test regexes and kubelet flags.

## Control Flow
The job first frees disk space, checks out both repositories, disables swap, installs dependencies, builds/installs containerd, configures CRI runtimes for runc and `test-handler`, verifies `ctr version`, runs node e2e, and on failure collects kubelet/containerd logs and uploads them.

## State And Persistence
Runner state includes installed containerd service, Kubernetes checkout, generated `/etc/containerd/config.toml`, and failure artifacts.

## Dependencies And Integration Points
It integrates containerd with Kubernetes node conformance, systemd, runc, CNI plugins, and GitHub reusable workflow callers such as `ci.yml`.

## Risks
Testing against Kubernetes `master` is intentionally high-signal but can introduce upstream breakage unrelated to containerd. Disk pressure is managed by deleting many preinstalled toolchains. The skip/focus regex controls coverage and must be maintained as Kubernetes tests evolve.

## Test Signals
Passing node e2e and, on failure, uploaded kubelet/containerd logs are the relevant signals.
