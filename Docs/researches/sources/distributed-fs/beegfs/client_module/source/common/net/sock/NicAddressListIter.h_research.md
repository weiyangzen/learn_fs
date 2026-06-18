# sources/distributed-fs/beegfs/client_module/source/common/net/sock/NicAddressListIter.h

Purpose: Provides a typed BeeGFS wrapper around `PointerListIter` for NIC address/stat records.

Important APIs/types/functions: The inline surface is NicAddressListIter_init, NicAddressListIter_next, NicAddressListIter_value, NicAddressListIter_end. It preserves type names for callers while delegating storage and iteration mechanics to the common pointer-list implementation.

Control flow: Initialization prepares the embedded list/iterator, append/prepend/remove/move operations forward to `PointerList`, and iterator helpers advance or expose typed values. For connection lists, moving/removing also maintains `PooledSocket` pool metadata where required.

State and persistence behavior: State is in-memory list membership only. Ownership depends on the caller-supplied `owner` flag or external cleanup conventions; there is no persistence beyond the client process.

Dependencies and integration points: Used by NIC discovery/stats, connection pools, pooled sockets, and node connection selection.

Risks: Typed wrappers do not add deep validation; stale iterators, double removal, or wrong ownership cleanup can corrupt list state or leak sockets/address objects.

Test signals: List length, append/remove, iterator removal, owner cleanup, and socket pool metadata updates.
