# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/labels.go

Purpose: provides typed label maps, component-specific label selection, object metadata application, and DNS-safe label normalization.

Important APIs/types/functions: `SkipReconcileLabelKey`, `LabelsSpec`, `KeyType`, `Labels`, getters such as `GetMgrLabels`, `GetMonitoringLabels`, `GetCephExporterLabels`, `GetCmdReporterLabels`, `ApplyToObjectMeta`, `OverwriteApplyToObjectMeta`, `Merge`, `ToValidDNSLabel`, and `cutMiddle`.

Control flow: component getters merge `all` labels with component labels. Apply fills absent keys, overwrite apply replaces keys, and `ToValidDNSLabel` lowercases, converts invalid bytes to dashes, prepends `d` for numeric starts, trims dashes, and middle-truncates to DNS-1035 length.

State and persistence: no global state; labels persist on Kubernetes object metadata and affect selectors/reconciliation.

Dependencies/integration: uses Kubernetes validation constants and `metav1.ObjectMeta`.

Risks: `Merge` preserves receiver values despite comments about supplied override; `all` labels win collisions over component labels. DNS conversion operates byte-wise, not Unicode-aware.

Test signals: `labels_test.go` covers merge, apply/overwrite, YAML parsing, DNS conversion, and middle truncation.
