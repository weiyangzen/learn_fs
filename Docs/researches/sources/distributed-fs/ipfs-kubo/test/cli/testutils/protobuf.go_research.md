# sources/distributed-fs/ipfs-kubo/test/cli/testutils/protobuf.go

Purpose: estimates protobuf serialized sizes for dag-pb directory links, enabling tests to construct directories near block-size thresholds.

Important APIs: `VarintLen(v uint64) int` estimates protobuf varint byte length using `math/bits`. `LinkSerializedSize(nameLen, cidLen int, tsize uint64) int` computes a PBLink's wrapper and inner-field size. `EstimateFilesForBlockThreshold(threshold, nameLen, cidLen int, tsize uint64) int` estimates how many links fit under a block threshold, assuming four bytes of base overhead.

Control flow: size calculation adds field tags, varint lengths, raw CID/name bytes, and Tsize encoding, then divides the remaining threshold by per-link size.

State and persistence: no state.

Dependencies and integration points: mirrors sizing logic from boxo UnixFS directory code and supports CLI tests for UnixFS/HAMT/block threshold behavior.

Risks and test signals: this is an estimate tied to dag-pb encoding details and the empirically chosen base overhead. If upstream serialization changes, threshold tests using this helper may drift and require recalibration.
