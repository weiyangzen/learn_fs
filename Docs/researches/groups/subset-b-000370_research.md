# Research Group subset-b-000370

Grouped research report for subset B item `subset-b-000370`. Each section preserves the original source path and is bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.7.0/csi-smb-node-windows.yaml -->

# sources/control-plane/csi-driver-smb/deploy/v1.7.0/csi-smb-node-windows.yaml

## Purpose
Windows DaemonSet for the v1.7.0 SMB CSI node plugin. It deploys the liveness sidecar, node-driver-registrar, and `smbplugin:v1.7.0` on Windows nodes.

## Important APIs, Types, and Functions
Defines an `apps/v1` DaemonSet named `csi-smb-node-win` in `kube-system`, with Windows node selector, `csi-smb-node-sa`, plugin socket at `C:\csi\csi.sock`, kubelet registration path, health port `29643`, and CSI proxy filesystem/SMB pipe hostPaths for v1 and v1beta1.

## Control Flow
Kubernetes schedules one pod per Windows node. The SMB container starts with endpoint, node ID, and metrics address flags. The registrar registers the Windows kubelet plugin socket, and the liveness probe checks the CSI endpoint through the health endpoint.

## State and Persistence
Persistent host state lives under `C:\var\lib\kubelet\plugins\smb.csi.k8s.io\`, `plugins_registry`, and CSI proxy named pipes. Rolling updates permit one unavailable node pod.

## Dependencies
Depends on Windows kubelet layout, CSI proxy named pipes, `registry.k8s.io/sig-storage/livenessprobe:v2.6.0`, `csi-node-driver-registrar:v2.5.0`, and `smbplugin:v1.7.0`.

## Integration Points
Integrates with kubelet CSI registration, Windows CSI proxy filesystem and SMB APIs, node identity injection through `spec.nodeName`, and RBAC from `rbac-csi-smb.yaml`.

## Risks and Edge Cases
Missing CSI proxy pipes or host directories prevent startup. Both v1 and v1beta1 pipes are mounted for compatibility, increasing deployment assumptions. Windows socket path escaping is fragile.

## Test Signals
Signals are DaemonSet rollout, registrar liveness probe, `/healthz` success on `29643`, successful CSINode registration, and SMB mount operations on Windows nodes.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.7.0/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.7.0/csi-smb-node.yaml -->

# sources/control-plane/csi-driver-smb/deploy/v1.7.0/csi-smb-node.yaml

## Purpose
Linux DaemonSet for the v1.7.0 SMB CSI node plugin. It runs the node CSI service, liveness sidecar, and kubelet registrar on every Linux node.

## Important APIs, Types, and Functions
Defines `csi-smb-node` with host networking, Linux node selector, system-node-critical priority, privileged `smb` container, CSI socket hostPath, kubelet mountpoint hostPath with bidirectional mount propagation, and plugins registry hostPath.

## Control Flow
The SMB container serves CSI over `/csi/csi.sock`; the registrar exposes `/var/lib/kubelet/plugins/smb.csi.k8s.io/csi.sock` to kubelet. Kubelet then calls NodeStage/Publish methods for SMB volumes.

## State and Persistence
Persists the plugin socket and kubelet volume mounts under `/var/lib/kubelet`. The pod itself has no app data, but it manipulates host mounts through privileged mode and mount propagation.

## Dependencies
Depends on Linux CIFS mount support, kubelet plugin paths, `livenessprobe:v2.6.0`, `csi-node-driver-registrar:v2.5.0`, and `smbplugin:v1.7.0`.

## Integration Points
Integrates with kubelet CSI registration, node-local mount namespace, host networking/DNS policy, and node service account permissions.

## Risks and Edge Cases
Privileged host mount access has high blast radius. HostNetwork plus `dnsPolicy: Default` may affect SMB DNS behavior. Missing CIFS support or kubelet path drift causes runtime mount failures.

## Test Signals
Rollout, registrar liveness, `/healthz`, CSINode driver entry, and successful SMB volume stage/publish are primary signals.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.7.0/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.7.0/rbac-csi-smb.yaml -->

# sources/control-plane/csi-driver-smb/deploy/v1.7.0/rbac-csi-smb.yaml

## Purpose
RBAC and service accounts for the v1.7.0 SMB CSI controller and node components.

## Important APIs, Types, and Functions
Creates `csi-smb-controller-sa`, `csi-smb-node-sa`, `smb-external-provisioner-role`, and `smb-csi-provisioner-binding`. The role covers PV/PVC watch and mutation, StorageClass read, events, CSINodes, nodes, leader-election leases, and secret get.

## Control Flow
After apply, the controller service account can run external-provisioner workflows and retrieve secrets needed for dynamic provisioning. Node service account is defined for DaemonSets but no binding is present in this file.

## State and Persistence
Persists cluster-scoped RBAC objects. No runtime state beyond Kubernetes RBAC policy.

## Dependencies
Requires Kubernetes RBAC, coordination leases, storage APIs, and namespace `kube-system`.

## Integration Points
Used by controller and node manifests in the same release folder. Secret access supports SMB credentials in CSI Create/Delete paths.

## Risks and Edge Cases
Secret `get` is cluster role scoped when bound to the controller account, so namespace boundaries rely on provisioner request context. Node account has no explicit permissions here.

## Test Signals
`kubectl auth can-i` for controller operations, successful external-provisioner leader election, PVC provisioning, events, and secret retrieval.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.7.0/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.8.0/csi-smb-controller.yaml -->

# sources/control-plane/csi-driver-smb/deploy/v1.8.0/csi-smb-controller.yaml

## Purpose
Controller Deployment for SMB CSI v1.8.0. It runs external-provisioner, liveness probe, and the controller-capable SMB CSI process.

## Important APIs, Types, and Functions
Defines `apps/v1` Deployment `csi-smb-controller`, one replica, Linux node selector, control-plane tolerations, `csi-provisioner:v3.2.0`, `livenessprobe:v2.7.0`, and `smbplugin:v1.8.0`.

## Control Flow
The provisioner talks to the SMB CSI socket at `/csi/csi.sock` and performs leader-elected Create/DeleteVolume workflows. The SMB container exposes health port `29642` and metrics port `29644`.

## State and Persistence
Uses `emptyDir` for the internal controller socket. Cluster state is created through PV/PVC provisioning, events, and leases; no controller-local persistence survives pod restart.

## Dependencies
Depends on controller RBAC, Linux scheduling, sidecar images, the SMB CSI controller server, and kube-system leader-election leases.

## Integration Points
Pairs with `csi-smb-driver.yaml`, node DaemonSets, storage classes, and external-provisioner metadata injection.

## Risks and Edge Cases
Single replica relies on restart/leader election for availability. The SMB container is privileged even in the controller pod. Resource requests are small relative to provisioning bursts.

## Test Signals
Deployment rollout, liveness endpoint, provisioner leader-election lease, PVC provisioning/deletion, and metrics scraping on `29644`.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.8.0/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.8.0/csi-smb-driver.yaml -->

# sources/control-plane/csi-driver-smb/deploy/v1.8.0/csi-smb-driver.yaml

## Purpose
Kubernetes CSIDriver object for SMB CSI v1.8.0.

## Important APIs, Types, and Functions
Defines `storage.k8s.io/v1` `CSIDriver` named `smb.csi.k8s.io` with `attachRequired: false` and `podInfoOnMount: true`.

## Control Flow
Kubernetes uses this object to skip attach/detach and pass pod metadata into NodePublish/NodeStage contexts for supported volume flows.

## State and Persistence
Persists a cluster-scoped CSIDriver registration object.

## Dependencies
Requires the storage.k8s.io v1 API and the node/controller deployments using the same driver name.

## Integration Points
Matches `DefaultDriverName` in Go code and the kubelet registration path in node manifests.

## Risks and Edge Cases
Name mismatch breaks volume routing. `podInfoOnMount` increases context data exposure but is needed for features that reference pod/PVC metadata.

## Test Signals
`kubectl get csidriver smb.csi.k8s.io`, CSINode entries, and successful volume scheduling without attach operations.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.8.0/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.8.0/csi-smb-node-windows.yaml -->

# sources/control-plane/csi-driver-smb/deploy/v1.8.0/csi-smb-node-windows.yaml

## Purpose
Windows node DaemonSet for SMB CSI v1.8.0.

## Important APIs, Types, and Functions
Same topology as v1.7.0 but updates sidecars to `livenessprobe:v2.7.0`, `csi-node-driver-registrar:v2.5.1`, and `smbplugin:v1.8.0`.

## Control Flow
Schedules on Windows nodes, exposes CSI socket under `C:\csi`, registers with kubelet, and connects the SMB container to CSI proxy filesystem/SMB pipes.

## State and Persistence
Host state remains in kubelet plugin, registry, and CSI proxy pipe paths. No SMB mapping cleanup flag is enabled in this version.

## Dependencies
Depends on Windows kubelet, CSI proxy v1 or v1beta1 named pipes, and v1.8.0 images.

## Integration Points
Integrates with v1.8.0 RBAC, CSIDriver, and Windows mounter implementations that can negotiate CSI proxy versions.

## Risks and Edge Cases
Compatibility with v1beta1 pipes is preserved but may hide CSI proxy upgrades. Global SMB mappings can outlive pod lifecycle depending on node unmount behavior.

## Test Signals
DaemonSet rollout, registrar probe, health endpoint, successful Windows staging/publishing, and CSI proxy pipe availability.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.8.0/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.8.0/csi-smb-node.yaml -->

# sources/control-plane/csi-driver-smb/deploy/v1.8.0/csi-smb-node.yaml

## Purpose
Linux node DaemonSet for SMB CSI v1.8.0.

## Important APIs, Types, and Functions
Defines hostNetwork Linux node pod with livenessprobe v2.7.0, registrar v2.5.1, `smbplugin:v1.8.0`, privileged mode, `/csi` socket, plugin registry, and bidirectional `/var/lib/kubelet` mount propagation.

## Control Flow
The pod registers the SMB driver with kubelet and handles node-stage/node-publish CSI requests through the SMB container.

## State and Persistence
Persists node CSI socket and host mount state under `/var/lib/kubelet`. No container-local data persistence.

## Dependencies
Depends on Linux CIFS tooling/kernel support, kubelet CSI directories, and v1.8.0 sidecars.

## Integration Points
Works with the v1.8.0 controller, CSIDriver, and Linux `SafeFormatAndMount` implementation.

## Risks and Edge Cases
Privileged mount access and bidirectional propagation are necessary but high risk. DNS policy and host networking can influence SMB service name resolution.

## Test Signals
Rollout, liveness, CSINode registration, and successful pod volume mounts.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.8.0/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.8.0/rbac-csi-smb.yaml -->

# sources/control-plane/csi-driver-smb/deploy/v1.8.0/rbac-csi-smb.yaml

## Purpose
RBAC for SMB CSI v1.8.0 controller and node identities.

## Important APIs, Types, and Functions
Creates the same service accounts, cluster role, and controller binding as v1.7.0, granting PV/PVC, StorageClass, event, CSINode, node, lease, and secret access.

## Control Flow
External-provisioner uses these permissions during provisioning, deletion, event recording, and leader election.

## State and Persistence
Cluster RBAC objects persist until removed.

## Dependencies
Depends on RBAC and coordination APIs in Kubernetes.

## Integration Points
Consumed by v1.8.0 controller and node manifests; secret `get` integrates with SMB credential retrieval.

## Risks and Edge Cases
Broad secret access on a cluster role remains the main security concern. Node service account still has no additional binding in this file.

## Test Signals
Provisioner lease acquisition, PVC lifecycle success, and authorization checks for listed resources.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.8.0/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.9.0/csi-smb-controller.yaml -->

# sources/control-plane/csi-driver-smb/deploy/v1.9.0/csi-smb-controller.yaml

## Purpose
Controller Deployment for SMB CSI v1.9.0.

## Important APIs, Types, and Functions
Matches v1.8.0 controller structure with `smbplugin:v1.9.0`, external-provisioner v3.2.0, livenessprobe v2.7.0, health `29642`, metrics `29644`, and kube-system leader election.

## Control Flow
External-provisioner invokes the controller service over the shared `/csi/csi.sock`; the SMB container serves controller, identity, and optionally node APIs.

## State and Persistence
Uses an ephemeral socket `emptyDir`; persistent effects are PV/PVC objects, events, leases, and SMB-backed subdirectories created during provisioning.

## Dependencies
Depends on v1.9.0 image, RBAC, Linux scheduling, and storage sidecar compatibility.

## Integration Points
Coordinates with v1.9.0 node DaemonSets and CSIDriver. Controller create/delete paths internally call node stage/unstage code for SMB share access.

## Risks and Edge Cases
Privileged controller container and single replica remain notable. If internal mount operations fail, provisioning/deletion fails despite Kubernetes API permissions.

## Test Signals
Deployment readiness, liveness, metrics, leader election, and PVC create/delete/clone flows.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.9.0/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.9.0/csi-smb-driver.yaml -->

# sources/control-plane/csi-driver-smb/deploy/v1.9.0/csi-smb-driver.yaml

## Purpose
CSIDriver object for SMB CSI v1.9.0.

## Important APIs, Types, and Functions
Defines driver name `smb.csi.k8s.io`, disables attach, and enables pod info on mount.

## Control Flow
Kubernetes uses it to route CSI calls to the node plugin without attach/detach controller operations.

## State and Persistence
Cluster-scoped CSIDriver state only.

## Dependencies
Requires storage.k8s.io/v1 and matching node registration.

## Integration Points
Matches manifests and Go driver constants for the SMB CSI driver name.

## Risks and Edge Cases
Driver name drift or absent CSIDriver can cause scheduling or mount behavior differences.

## Test Signals
CSIDriver existence, no attach operation creation, and pod metadata appearing in mount context.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.9.0/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.9.0/csi-smb-node-windows.yaml -->

# sources/control-plane/csi-driver-smb/deploy/v1.9.0/csi-smb-node-windows.yaml

## Purpose
Windows node DaemonSet for SMB CSI v1.9.0.

## Important APIs, Types, and Functions
Extends the v1.8.0 Windows manifest by using `smbplugin:v1.9.0` and adding `--remove-smb-mapping-during-unmount=true` to the SMB container.

## Control Flow
Node pod registers the driver and mounts via CSI proxy pipes. On unmount, the v1 Windows mounter can remove SMB global mappings after reference counting.

## State and Persistence
Uses host kubelet plugin/registry directories and CSI proxy pipes. The remove-mapping flag makes local reference files under the Windows CSI mount base relevant to cleanup state.

## Dependencies
Depends on Windows CSI proxy, kubelet host paths, v1.9.0 plugin image, and refcounter logic in `pkg/mounter`.

## Integration Points
Connects directly to `RemoveSMBMappingDuringUnmount` driver option and Windows `SMBUnmount` behavior.

## Risks and Edge Cases
Incorrect reference counts can remove a global SMB mapping still used by another volume or leave mappings behind. Mixed v1/v1beta proxy environments may not support identical cleanup semantics.

## Test Signals
Windows mount/unmount tests, absence of leaked SMB global mappings, liveness, registrar probe, and successful repeated volume reuse.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.9.0/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.9.0/csi-smb-node.yaml -->

# sources/control-plane/csi-driver-smb/deploy/v1.9.0/csi-smb-node.yaml

## Purpose
Linux node DaemonSet for SMB CSI v1.9.0.

## Important APIs, Types, and Functions
Linux hostNetwork DaemonSet with livenessprobe v2.7.0, registrar v2.5.1, `smbplugin:v1.9.0`, privileged security context, CSI socket hostPath, kubelet mountpoint hostPath, and plugins registry hostPath.

## Control Flow
Serves node CSI RPCs from `/csi/csi.sock`, registers with kubelet, and performs CIFS mounts into kubelet-managed pod paths.

## State and Persistence
Host mount state and sockets persist in kubelet directories. Pod replacement does not remove existing host mounts by itself.

## Dependencies
Depends on Linux CIFS support, kubelet, mount propagation, and v1.9.0 images.

## Integration Points
Works with v1.9.0 controller and CSIDriver. Linux cleanup uses `mount-utils` rather than the Windows SMB mapping flag.

## Risks and Edge Cases
Privileged host access, mount propagation, DNS behavior, and stale mounts remain operational risks.

## Test Signals
DaemonSet rollout, health endpoint, CSINode registration, and successful stage/publish/unpublish/unstage flows.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.9.0/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.9.0/rbac-csi-smb.yaml -->

# sources/control-plane/csi-driver-smb/deploy/v1.9.0/rbac-csi-smb.yaml

## Purpose
RBAC for SMB CSI v1.9.0.

## Important APIs, Types, and Functions
Defines controller/node service accounts, `smb-external-provisioner-role`, and controller binding. Grants PV/PVC, StorageClass, event, CSINode, node, lease, and secret access.

## Control Flow
Provisioner sidecar uses the controller account to watch and mutate storage resources, emit events, run leader election, and read credentials.

## State and Persistence
Persistent RBAC policy objects only.

## Dependencies
Requires Kubernetes RBAC, storage, core, and coordination APIs.

## Integration Points
Bound to v1.9.0 controller Deployment and referenced by v1.9.0 node DaemonSets.

## Risks and Edge Cases
Secret read permission is broad for a cluster role. Any namespace or service account name drift between manifests breaks provisioning.

## Test Signals
Authorization checks, leader-election lease, successful PVC provisioning/deletion, and event emission.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.9.0/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/boilerplate/boilerplate.py -->

# sources/control-plane/csi-driver-smb/hack/boilerplate/boilerplate.py

## Purpose
Python verifier for Kubernetes copyright boilerplate headers across repository files.

## Important APIs, Types, and Functions
Uses argparse, glob, regex, os.walk, and difflib. Key functions are `get_refs`, `file_passes`, `file_extension`, `normalize_files`, `get_files`, `get_regexs`, and `main`.

## Control Flow
Loads boilerplate reference files by extension, walks input/root files, strips Go build tags or script shebangs, normalizes copyright years, compares headers, and prints failing filenames.

## State and Persistence
Read-only against source files. Opens `/dev/null` for quiet mode and emits diagnostics to stderr/stdout.

## Dependencies
Depends on `boilerplate.*.txt` templates and filesystem layout rooted above the hack directory.

## Integration Points
Called by `verify-boilerplate.sh` as a CI gate.

## Risks and Edge Cases
Default root/boilerplate paths are unusual for nested source snapshots. `refs[extension]` assumes a matching reference exists. Skips are substring-based and may over/under-filter.

## Test Signals
Failing filenames on stdout, verbose unified diffs, and successful zero-output verification.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/boilerplate/boilerplate.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/release-image.sh -->

# sources/control-plane/csi-driver-smb/hack/release-image.sh

## Purpose
Release helper to build and publish Linux/Windows SMB CSI images to Azure Container Registry and inspect the public latest image.

## Important APIs, Types, and Functions
Shell script requiring registry name argument. Exports `REGISTRY_NAME`, `REGISTRY`, `IMAGENAME`, `CI`, `PUBLISH`, and `WINDOWS_USE_HOST_PROCESS_CONTAINERS`, runs `az acr login`, then make targets.

## Control Flow
Validates an argument, logs into ACR, runs `make container-all container-windows-hostprocess-latest push-manifest push-latest`, waits 60 seconds, pulls `mcr.microsoft.com/k8s/csi/smb-csi:latest`, and prints image creation metadata.

## State and Persistence
Mutates local Docker image cache, ACR registry content, public manifest/tag state, and environment for make.

## Dependencies
Requires bash, Azure CLI, Docker, Makefile targets, registry credentials, and network access.

## Integration Points
Part of release automation for publishing multi-platform images referenced by manifests and Helm chart.

## Risks and Edge Cases
Publishes mutable `latest`; unquoted registry variable usage is fragile; release success depends on delayed external registry propagation.

## Test Signals
Successful ACR login, make completion, docker pull success, and `docker inspect` Created output.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/release-image.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/update-dependencies.sh -->

# sources/control-plane/csi-driver-smb/hack/update-dependencies.sh

## Purpose
Updates Go module dependency pins and vendor content in a deterministic Kubernetes-style workflow.

## Important APIs, Types, and Functions
Uses `go mod edit -json`, `jq`, `go list -m -json all`, `go mod tidy`, `go mod vendor`, and helper functions `ensure_require_replace_directives_for_all_dependencies`, `group_replace_directives`, and `prune-vendor`.

## Control Flow
Enables modules, clears GOPATH/GOFLAGS, cd's to repo root, captures require/replace directives, pins all dependencies with replace directives, adds indirect requires, tidies, repeats pinning, groups replace directives, and vendors.

## State and Persistence
Mutates `go.mod`, `go.sum`, and `vendor/`. Uses a temp directory and leaves source changes for review.

## Dependencies
Requires git, Go toolchain, jq, awk, xargs, and module network/cache access.

## Integration Points
Pairs with `verify-gomod.sh` and `verify-update.sh` in CI.

## Risks and Edge Cases
Mass pinning can create large diffs and hide upstream replacement intent. `xargs` with empty input and network instability can fail. `prune-vendor` is defined but disabled.

## Test Signals
`SUCCESS`, clean `go mod tidy/vendor`, and no unexpected diff under verify scripts.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/update-dependencies.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/update-gofmt.sh -->

# sources/control-plane/csi-driver-smb/hack/update-gofmt.sh

## Purpose
Formats all non-vendor Go files with simplified gofmt.

## Important APIs, Types, and Functions
Runs `find . -name "*.go" | grep -v "/vendor/" | xargs gofmt -s -w`.

## Control Flow
Fails on command errors through `set -euo pipefail`; otherwise rewrites matching files in place.

## State and Persistence
Mutates Go source files.

## Dependencies
Requires bash, find, grep, xargs, and gofmt.

## Integration Points
Repair companion for `verify-gofmt.sh`.

## Risks and Edge Cases
Whitespace-only changes can touch many files. It assumes file names are safe for xargs whitespace handling.

## Test Signals
Subsequent `verify-gofmt.sh` reports no diff.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/update-gofmt.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/update-gomod.sh -->

# sources/control-plane/csi-driver-smb/hack/update-gomod.sh

## Purpose
Updates `replace` directives for Kubernetes staging modules to match a specified Kubernetes version.

## Important APIs, Types, and Functions
Accepts a version argument, fetches Kubernetes `go.mod`, extracts staging module names with sed, resolves `kubernetes-$VERSION` module versions via `go mod download -json`, and applies `go mod edit -replace`.

## Control Flow
Strips leading `v` from the version, validates it, downloads upstream go.mod, loops over modules, prints module/version, and edits local go.mod.

## State and Persistence
Mutates local `go.mod` replace directives.

## Dependencies
Requires curl, sed, Go modules network access, and a valid Kubernetes release tag.

## Integration Points
Used during Kubernetes dependency bumps before dependency/vendor update verification.

## Risks and Edge Cases
Remote `go.mod` parsing is brittle. Network or missing pseudo-version modules fail the update. No `go mod tidy` is run here.

## Test Signals
Printed module versions, changed replace directives, and subsequent `go mod tidy/vendor` success.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/update-gomod.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/verify-all.sh -->

# sources/control-plane/csi-driver-smb/hack/verify-all.sh

## Purpose
Aggregates major repository verification gates.

## Important APIs, Types, and Functions
Computes `PKG_ROOT` with `git rev-parse --show-toplevel` and runs verify scripts for gofmt, govet, yamllint, boilerplate, Helm chart files, Helm chart content, Helm chart index, and gomod.

## Control Flow
Sequentially executes each gate with `set -euo pipefail`, stopping at the first failure.

## State and Persistence
Mostly read-only, but invoked scripts may install tools or run `go mod tidy/vendor` before diffing.

## Dependencies
Depends on every child verify script and their tools.

## Integration Points
Top-level CI entrypoint for static validation.

## Risks and Edge Cases
Ordering hides later failures. Some child scripts have network and package-manager side effects.

## Test Signals
Zero exit status after all child scripts.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/verify-all.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/verify-boilerplate.sh -->

# sources/control-plane/csi-driver-smb/hack/verify-boilerplate.sh

## Purpose
CI gate for source boilerplate compliance.

## Important APIs, Types, and Functions
Sets `REPO_ROOT`, locates `hack/boilerplate/boilerplate.py`, captures failing files into an array, defines cleanup for a temp file, and exits nonzero when failures exist.

## Control Flow
Runs the Python checker, prints each file with a wrong header, and exits 1 if any are found.

## State and Persistence
Creates and deletes a temp file. Does not change source.

## Dependencies
Requires bash, Python checker, boilerplate templates, and mktemp.

## Integration Points
Called by `verify-all.sh`.

## Risks and Edge Cases
The `unitTestOut` temp file is created but not used. Array capture can mis-handle filenames with whitespace.

## Test Signals
No printed "Boilerplate header is wrong" lines and zero exit status.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/verify-boilerplate.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/verify-examples.sh -->

# sources/control-plane/csi-driver-smb/hack/verify-examples.sh

## Purpose
Runtime smoke test for example Kubernetes manifests.

## Important APIs, Types, and Functions
Defines `rollout_and_wait`, runs `kubectl apply`, parses created app resource names, then uses `kubectl rollout status` or `kubectl wait`.

## Control Flow
Applies the SMB StorageClass, then deploys example Deployment and StatefulSets and waits up to five minutes for readiness.

## State and Persistence
Creates real Kubernetes resources in the default namespace and storage classes in the cluster.

## Dependencies
Requires kubectl, a reachable cluster, working SMB CSI driver, and example manifests.

## Integration Points
Validates deploy/example workloads against the installed driver.

## Risks and Edge Cases
Resource parsing from `kubectl apply` output is brittle. It does not clean up created resources. Namespace is hard-coded to default.

## Test Signals
All examples reach rollout/ready status and script prints completion.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/verify-examples.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/verify-gofmt.sh -->

# sources/control-plane/csi-driver-smb/hack/verify-gofmt.sh

## Purpose
Checks that non-vendor Go files are gofmt-simplified.

## Important APIs, Types, and Functions
Captures `gofmt -s -d` output for all `.go` files outside vendor.

## Control Flow
Prints the diff and remediation hint if any formatting diff exists, otherwise prints "No issue found".

## State and Persistence
Read-only.

## Dependencies
Requires find, grep, xargs, and gofmt.

## Integration Points
Called by `verify-all.sh`; repaired by `update-gofmt.sh`.

## Risks and Edge Cases
Whitespace in filenames can confuse xargs. Very large diffs are printed in full.

## Test Signals
Empty gofmt diff and zero exit code.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/verify-gofmt.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/verify-gomod.sh -->

# sources/control-plane/csi-driver-smb/hack/verify-gomod.sh

## Purpose
Verifies module and vendor state are tidy and reproducible.

## Important APIs, Types, and Functions
Runs `go mod tidy`, `go mod vendor`, `git diff`, and `go list -mod readonly -m all`.

## Control Flow
Tidies and vendors, fails if any git diff remains, then lists all modules in readonly mode.

## State and Persistence
May mutate `go.mod`, `go.sum`, and vendor before failing, which is intentional for detecting required updates.

## Dependencies
Requires Go toolchain, git, module network/cache, and vendor support.

## Integration Points
CI gate and companion to dependency update scripts.

## Risks and Edge Cases
Running in a dirty worktree can conflate existing diffs with gomod changes. Network-dependent module resolution can make verification flaky.

## Test Signals
No git diff after tidy/vendor and successful readonly module listing.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/verify-gomod.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/verify-govet.sh -->

# sources/control-plane/csi-driver-smb/hack/verify-govet.sh

## Purpose
Runs Go vet across repository packages.

## Important APIs, Types, and Functions
Executes `go vet $(go list ./... | grep -v vendor)`.

## Control Flow
Lists Go packages, filters vendor, vets them, and exits on vet failure.

## State and Persistence
Read-only except Go cache.

## Dependencies
Requires Go toolchain and loadable packages.

## Integration Points
Called by `verify-all.sh`.

## Risks and Edge Cases
Command substitution can exceed shell limits in huge repos. Build tags or platform-specific packages may alter coverage.

## Test Signals
"Done" with zero exit status.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/verify-govet.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/verify-helm-chart-files.sh -->

# sources/control-plane/csi-driver-smb/hack/verify-helm-chart-files.sh

## Purpose
Verifies packaged Helm chart archives match committed chart sources.

## Important APIs, Types, and Functions
Disables git filemode tracking, checks initial diff, extracts chart `.tgz` files into chart directories, then checks git diff again.

## Control Flow
Fails immediately if the worktree is dirty, expands each packaged chart, and fails if expansion changes committed files.

## State and Persistence
Mutates git config `core.filemode` and extracts archives into chart directories during verification.

## Dependencies
Requires git, tar, chart archives, and shell glob behavior.

## Integration Points
Called by `verify-all.sh`; remediation is Helm package update.

## Risks and Edge Cases
Dirty worktree blocks verification. Extraction can overwrite files. The `[ -f $dir/*.tgz ]` glob test is fragile with multiple/no archives.

## Test Signals
No git diff after extraction and "chart tgz files verified."

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/verify-helm-chart-files.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/verify-helm-chart-index.sh -->

# sources/control-plane/csi-driver-smb/hack/verify-helm-chart-index.sh

## Purpose
Validates URLs referenced in `charts/index.yaml`.

## Important APIs, Types, and Functions
Defines `check_url` using `curl -I` and local fallback path checks, plus `check_yaml` that greps HTTP URLs from the index.

## Control Flow
Iterates over index URLs, accepts HTTP 200, or verifies the equivalent local file exists before failing.

## State and Persistence
Read-only.

## Dependencies
Requires curl, grep, awk, and chart index layout.

## Integration Points
Called by `verify-all.sh` and protects Helm repository index integrity.

## Risks and Edge Cases
YAML parsing via grep/awk can catch unrelated URLs or miss quoted forms. Network failures may be treated as warnings only if local file exists.

## Test Signals
All URLs report valid or have local files, followed by success message.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/verify-helm-chart-index.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/verify-helm-chart.sh -->

# sources/control-plane/csi-driver-smb/hack/verify-helm-chart.sh

## Purpose
Lints the latest Helm chart and verifies chart image settings match deploy manifests.

## Important APIs, Types, and Functions
Uses `helm lint`, `yq`, `pip`, `jq`, and helper functions `get_image_from_helm_chart` and `validate_image`.

## Control Flow
Installs Helm/pip/jq/yq if missing, lints the chart, extracts image references from deploy manifests and chart values, and compares expected image substrings.

## State and Persistence
May install system packages and Python packages. Reads manifests and chart values.

## Dependencies
Requires helm, yq, jq, pip, apt for auto-install paths, and chart/deploy file layout.

## Integration Points
Called by `verify-all.sh`; couples `charts/latest/csi-driver-smb` to `deploy/csi-smb-*.yaml`.

## Risks and Edge Cases
Auto-installing tools in CI is intrusive. The controller extraction assumes fixed container indexes and references an expected resizer image position that may not exist in older manifests.

## Test Signals
Helm lint success and all image comparisons pass.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/verify-helm-chart.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/verify-spelling.sh -->

# sources/control-plane/csi-driver-smb/hack/verify-spelling.sh

## Purpose
Runs misspell across tracked non-vendor files.

## Important APIs, Types, and Functions
Uses `misspell` version `v0.3.4`, installs it into a temp `GOBIN` if missing, and scans `git ls-files | grep -v vendor`.

## Control Flow
Creates temp dir, ensures misspell is available, writes misspell output to temp log, prints errors with `error:` prefix, and exits nonzero if any exist.

## State and Persistence
Uses temp directory and Go module/cache. Does not edit source.

## Dependencies
Requires git, Go toolchain, misspell or network access to install it.

## Integration Points
Optional CI quality gate.

## Risks and Edge Cases
`go get` for tool installation is outdated in newer Go versions. Grep vendor filtering is broad. False positives require dictionary or source changes elsewhere.

## Test Signals
Empty errors log and zero exit status.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/verify-spelling.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/verify-update.sh -->

# sources/control-plane/csi-driver-smb/hack/verify-update.sh

## Purpose
Checks whether previous update steps left the worktree dirty.

## Important APIs, Types, and Functions
Runs `git diff --shortstat`, prints full diff on failure, and exits nonzero.

## Control Flow
If any diff exists, reports dependency update changed files; otherwise prints Done.

## State and Persistence
Read-only.

## Dependencies
Requires git.

## Integration Points
Used after update scripts in CI to enforce committed generated output.

## Risks and Edge Cases
Any pre-existing uncommitted change causes failure, not only dependency updates.

## Test Signals
No shortstat output and zero exit status.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/verify-update.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/verify-yamllint.sh -->

# sources/control-plane/csi-driver-smb/hack/verify-yamllint.sh

## Purpose
Runs yamllint over deploy and example YAML files while ignoring line-length findings.

## Important APIs, Types, and Functions
Installs yamllint with apt if absent, writes lint output to `/tmp/yamllint.log`, filters "line too long", counts remaining findings, and fails if any remain.

## Control Flow
Loops over fixed glob patterns under `deploy/` and `deploy/example/`, runs yamllint, prints findings, and exits on first non-line-length issue.

## State and Persistence
May install yamllint. Writes `/tmp/yamllint.log`.

## Dependencies
Requires apt, yamllint, shell glob matching, and deploy/example layout.

## Integration Points
Called by `verify-all.sh`.

## Risks and Edge Cases
Unmatched globs may be passed literally. Shared `/tmp/yamllint.log` can be clobbered. Auto-installing packages requires root and network.

## Test Signals
All checked patterns print no remaining lint findings and final success message.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/hack/verify-yamllint.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/csi-common/driver.go -->

# sources/control-plane/csi-driver-smb/pkg/csi-common/driver.go

## Purpose
Shared CSI driver metadata and capability helper implementation.

## Important APIs, Types, and Functions
Defines `CSIDriver` with name, node ID, version, controller capabilities, volume access modes, and node capabilities. Functions include `NewCSIDriver`, validation methods, and add/get capability helpers.

## Control Flow
Driver construction validates nonempty name and node ID, logs empty version, and returns metadata. Validation methods allow UNKNOWN and otherwise check configured capability slices.

## State and Persistence
In-memory driver capability state only.

## Dependencies
Depends on CSI protobuf types, gRPC status/codes, and klog.

## Integration Points
Embedded by `pkg/smb.Driver`; used during driver startup and CSI RPC validation.

## Risks and Edge Cases
Empty version logs but still constructs a driver. Add methods replace existing capability slices instead of appending. Validation returns InvalidArgument with only enum string detail.

## Test Signals
`driver_test.go` covers constructor validation and capability add/validate behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/csi-common/driver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/csi-common/driver_test.go -->

# sources/control-plane/csi-driver-smb/pkg/csi-common/driver_test.go

## Purpose
Unit tests for shared CSI driver metadata and capability helpers.

## Important APIs, Types, and Functions
Defines fake driver constants and `NewFakeDriver`. Tests cover `NewCSIDriver`, `GetVolumeCapabilityAccessModes`, controller/node service validation, and add helpers.

## Control Flow
Table-driven tests construct drivers with valid/missing inputs and compare expected structs or gRPC errors.

## State and Persistence
No persistence; in-memory test objects only.

## Dependencies
Uses CSI protobufs, testify/assert, reflect, and gRPC status/codes.

## Integration Points
Provides confidence for `pkg/smb.Driver` embedded capability behavior.

## Risks and Edge Cases
Some comparisons use reflect on errors, which is sensitive to exact status representation. Tests do not cover duplicate capability handling.

## Test Signals
Passing package tests validate constructor and capability semantics.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/csi-common/driver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/csi-common/server.go -->

# sources/control-plane/csi-driver-smb/pkg/csi-common/server.go

## Purpose
Non-blocking gRPC server wrapper for CSI identity, controller, and node services.

## Important APIs, Types, and Functions
Defines `NonBlockingGRPCServer`, `NewNonBlockingGRPCServer`, and `nonBlockingGRPCServer` methods `Start`, `Wait`, `Stop`, `ForceStop`, and `serve`.

## Control Flow
`Start` launches `serve` in a goroutine. `serve` parses endpoint, removes existing Unix socket, listens, creates a gRPC server with `logGRPC` interceptor, registers supplied CSI services, and serves until stopped. Test mode schedules a graceful stop.

## State and Persistence
Holds a waitgroup and gRPC server pointer. Removes/recreates Unix socket files for Unix endpoints.

## Dependencies
Depends on net, os, runtime, sync, grpc, CSI protobuf registration, klog, and `ParseEndpoint`.

## Integration Points
Used by SMB driver `Run` to expose CSI services.

## Risks and Edge Cases
`Stop` and `ForceStop` assume `s.server` is initialized. Fatal logging exits the process on endpoint/listen errors. Test-mode waitgroup choreography is unusual and timing-sensitive.

## Test Signals
`server_test.go` smoke-tests construction, start, serve, wait, stop, and force stop.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/csi-common/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/csi-common/server_test.go -->

# sources/control-plane/csi-driver-smb/pkg/csi-common/server_test.go

## Purpose
Smoke tests for the non-blocking gRPC server wrapper.

## Important APIs, Types, and Functions
Tests `NewNonBlockingGRPCServer`, `Start`, direct `serve`, `Wait`, `Stop`, and `ForceStop`.

## Control Flow
Uses ephemeral TCP endpoints and sleeps to avoid races, then relies on test mode to stop serving.

## State and Persistence
Creates transient local listeners and in-memory gRPC servers.

## Dependencies
Uses grpc, sync, time, and testify/assert.

## Integration Points
Guards the server wrapper used by driver startup.

## Risks and Edge Cases
Sleep-based timing can be flaky. It does not exercise Unix socket cleanup, registered service calls, or nil-server stop behavior.

## Test Signals
Passing tests indicate basic lifecycle methods do not panic in expected paths.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/csi-common/server_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/csi-common/utils.go -->

# sources/control-plane/csi-driver-smb/pkg/csi-common/utils.go

## Purpose
CSI utility helpers for endpoint parsing, capability object construction, log levels, and gRPC request/response logging.

## Important APIs, Types, and Functions
Functions include `ParseEndpoint`, `NewVolumeCapabilityAccessMode`, `NewControllerServiceCapability`, `NewNodeServiceCapability`, `getLogLevel`, and `logGRPC`.

## Control Flow
Endpoint parsing accepts `unix://` and `tcp://` prefixes. The interceptor logs method, sanitized request, error or sanitized response, lowering verbosity for common probe/stat calls.

## State and Persistence
No persistent state; writes logs through klog.

## Dependencies
Depends on CSI protobufs, grpc interceptor APIs, klog, and `protosanitizer.StripSecrets`.

## Integration Points
Used by `server.go` and capability setup in driver code.

## Risks and Edge Cases
Endpoint proto preserves original case, which may be rejected by `net.Listen` if uppercase. Logging still exposes non-secret request fields.

## Test Signals
`utils_test.go` covers valid/invalid endpoints, secret stripping, capability constructors, and log-level mapping.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/csi-common/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/csi-common/utils_test.go -->

# sources/control-plane/csi-driver-smb/pkg/csi-common/utils_test.go

## Purpose
Unit tests for CSI common utilities.

## Important APIs, Types, and Functions
Tests endpoint parsing, `logGRPC`, capability constructor helpers, and `getLogLevel`.

## Control Flow
Configures klog to a buffer for interceptor assertions, invokes helper functions over tables, and validates expected values.

## State and Persistence
Temporarily changes process flags/klog output in tests.

## Dependencies
Uses CSI protobufs, grpc, klog, flags, bytes, and testify.

## Integration Points
Protects logging and endpoint behavior used by the gRPC server.

## Risks and Edge Cases
Global flag parsing/klog output can interact with other tests. The endpoint tests assert uppercase proto output but not net.Listen compatibility.

## Test Signals
Passing tests show secrets are stripped and helper outputs match CSI protobuf expectations.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/csi-common/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/mounter/refcounter_windows.go -->

# sources/control-plane/csi-driver-smb/pkg/mounter/refcounter_windows.go

## Purpose
Windows-only reference counter for SMB global mappings.

## Important APIs, Types, and Functions
Defines `basePath`, `mutexes`, `lock`, `getRootMappingPath`, `incementVolumeIDReferencesCount`, `decrementVolumeIDReferencesCount`, `getVolumeIDReferencesCount`, and `getMd5`.

## Control Flow
Normalizes UNC paths to server/share mapping keys, serializes operations per mapping key, writes one MD5-named reference file per volume ID, removes it on decrement, and counts files to decide when no references remain.

## State and Persistence
Persists reference files under `c:\csi\smbmounts\<server>\<share>`. In-memory mutexes serialize per-process access only.

## Dependencies
Uses os, filepath, strings, sync.Map, md5, and Windows path conventions.

## Integration Points
Used by Windows CSI proxy v1 mounter when `RemoveSMBMappingDuringUnmount` is enabled from the v1.9 manifest flag.

## Risks and Edge Cases
Function names contain misspellings but are internal. Reference files can become stale after process crash. `os.MkdirAll(path, os.ModeDir)` lacks normal permission bits. MD5 is for naming only.

## Test Signals
`refcounter_windows_test.go` covers locking, root path parsing, increment/decrement, idempotent increments, and duplicate decrement errors.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/mounter/refcounter_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/mounter/refcounter_windows_test.go -->

# sources/control-plane/csi-driver-smb/pkg/mounter/refcounter_windows_test.go

## Purpose
Windows tests for SMB mapping reference counter behavior.

## Important APIs, Types, and Functions
Tests `lock`, `getRootMappingPath`, increment/decrement/count helpers, and MD5 reference file creation.

## Control Flow
Uses TEMP-derived base paths, creates references for volumes, checks counts, removes references, and cleans temp directories.

## State and Persistence
Creates temporary directories/files under `%TEMP%\TestMappingPathCounter`.

## Dependencies
Uses os, testing, time, and testify/assert.

## Integration Points
Validates cleanup logic used by Windows SMB unmount mapping removal.

## Risks and Edge Cases
Global `basePath` mutation can leak between parallel tests if ever run concurrently. Timing test for lock blocking is sleep-based.

## Test Signals
Passing tests verify expected reference count transitions and path parsing.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/mounter/refcounter_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/mounter/safe_mounter_host_process_windows.go -->

# sources/control-plane/csi-driver-smb/pkg/mounter/safe_mounter_host_process_windows.go

## Purpose
Windows HostProcess mounter implementation that bypasses CSI proxy clients and uses local filesystem/SMB wrappers.

## Important APIs, Types, and Functions
Defines `winMounter`, `NewWinMounter`, `SMBMount`, `SMBUnmount`, `Mount`, `Unmount`, `Rmdir`, `IsLikelyNotMountPoint`, `MakeDir`, `ExistsPath`, and mount.Interface stubs.

## Control Flow
`SMBMount` validates options, ensures parent directory, normalizes UNC path, checks/removes invalid existing global mapping, creates mapping with credentials, and creates a symlink from target to remote path. `SMBUnmount` reads the target link, checks duplicate mounts, removes global mapping if safe, then removes the target.

## State and Persistence
Creates Windows symlinks and SMB global mappings. Uses driver global mount path to find duplicate mounts.

## Dependencies
Depends on `pkg/os/filesystem`, `pkg/os/smb`, os symlinks, klog, and mount-utils interfaces.

## Integration Points
Selected by `NewSafeMounter(enableWindowsHostProcess=true, ...)` and connected to HostProcess manifests/options.

## Risks and Edge Cases
Duplicate detection scans a fixed kubelet path. Mapping removal errors are logged but unmount still removes target in some cases. Symlink creation fails if target already exists.

## Test Signals
No direct tests in this file; exercised indirectly by Windows node lifecycle and OS wrapper tests.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/mounter/safe_mounter_host_process_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/mounter/safe_mounter_unix.go -->

# sources/control-plane/csi-driver-smb/pkg/mounter/safe_mounter_unix.go

## Purpose
Linux/Darwin factory for Kubernetes `SafeFormatAndMount`.

## Important APIs, Types, and Functions
Defines `NewSafeMounter(_, _ bool)` returning `mount.SafeFormatAndMount{Interface: mount.New(""), Exec: utilexec.New()}`.

## Control Flow
Ignores Windows-specific flags and returns the standard mount implementation.

## State and Persistence
No state; callers perform actual mount operations.

## Dependencies
Depends on `k8s.io/mount-utils` and `k8s.io/utils/exec`.

## Integration Points
Used by SMB driver startup on Linux and Darwin.

## Risks and Edge Cases
No custom behavior for SMB mapping cleanup or HostProcess flags outside Windows.

## Test Signals
`safe_mounter_unix_test.go` verifies a nonnil mounter and nil error.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/mounter/safe_mounter_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/mounter/safe_mounter_unix_test.go -->

# sources/control-plane/csi-driver-smb/pkg/mounter/safe_mounter_unix_test.go

## Purpose
Basic Unix test for the safe mounter factory.

## Important APIs, Types, and Functions
Calls `NewSafeMounter(true, true)` and asserts nonnil response and nil error.

## Control Flow
Single construction test; Windows flags are intentionally ignored on this build.

## State and Persistence
No persistent state.

## Dependencies
Uses testing and testify/assert.

## Integration Points
Confirms Linux/Darwin driver startup can obtain a mount implementation.

## Risks and Edge Cases
Does not exercise mount commands or error paths.

## Test Signals
Passing test indicates factory wiring is intact.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/mounter/safe_mounter_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/mounter/safe_mounter_v1beta_windows.go -->

# sources/control-plane/csi-driver-smb/pkg/mounter/safe_mounter_v1beta_windows.go

## Purpose
Windows CSI proxy v1beta fallback mounter.

## Important APIs, Types, and Functions
Defines `csiProxyMounterV1Beta` with filesystem and SMB v1beta clients. Implements `SMBMount`, `SMBUnmount`, symlink `Mount`, `Rmdir`, mountpoint checks, `MakeDir`, `ExistsPath`, `GetAPIVersions`, and unimplemented mount.Interface methods.

## Control Flow
Mount ensures parent path, optionally resolves `svc.cluster.local` hostnames to IPv4, normalizes slashes, calls `NewSmbGlobalMapping`, and uses CSI proxy filesystem operations for links/directories. Unmount removes the target directory only.

## State and Persistence
Creates SMB global mappings and filesystem links through CSI proxy, but does not remove global mappings on unmount.

## Dependencies
Depends on CSI proxy filesystem/smb v1beta clients, net DNS resolution, klog, and mount-utils.

## Integration Points
Fallback from `NewSafeMounter` when CSI proxy v1 client creation fails.

## Risks and Edge Cases
Older proxy API has different semantics and lacks mapping cleanup. Hostname-to-IP replacement only handles first source component ending in `svc.cluster.local`. Many interface methods return unimplemented errors.

## Test Signals
No direct tests in this file; behavior is covered by Windows integration and fallback startup logs.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/mounter/safe_mounter_v1beta_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/mounter/safe_mounter_windows.go -->

# sources/control-plane/csi-driver-smb/pkg/mounter/safe_mounter_windows.go

## Purpose
Primary Windows CSI proxy v1 mounter and safe mounter factory.

## Important APIs, Types, and Functions
Defines `CSIProxyMounter`, `csiProxyMounter`, `normalizeWindowsPath`, `SMBMount`, `SMBUnmount`, `Mount`, `Rmdir`, `IsLikelyNotMountPoint`, `MakeDir`, `ExistsPath`, `NewCSIProxyMounter`, and Windows `NewSafeMounter`.

## Control Flow
`SMBMount` validates credentials, ensures parent, resolves cluster DNS hostnames, normalizes/trims source, obtains root mapping path when cleanup is enabled, locks by mapping, calls CSI proxy `NewSmbGlobalMapping`, and writes a volume reference file. `SMBUnmount` reads the symlink target, decrements reference count, removes the global mapping when count reaches zero, then removes the target. Factory chooses HostProcess, CSI proxy v1, then v1beta fallback.

## State and Persistence
Maintains SMB global mappings, CSI proxy symlinks/directories, and optional reference files under `c:\csi\smbmounts`.

## Dependencies
Depends on CSI proxy filesystem/smb v1 clients, v1beta fallback, host-process mounter, mount-utils, utilexec, klog, os symlinks, DNS, and refcounter helpers.

## Integration Points
Used by driver startup on Windows; driven by deployment flags for HostProcess and mapping cleanup.

## Risks and Edge Cases
Reference file failure after mapping creation can leave mappings without tracked references. `os.Readlink(target)` assumes local process can read CSI proxy-created links. Locking is process-local only.

## Test Signals
Covered indirectly by Windows refcounter tests and node lifecycle tests; startup logs identify selected API version.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/mounter/safe_mounter_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/os/filesystem/filesystem.go -->

# sources/control-plane/csi-driver-smb/pkg/os/filesystem/filesystem.go

## Purpose
Windows filesystem abstraction for HostProcess mounter operations.

## Important APIs, Types, and Functions
Functions include `ValidatePathWindows`, `PathExists`, `PathValid`, `Rmdir`, `IsMountPoint`, `IsSymlink`, plus helpers for invalid character, UNC, and absolute path checks.

## Control Flow
Validates Windows paths for length, absolute drive prefix, no UNC prefix, no invalid characters or `..`; checks existence with `os.Lstat`; validates remote paths through PowerShell `Test-Path`; removes paths with os remove calls; treats valid symlinks as mountpoints.

## State and Persistence
Mutates filesystem only through `Rmdir`; otherwise reads path state and executes PowerShell.

## Dependencies
Depends on os, regexp, strings, klog, and `util.RunPowershellCmd`.

## Integration Points
Used by HostProcess Windows mounter to create/check/remove local paths and verify SMB mapping targets.

## Risks and Edge Cases
Rejects UNC paths intentionally, so callers must normalize local paths first. `strings.Contains(path, "..")` can reject benign names. PowerShell output parsing is prefix-based.

## Test Signals
No mapped direct tests; exercised through HostProcess mounter and Windows integration.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/os/filesystem/filesystem.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/os/smb/smb.go -->

# sources/control-plane/csi-driver-smb/pkg/os/smb/smb.go

## Purpose
Windows SMB global mapping wrapper for HostProcess mode.

## Important APIs, Types, and Functions
Functions include `IsSmbMapped`, `NewSmbGlobalMapping`, `RemoveSmbGlobalMapping`, `GetRemoteServerFromTarget`, and `CheckForDuplicateSMBMounts`.

## Control Flow
Uses PowerShell commands with environment variables for user input to check mapping status, create mappings with credentials and privacy, remove mappings, read symlink targets, and scan kubelet globalmount links for duplicate remote server usage.

## State and Persistence
Creates/removes Windows SMB global mappings and reads symlink state under the driver global mount directory.

## Dependencies
Depends on PowerShell SMB cmdlets, os symlinks, filepath, klog, and `util.RunPowershellCmd`.

## Integration Points
Used by HostProcess `winMounter` for SMB mapping lifecycle.

## Risks and Edge Cases
PowerShell/SMB cmdlet availability is required. Duplicate detection compares remote server strings case-sensitively. Directory scan failures abort duplicate detection.

## Test Signals
`smb_test.go` covers duplicate mount error behavior for a missing directory.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/os/smb/smb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/os/smb/smb_test.go -->

# sources/control-plane/csi-driver-smb/pkg/os/smb/smb_test.go

## Purpose
Windows unit test for HostProcess SMB duplicate mount detection.

## Important APIs, Types, and Functions
Tests `CheckForDuplicateSMBMounts` with a non-existing directory.

## Control Flow
Calls the function and compares expected false result plus expected Windows open error string.

## State and Persistence
No created state.

## Dependencies
Uses testing and fmt; expected error text is Windows-specific.

## Integration Points
Protects one failure path used by HostProcess unmount logic.

## Risks and Edge Cases
Coverage is very narrow and error-string matching can vary by OS/localization.

## Test Signals
Passing test confirms missing duplicate scan root returns an error.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/os/smb/smb_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/controllerserver.go -->

# sources/control-plane/csi-driver-smb/pkg/smb/controllerserver.go

## Purpose
CSI controller implementation for dynamic SMB volume provisioning, deletion, validation, clone, and expansion metadata.

## Important APIs, Types, and Functions
Defines `smbVolume`, volume ID segment constants, `CreateVolume`, `DeleteVolume`, capability RPCs, `ControllerExpandVolume`, `internalMount`, `internalUnmount`, `copyFromVolume`, `copyVolume`, `getVolumeIDFromSmbVol`, `getInternalMountPath`, `newSMBVolume`, `getInternalVolumePath`, `smbVolToCSI`, `getSmbVolFromID`, and `isValidVolumeCapabilities`.

## Control Flow
Create validates name/capabilities/parameters, builds an SMB volume, decides whether to create a subdirectory based on secrets, explicit subDir, guest mount, or content source, internally stages the base share, creates subdirectories, optionally clones data via `cp -a`, and returns a CSI Volume. Delete parses the volume ID, locks the volume, stages the share when secrets are available and policy is not retain, deletes or archives the subdirectory, caches deletion, and unmounts.

## State and Persistence
Creates, deletes, or renames directories on the SMB share. Uses in-memory volume locks and timed deletion cache. Volume identity is encoded in a `#`-separated string containing source, subDir, uuid, and optional onDelete policy.

## Dependencies
Depends on CSI protobufs, gRPC status codes, os/filepath/fs, `cp`, klog, Azure timed cache, and node server staging methods.

## Integration Points
Called by external-provisioner. Internal mount/unmount reuses NodeStage/NodeUnstage; volume context feeds node publishing.

## Risks and Edge Cases
Volume IDs cannot safely contain `#`. Clone uses Unix `cp`, so controller clone is platform-dependent. Delete only mutates remote data when secrets are provided. Archive can overwrite after optional removal.

## Test Signals
`controllerserver_test.go` covers create/delete validation, ID encoding/parsing, onDelete policies, clone paths, capability validation, and unsupported RPCs.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/controllerserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/controllerserver_test.go -->

# sources/control-plane/csi-driver-smb/pkg/smb/controllerserver_test.go

## Purpose
Unit tests for SMB controller behavior and helper functions.

## Important APIs, Types, and Functions
Tests controller capabilities, create/delete volume, validate capabilities, unsupported controller RPCs, expansion, volume ID parse/build, internal path helpers, `newSMBVolume`, `isValidVolumeCapabilities`, and clone helper behavior.

## Control Flow
Uses fake driver and fake mounter, sets working mount directories, builds CSI requests, and validates responses/errors across table cases. Some Windows paths are skipped or treated specially.

## State and Persistence
Creates local test directories/files under the current working directory and uses fake mounter state.

## Dependencies
Uses CSI protobufs, testify, grpc status/codes, runtime checks, os/filepath, and test utilities.

## Integration Points
Exercises controller code paths that external-provisioner depends on and internal staging calls that reuse node server logic.

## Risks and Edge Cases
Large tests include platform skips, so Windows-specific controller behavior has less assertion depth. Fake mounter does not simulate real CIFS or CSI proxy semantics.

## Test Signals
Passing tests validate parameter validation, onDelete ID semantics, clone support, and expected unimplemented RPC errors.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/controllerserver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/fake_mounter.go -->

# sources/control-plane/csi-driver-smb/pkg/smb/fake_mounter.go

## Purpose
Test mounter implementation for SMB driver unit tests.

## Important APIs, Types, and Functions
Defines `fakeMounter` embedding `mount.FakeMounter`, overrides `Mount`, `MountSensitive`, and `IsLikelyNotMountPoint`, and exposes `NewFakeMounter`.

## Control Flow
Fake methods return errors when source/target/path contains sentinel substrings, otherwise success. On Windows, `NewFakeMounter` delegates to real Windows safe mounter with HostProcess flags.

## State and Persistence
No fake persistence. Windows path may create real mounter clients.

## Dependencies
Depends on runtime, strings, mount-utils, and package mounter.

## Integration Points
Used by controller/node tests to simulate mount success/failure.

## Risks and Edge Cases
Windows behavior is not actually fake, which can make tests depend on host Windows/CSI-proxy capabilities. Fake does not track mounts.

## Test Signals
`fake_mounter_test.go` validates sentinel error behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/fake_mounter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/fake_mounter_test.go -->

# sources/control-plane/csi-driver-smb/pkg/smb/fake_mounter_test.go

## Purpose
Tests fake mounter sentinel behavior.

## Important APIs, Types, and Functions
Tests `Mount`, `MountSensitive`, and `IsLikelyNotMountPoint` using configured source/target/path substrings.

## Control Flow
Installs fake mounter on a fake driver and checks returned errors match expected values.

## State and Persistence
No persistent state.

## Dependencies
Uses mount-utils, reflect, fmt, and testing.

## Integration Points
Ensures fake behavior used by broader driver tests is predictable.

## Risks and Edge Cases
Does not validate fake mount state transitions or Windows fallback behavior.

## Test Signals
Expected fake errors and nil success paths.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/fake_mounter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/identityserver.go -->

# sources/control-plane/csi-driver-smb/pkg/smb/identityserver.go

## Purpose
CSI identity service implementation for the SMB driver.

## Important APIs, Types, and Functions
Implements `GetPluginInfo`, `Probe`, and `GetPluginCapabilities` on `Driver`.

## Control Flow
Plugin info validates configured name/version and returns them. Probe always returns ready true. Capabilities advertise controller service support.

## State and Persistence
Reads driver metadata only; no persistence.

## Dependencies
Depends on CSI protobufs, gRPC status/codes, and wrapperspb.

## Integration Points
Registered by the common gRPC server and used by sidecars/liveness checks.

## Risks and Edge Cases
Empty name/version makes GetPluginInfo unavailable. Probe does not verify backend mount readiness.

## Test Signals
`identityserver_test.go` covers info errors, probe readiness, and advertised plugin capabilities.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/identityserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/identityserver_test.go -->

# sources/control-plane/csi-driver-smb/pkg/smb/identityserver_test.go

## Purpose
Unit tests for SMB CSI identity RPCs.

## Important APIs, Types, and Functions
Tests `GetPluginInfo`, `Probe`, and `GetPluginCapabilities` using fake drivers with missing metadata variants.

## Control Flow
Builds requests, invokes identity methods, compares errors and response fields.

## State and Persistence
In-memory only.

## Dependencies
Uses CSI protobufs, testify/assert, grpc status/codes, reflect, and testing.

## Integration Points
Validates identity behavior expected by sidecars and CSI clients.

## Risks and Edge Cases
Tests do not verify driver version content beyond empty/nonempty behavior.

## Test Signals
Expected unavailable errors for missing metadata and ready probe response.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/identityserver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/nodeserver.go -->

# sources/control-plane/csi-driver-smb/pkg/smb/nodeserver.go

## Purpose
CSI node service implementation for staging, publishing, unpublishing, unstaging, volume stats, node info, and mount-related helpers.

## Important APIs, Types, and Functions
Implements `NodePublishVolume`, `NodeUnpublishVolume`, `NodeStageVolume`, `NodeUnstageVolume`, `NodeGetCapabilities`, `NodeGetInfo`, `NodeGetVolumeStats`, `NodeExpandVolume`, `ensureMountPoint`, Kerberos helpers, mount flag helpers, and group permission helpers.

## Control Flow
Publish validates request, handles ephemeral volumes by staging directly at target, otherwise bind-mounts staging to target and propagates read-only flags. Stage validates volume/source, locks by volume-target, resolves credentials from secrets or Kubernetes secret for ephemeral volumes, prepares Linux CIFS or Windows SMB options, handles Kerberos caches, ensures mountpoint, appends subDir, validates traversal, and mounts with a timeout. Unstage cleans SMB mountpoint and deletes Kerberos cache. Stats read filesystem metrics and cache responses.

## State and Persistence
Creates mountpoints, bind mounts, SMB/CIFS mounts, Kerberos cache files and symlinks, and timed volume stats cache entries. Uses per-volume operation locks.

## Dependencies
Depends on CSI protobufs, mount-utils, Kubernetes volume metrics, os/filepath, runtime, base64, klog, Azure timed cache, utility timeout helpers, and platform-specific SMB mount helpers.

## Integration Points
Called by kubelet and by controller internal mount/unmount paths. Integrates with Kubernetes secrets for ephemeral volume credentials and `volumeMountGroup` for group access.

## Risks and Edge Cases
Mount timeout is fixed at 110 seconds. Password special characters change sensitive option shape. Kerberos symlink is shared per UID and requires careful cleanup. Cached stats can become stale for up to cache duration.

## Test Signals
Mapped tests are outside this item, but rg shows node tests covering stage/publish/unpublish/unstage, stats, Kerberos helpers, mountpoint behavior, and group mode helpers.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/nodeserver.go -->
