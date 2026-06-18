<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_test.go -->
# sources/cloud-native/containerd/core/mount/mount_test.go

Purpose: platform-neutral tests for read-only mount rewriting and temporary overlay option filtering.

Important APIs/types/functions: `TestReadonlyMounts` and `TestRemoveVolatileTempMount`.

Control flow: tests table-driven input mount slices and expected output slices using `reflect.DeepEqual`; the volatile tests also verify original input slices are not modified when `RemoveVolatileOption` copies.

State and persistence: no external state.

Dependencies and integration points: validates helpers used by `WithReadonlyTempMount` and `WithTempMount` before real mounting occurs.

Risks covered: overlay read-only conversion removes `upperdir`/`workdir` and prepends upperdir to lowerdir; normal mounts normalize `ro`; overlay-only volatile stripping leaves non-overlay options intact.

Test signals: does not cover `RemoveIDMapOption` directly and does not exercise `Mount.Mount`; those are covered elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_test.go -->
