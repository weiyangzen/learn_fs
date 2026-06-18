# sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/Chart.yaml

Purpose: Helm metadata for CSI NFS chart 4.12.0.

Important APIs/types/functions: `apiVersion: v1`, `appVersion: 4.12.0`, `description: CSI NFS Driver for Kubernetes`, `name: csi-driver-nfs`, and `version: 4.12.0`.

Control flow: Static chart metadata only; Helm uses it for package identity, repository index entries, install/upgrade records, and chart dependency bookkeeping.

State and persistence: No runtime Kubernetes state. Metadata is persisted in chart archives and Helm release history.

Dependencies and integration points: Connects the v4.12.0 chart directory to the CSI NFS application release; the rest of the v4.12.0 templates and values are outside this work item except where Helm reads the metadata.

Risks: Version format remains no-`v` like 4.11.0, which differs from older directories. Test signals: `helm lint`, `helm package`, repository index validation, and upgrade dry-run from 4.11.0.
