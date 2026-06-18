<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/reftype/reftype_test.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/reftype/reftype_test.go

Purpose: validates binary serialization for `RefType`.

Coverage: `ToBytes` maps `Normal` to `{1}` and `Mask` to `{2}`. `FromBytes` accepts those values and rejects an invalid byte and a multi-byte slice.

Dependencies: `testify/require`.

State and integration: no persistence, but it protects the omap value contract used by v1 reftracker.

Risks and gaps: does not assert exact error messages or `Unknown` return on error, and does not test empty byte slice separately from wrong size.

Test signal quality: focused and sufficient for the current two valid encodings.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/reftype/reftype_test.go -->
