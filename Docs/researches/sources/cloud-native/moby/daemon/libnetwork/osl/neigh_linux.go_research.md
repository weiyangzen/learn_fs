## sources/cloud-native/moby/daemon/libnetwork/osl/neigh_linux.go

Purpose: Linux neighbor table management for OSL sandboxes, adding and deleting permanent neighbor entries for endpoint reachability.

Important APIs/types/functions: `NeighborSearchError` formats already-present/not-found errors; `Namespace.AddNeighbor`, `Namespace.DeleteNeighbor`, internal `neigh` options holder, and `nlNeigh` for netlink neighbor construction.

Control flow: options set link name and address family. `nlNeigh` creates a permanent `netlink.Neigh`, sets `NTF_SELF` when family is specified, resolves source link names to destination interface names through `findDst`, and fills link index. Add calls `NeighAdd` and maps `os.ErrExist` to `NeighborSearchError`. Delete calls `NeighDel`, maps missing entries to `NeighborSearchError`, and for family-specific bridge entries also tries deleting a dynamic `NTF_MASTER` entry.

State and persistence behavior: mutates namespace neighbor tables. Entries are permanent until deleted or namespace teardown. The file itself stores no persistent Go state.

Dependencies and integration points: uses `Namespace.nlHandle`, OSL interface mapping, vishvananda/netlink, and `NeighOption` functions from `options_linux.go`.

Risks: add/delete must use the same parameters to identify entries. Link-name resolution depends on `Namespace.iFaces` metadata. Bridge family behavior is specialized and may leave dynamic entries if deletion fails. Error mapping depends on netlink errors wrapping `os.ErrExist`/`os.ErrNotExist`.

Test signals: no direct tests in this subset. Integration tests should verify bridge and non-bridge neighbor add/delete, duplicate handling, missing delete handling, and link-specific entries.
