# sources/control-plane/csi-driver-nfs/charts/v3.0.0/csi-driver-nfs/Chart.yaml

Purpose: Helm metadata for CSI NFS chart v3.0.0.

Important APIs/types/functions: Helm v1 chart fields with `appVersion: v3.0.0`, `name: csi-driver-nfs`, and `version: v3.0.0`.

Control flow: Static packaging metadata; Helm reads it during chart install/package/index operations.

State and persistence: Stored in chart package and Helm release history.

Dependencies and integration points: Associates the v3.0.0 templates with the v3 NFS plugin and sidecar defaults.

Risks: Still uses chart API v1, and install compatibility depends on rendered templates rather than metadata. Test signals: `helm lint`, repository index validation, and dry-run install.
