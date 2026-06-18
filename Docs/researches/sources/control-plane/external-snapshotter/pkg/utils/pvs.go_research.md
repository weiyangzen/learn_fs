# sources/control-plane/external-snapshotter/pkg/utils/pvs.go

Purpose: provides cache index keys for looking up CSI persistent volumes by driver name and volume handle.

Important APIs/functions: `CSIDriverHandleIndexName`, `PersistentVolumeKeyFunc`, and `PersistentVolumeKeyFuncByCSIDriverHandle`.

Control flow: `PersistentVolumeKeyFunc` returns `driver^volumeHandle` only for non-nil CSI PVs; non-CSI or nil PVs map to the empty string. The component function formats the same key from explicit strings.

State and persistence: stateless; keys are used by informer indexes and lookups.

Dependencies and integration: depends on core `PersistentVolume` types and integrates with snapshot controller logic that needs to map PVC/PV sources to CSI driver handles.

Risks and test signals: separator collisions are theoretically possible if driver names or handles contain `^`; the code assumes CSI handles are safe enough for this indexing use. Tests cover nil, CSI, and hostPath PV inputs.
