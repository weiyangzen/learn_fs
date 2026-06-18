<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/volid_test.go -->
## sources/control-plane/ceph-csi/internal/util/volid_test.go

Purpose: verifies one canonical CSI ID compose/decompose round trip.

Coverage: fixture includes `LocationID 0xffff`, encoding version `0xffff`, a 36-byte cluster ID, and a 36-byte object UUID. Test asserts composed string equality and decomposed struct equality.

Dependencies: Go testing package only.

Integration: protects the field order and hex widths expected by CSI volume handles and related tools.

Risks and gaps: only one fixture. No negative tests for overflow, malformed hex, bad UUID length, missing separators, short strings, max length, default version, or negative location id.

Test signal quality: basic format guard, but edge-case coverage is sparse.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/volid_test.go -->
