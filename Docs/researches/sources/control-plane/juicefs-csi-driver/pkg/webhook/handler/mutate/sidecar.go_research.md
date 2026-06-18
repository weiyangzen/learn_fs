<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/mutate/sidecar.go -->
## sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/mutate/sidecar.go

### Purpose
`sidecar.go` implements JuiceFS sidecar injection for pods admitted by the webhook. It converts PVC-backed volumes into hostPath mounts served by a generated JuiceFS mount sidecar or native sidecar init container, creates per-PVC secrets, and supports serverless-specific builders.

### Important APIs, Types, And Functions
`checkSupportNativeSidecar` gates native sidecars by Kubernetes version and global override. `SidecarMutate` holds the k8s client, JuiceFS provider, serverless flag, native sidecar support, PV/PVC pairs, and current `JfsSetting`. `NewSidecarMutate` discovers server version. `Mutate` loops over all PV pairs. `mutate` builds settings and injects resources. `Deduplicate`, `GetSettings`, `injectContainer`, `injectVolume`, `injectLabel`, `injectAnnotation`, and `createOrUpdateSecret` are the main subroutines.

### Control Flow
The constructor queries discovery `ServerVersion`, parses it, and enables native sidecar support for Kubernetes `>=1.29.0` unless the global override is set. For each PV/PVC pair, `mutate` reads node-publish secrets and volume attributes, overlays PVC annotations prefixed `juicefs`, resolves optional node metadata from `Spec.NodeName` or `NodeSelector`, parses a `JfsSetting`, selects a random mount path or a deterministic serverless PVC/UID path, enforces at least 1GiB quota capacity when quota is enabled, selects a builder, creates/updates a secret with the PVC as owner, builds a mount sidecar pod, deduplicates names, rewrites matching pod volumes/mounts, injects sidecar volumes, labels, annotations, and the container/init-container.

### State, Persistence, And Dependencies
Persistent state is the Kubernetes Secret created or updated for each PVC. The returned pod mutation is sent back as an admission patch. Dependencies include Kubernetes discovery/version APIs, corev1 resources, client-go retry, project config/global config, JuiceFS provider interface, mount builders, k8s client, resource PV pairs, and utility helpers.

### Integration Points
This is the core of webhook sidecar mode. It integrates pod admission with CSI PV attributes, PVC annotations, node labels/annotations for templating, builder-specific mount pod templates, serverless VCI/CCI modes, and Kubernetes native sidecar semantics.

### Risks
`GetSettings` assumes `pv.Spec.CSI.NodePublishSecretRef` is non-nil. Capacity below 1GiB fails admission when quota is enabled. `Deduplicate` only checks existing container/volume names and can still collide across multiple generated mount pods in edge cases. Secret update compares owner references by index, so reordered references can trigger updates. Native sidecar support is checked twice in the constructor. Pod volume rewrite affects app containers and, for native sidecars, init containers, but not ephemeral containers. Serverless mount paths based on PVC UID improve stability but can leak assumptions into hostPath layout.

### Test Signals
High-value tests include Kubernetes version/override gating, missing secret errors, PVC annotation overrides, node selector fallback, quota disabled/enabled capacity handling, serverless builder selection, secret create/update conflict paths, duplicate names across multiple PVCs, native sidecar init-container restart policy, volume/mount rewrite for app and init containers, and admission patch shape.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/mutate/sidecar.go -->
