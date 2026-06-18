<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/csi-beegfs-connauth.yaml -->
# sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/csi-beegfs-connauth.yaml

Purpose: raw file-system-specific connection auth snippet used by Kustomize/test deployment for non-operator configuration.
Important surface: list entry with `sysMgmtdHost: localhost`, `connAuth: ${BEEGFS_SECRET}`, and intentionally omitted encoding field to verify backwards compatibility.
Control flow/state: no Kubernetes resource kind; it is transformed into a Secret/config artifact elsewhere.
Dependencies/integration: deployment documentation and Kustomize overlays expect this shape.
Risks/test signals: leaving encoding unspecified is deliberate; changing it would reduce backwards-compatibility coverage. Successful driver config parsing is the signal.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/csi-beegfs-connauth.yaml -->
