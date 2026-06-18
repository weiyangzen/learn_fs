<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/entry.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/msg/entry.go

Purpose: defines BeeGFS entry/metadata BeeMsg payloads and wire serializers for directory creation, file unlink, directory listing, owner lookup, entry info, stripe pattern manipulation, file state changes, refresh, and lookup intent. It is a protocol-bound file: field order, integer widths, C-string alignment, and message IDs must match BeeGFS C++/kernel expectations.

Important APIs/types/functions: request/response structs implement `MsgId`, `Serialize`, or `Deserialize` for message IDs 2001/2002, 2007/2008, 2029/2030, 2035/2036, 2045/2046, 2047/2048, 2053/2054, 2123/2124, 2131/2132, 2055/2056, and 2059/2060. Shared protocol types include `EntryInfo`, `EntryInfoWithDepth`, `Path`, `StripePattern`, `PathInfo`, and `RemoteStorageTarget`. `SetDirPatternRequest.SetUID/GetUID` hides the UID field so the feature flag cannot be forgotten.

Control flow: serializers write primitive fields through `beeserde`, nested structs serialize themselves, and some messages set serializer feature flags while writing optional data. Deserializers read the same order and fail through `Deserializer.Fail` on unsupported states such as RAID10 patterns, missing pool IDs, unsupported RST versions, or non-basic lookup-intent response flags. `GetEntryInfoResponse` composes `StripePattern`, `PathInfo`, `RemoteStorageTarget`, session counts, and file state.

State and persistence: no local persistence; all state is transient wire payload state. `EntryInfo` includes `structs.HostLayout` and is also consumed by ioctl code, so its layout is a cross-package ABI surface. `StripePattern.Serialize` backfills its own length after writing the pattern body. `RemoteStorageTarget.Serialize` mutates private version fields when RST intent is present, including the important distinction between nil and empty `RSTIDs`.

Dependencies and integration points: depends on `common/beegfs` enums and `beeserde`; integrates with `util.AssembleBeeMsg`, `NodeStore` RPCs, and ioctl `GetEntryInfoV2` which manually assembles the same `GetEntryInfoResponse` shape. Comments explicitly note incomplete support for file events, buddy mirror secondary flags, RAID10, non-basic lookup intents, and some mkdir/unlink optional fields.

Risks: exact wire order is fragile; C layout coupling makes field reordering dangerous. `ListDirFromOffsetResponse` checks sequence lengths with `typesLen != entryIDsLen && entryIDsLen != namesLen`, which only fails when both comparisons are true and may miss a mismatch between types and IDs if IDs and names match. Unsupported legacy patterns/RST versions intentionally fail. Optional feature flag behavior must stay synchronized with header backfill in `AssembleBeeMsg`.

Test signals: `entry_test.go` round-trips representative RAID0/BuddyMirror stripe patterns and uses reflection to guard `RemoteStorageTarget` field count/order/kinds, but most individual messages rely on integration tests or protocol compatibility rather than direct unit coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/entry.go -->
