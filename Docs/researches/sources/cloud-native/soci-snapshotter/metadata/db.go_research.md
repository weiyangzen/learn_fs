# sources/cloud-native/soci-snapshotter/metadata/db.go

Purpose: bbolt schema and low-level serialization helpers for filesystem metadata derived from a ztoc TOC. It stores node attributes separately from parent/child and tar-offset metadata.

Important APIs/types/functions: bucket keys define the schema under `filesystems/<fsID>/nodes` and `filesystems/<fsID>/metadata`. `childEntry` and `metadataEntry` hold in-memory build state. Accessors include `getNodesBucket`, `getMetadataBucket`, `getNodeBucketByID`, and `getMetadataBucketByID`. Writers/readers include `writeNodeEntry`, `readNodeEntryToAttr`, `readNumLink`, `readChild`, `writeMetadataEntry`, and `getMetadataEntry`. Numeric helpers include `encodeID`, `decodeID`, `putInt`, and `encodeUint`.

Control flow: node attributes are stored sparsely, omitting zero values. Xattrs and children optimize the first entry as direct keys and store extra entries in sub-buckets. Metadata entries write tar name, tar header offsets/sizes, and uncompressed offsets. Reads iterate bucket keys and reconstruct `Attr` or metadata values.

State and persistence: persists filesystem metadata in a bbolt database. IDs are four-byte big-endian keys, integer values use varint/uvarint encoding, and modtime uses `time.GobEncode`. NumLink is stored as `NumLink-1`, making a missing/zero DB value mean one link.

Dependencies/integration points: used by `reader.go` to build and query metadata from ztoc entries. Depends on bbolt, `dbutil.EncodeInt`, `ztoc/compression.Offset`, and `metadata.Attr`.

Risks: sparse zero-value encoding means zero-valued attributes and missing attributes are indistinguishable. First xattr/child selection is map-iteration dependent, though extra children are sorted by base before writing. `readNodeEntryToAttr` stores xattr byte slices directly from bbolt values, which should not be retained past the transaction boundary unless copied. `decodeID` assumes a valid four-byte slice.

Test signals: metadata utility tests indirectly validate attributes, xattrs, child lookup, hardlinks, directory children, modes, device nodes, and link counts through the public Reader.
