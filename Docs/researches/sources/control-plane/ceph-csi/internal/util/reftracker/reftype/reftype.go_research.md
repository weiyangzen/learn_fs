<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/reftype/reftype.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/reftype/reftype.go

Purpose: defines on-disk reference type encoding for reftracker omap values.

APIs and types: `RefType` is an `int8` enum with `Unknown`, `Normal`, and `Mask`. `Normal` contributes to refcount and can be removed or converted to mask. `Mask` does not contribute to refcount and prevents future `Add` calls from re-counting the same key until removed with `Normal`. `ToBytes` encodes one byte; `FromBytes` validates one-byte length and known values.

State and persistence: serialized values are stored in reftracker object omap entries keyed by reference id.

Dependencies: uses reftracker `errors.UnexpectedReadSize` and `fmt` for unknown enum diagnostics.

Integration points: v1 add/remove code serializes `Normal` and `Mask`, and read paths parse omap values through `FromBytes`.

Risks: the v1 layout comment says omap type is `uint32`, but the implementation stores one byte. Compatibility depends on this implementation and tests, so future layout changes should use explicit versioning.

Test signals: `reftype_test.go` covers byte encoding for normal/mask and errors for unknown/wrong-sized inputs.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/reftype/reftype.go -->
