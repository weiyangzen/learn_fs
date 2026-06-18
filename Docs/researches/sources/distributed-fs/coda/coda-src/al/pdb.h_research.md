# sources/distributed-fs/coda/coda-src/al/pdb.h

Purpose: Public header for Coda's protection database layer. It declares the profile structure, ID classification macros, high-level PDB mutation APIs, profile pack/read/write helpers, and low-level database entry points.

Important APIs/types: `PDB_HANDLE`, `PDB_profile`, `PDB_ISUSER`, `PDB_ISGROUP`, `PDB_MAXID_SET`, `PDB_MAXID_FORCE`, high-level `PDB_*` user/group routines, `pdb_pack`, `pdb_unpack`, profile helpers, and `PDB_db_*` persistence routines.

Control flow and state model: The header defines positive IDs as users and negative IDs as groups. `PDB_profile` stores the name, owner metadata for groups, sorted arrays of parent groups, computed CPS, and owned groups or group members. Callers combine this with `PDB_db_open` modes and profile read/write calls to perform mutations.

Persistence and integration: The opaque `PDB_HANDLE` is implemented by `pdbdb.c`; serialization is implemented by `pdbpack.c`; membership arrays are defined in `pdbarray.h`. This header is included by AL, pdbtool, auth support, and server code.

Risks and test signals: The header exposes many internal helpers, so callers can bypass higher-level consistency routines if used carelessly. The flexible ownership semantics of `groups_or_members` depend on testing `PDB_ISGROUP(id)` at runtime.
