# sources/control-plane/external-snapshotter/pkg/utils/pvs_test.go

Purpose: unit-tests persistent volume CSI index key generation.

Important APIs/functions: `TestPersistentVolumeKeyFunc`.

Control flow: builds a CSI PV, a hostPath PV, and a nil PV case, then compares `PersistentVolumeKeyFunc` output with expected keys.

State and persistence: no external state.

Dependencies and integration: depends on core PV API types and validates keys used by informer indexes.

Risks and test signals: confirms non-CSI volumes do not pollute the CSI index; does not test the component helper directly or unusual characters in handles.
