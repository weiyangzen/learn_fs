## sources/control-plane/longhorn/chart/Chart.yaml

### Purpose
`Chart.yaml` defines the Longhorn Helm chart metadata.

### Important APIs, Types, And Functions
The chart is API version `v1`, named `longhorn`, with chart `version` and `appVersion` `1.12.0-dev`. It requires Kubernetes `>=1.25.0-0`, describes Longhorn as a distributed block storage system, lists keywords, project home, source repositories for Longhorn components, maintainer contact, and CNCF-hosted icon URL.

### Control Flow
Helm reads this metadata during chart packaging, dependency display, install validation, and repository indexing.

### State, Persistence, And Dependencies
The file persists release metadata for the chart. It depends on Helm chart schema, semantic versioning conventions, and valid component repository URLs.

### Integration Points
Chart packaging, Rancher catalog/app displays, and release workflows consume this metadata. Version fields should align with image tags and generated manifests.

### Risks
Version/appVersion drift can publish misleading charts. `apiVersion: v1` is older Helm chart metadata format. Kubernetes version constraints must stay aligned with actual template/API requirements.

### Test Signals
`helm lint`, chart packaging, install tests on supported Kubernetes versions, and release checks should validate this file.
