# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/spec.go

## Purpose
This file generates Kubernetes Deployment, Pod, PVC, and floating monitor resources for Ceph monitors. It is the main monitor spec construction layer, translating `CephCluster` monitor/network/storage/security/logging settings into Kubernetes workload definitions and Ceph daemon command lines.

## Important APIs, Types, And Functions
Key constants are `cephMonCommand` and `monContainerName`. `getLabels()` returns legacy and app labels plus optional PVC/zone/daemon labels. `GetFailureDomainLabel()` and `getFailureDomainName()` choose topology labels for zone or stretch cluster placement. `makeDeployment()`, `makeDeploymentPVC()`, and `makeMonPod()` build normal monitor resources. `makeChownInitContainer()`, `makeMonFSInitContainer()`, and `makeMonDaemonContainer()` build containers. Floating monitor support is implemented by `makeFloatingMonDeployment()`, `buildFloatingMonTemplateParams()`, `floatingMonMsgr2Value()`, `floatingMonTemplateToDeployment()`, and `renderFloatingMonTemplate()`. `UpdateCephDeploymentAndWait()` wraps deployment update gating with Ceph ok-to-stop/ok-to-continue checks.

## Control Flow And State
Normal deployment generation creates metadata, version/Ceph labels, owner refs, pod template, a single replica, and recreate strategy. Pod generation starts with chown and mkfs init containers, a mon daemon container, base volumes, service account, host network flag, priority class, and security context. It adds a log collector sidecar when enabled, PVC-specific unreachable-node toleration, host-network DNS policy, Multus annotations, and zone affinity when required. PVC generation applies the selected zone/default volume claim template and injects a default storage request when neither a request nor a limit is configured.

The mon daemon command always includes daemon flags, foreground mode, `--public-addr`, and `--setuser-match-path`. If the monitor is msgr2-only, it disables msgr1 and computes a bind address with IPv4/IPv6/dual-stack rules. Host-network monitors skip `--public-bind-addr`. Zone-aware monitors receive `--set-crush-location`, and arbiter zone selection records `c.arbiterMon` for later reconciliation. Probe specs are generated then overwritten by cluster health-check configuration if provided.

Floating monitor generation uses embedded DRBD YAML instead of the normal pod builder. It builds a stateful data path, merges ConfigMap parameters with built-ins, renders the template, applies owner refs/labels/annotations, and then patches resource requirements into named containers.

## Dependencies And Integration Points
This file depends on the CephCluster API, Rook controller helpers for labels, volumes, env vars, probes, and deployment updates, Kubernetes API types, embedded templates, text/template, YAML decoding, Ceph version labels, and environment variables such as the operator namespace. It integrates with monitor startup, scheduling, storage selection, log collection, network providers, stretch cluster placement, and upgrade orchestration.

## Risks And Test Signals
High-risk areas include immutable deployment selectors, host vs pod networking address selection, msgr2-only binding on IPv6/dual-stack, PVC defaults, zone affinity, arbiter location configuration, template rendering, and privileged DRBD floating monitor behavior. `spec_test.go` covers pod/deployment resource and label expectations, PVC defaults, failure-domain labels, run-as-root env handling, probes, and msgr2 bind variants. `mon_test.go` adds floating monitor parameter, label, scheduling, and update-path coverage. Residual risk remains around actual scheduler behavior, Multus runtime behavior, and DRBD mount/demote correctness because tests use fake clients and rendered object inspection.
