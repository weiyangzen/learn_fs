# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/keys.go

Purpose: centralizes component key constants used for labels, annotations, placement, and daemon-specific maps.

Important APIs/types/functions: constants `KeyAll`, `KeyMds`, `KeyRgw`, `KeyMon`, `KeyMonArbiter`, `KeyMgr`, `KeyDashboard`, `KeyOSDPrepare`, `KeyRotation`, `KeyOSD`, `KeyCleanup`, `KeyMonitoring`, `KeyCrashCollector`, `KeyClusterMetadata`, `KeyCephExporter`, and `KeyCmdReporter`.

Control flow: no logic; helpers in labels/annotations use these keys to select component-specific maps.

State and persistence: keys appear in CR specs and generated Kubernetes object metadata.

Dependencies/integration: used across Ceph API and operator reconciliation code.

Risks: changing key strings breaks user specs that already use those map keys.

Test signals: label/annotation tests and CR examples using these keys continue to unmarshal and apply.
