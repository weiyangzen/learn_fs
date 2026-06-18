<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/pod_with_gev.yaml -->
# sources/control-plane/longhorn/examples/pod_with_gev.yaml

Purpose: example pod using a Generic Ephemeral Volume backed by Longhorn.

Important APIs/types/functions: Pod `volume-test` defines `volumes[].ephemeral.volumeClaimTemplate` with RWO Longhorn storage request, mounts it at `/data`, and probes `/data/lost+found`.

Control flow: Kubernetes creates an ephemeral PVC for the pod, Longhorn provisions the volume, kubelet mounts it, and deletion of the pod triggers cleanup according to ephemeral volume ownership.

State and persistence: data is tied to the pod lifecycle rather than a user-managed PVC.

Dependencies/integration points: depends on Kubernetes generic ephemeral volume support and Longhorn dynamic provisioning.

Risks/test signals: data is not durable beyond pod lifecycle. Test signals are ephemeral PVC creation/owner references, pod mount success, and cleanup after pod deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/pod_with_gev.yaml -->
