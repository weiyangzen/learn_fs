<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/FindLinkOwnerMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/FindLinkOwnerMsg.h

### Purpose
`FindLinkOwnerMsg` asks metadata storage to find the stored link owner for a given entry ID. The file comment notes that this owner is only a hint because saved link-owner information may be stale or incorrect.

### Important APIs, Types, And Functions
The message subclasses `SimpleStringMsg`, using `NETMSGTYPE_FindLinkOwner` and the entry ID string as the payload. `getEntryID()` returns a `std::string` copy of `getValue()`.

### Control Flow
Construction either wraps an existing `std::string` for send or creates an empty deserialization instance. All wire encoding is inherited from `SimpleStringMsg`.

### State, Persistence, And Dependencies
The only message state is the transient string payload. It depends on `SimpleStringMsg` and the NetMessage type registry.

### Integration Points
Lookup/repair code can use this request before deciding which metadata node should own a hardlink or directory entry relationship.

### Risks
Because the owner is documented as a hint, callers must not treat a successful response as authoritative without fallback checks. Tests should verify string round-trip, empty/invalid entry ID handling by receivers, and compatibility with the paired response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/FindLinkOwnerMsg.h -->
