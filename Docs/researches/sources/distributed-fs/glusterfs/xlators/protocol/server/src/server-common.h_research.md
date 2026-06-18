# sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-common.h

## Purpose

`server-common.h` declares the version 4 response post-processing helpers implemented in `server-common.c`.

## Important APIs, types, and functions

The declarations cover response fill helpers for readlink, statfs, locks, directory reads, checksums, rename, open, read, create, common iatt response shapes, entry removal, lookup, link, lease, and no-inode variants. These functions operate on generated `gfx_*` response structs, `server_state_t`, `call_frame_t`, `xlator_t`, inode/fd objects, iatts, statvfs, dirent lists, flock/lease structures, and xdata dictionaries.

## Control flow

Server RPC FOP callback implementations include this header and call the relevant `server4_post_*()` helper just before serializing a response. The header separates protocol response shaping from the large generated FOP request/response logic.

## State and persistence behavior

The header declares functions that may mutate inode links and fdtable state, but it owns no state itself.

## Dependencies and integration points

It includes `server.h`, `glusterfs3.h`, compatibility errno support, and server message IDs, with optional GNFS XDR support under `BUILD_GNFS`. It integrates `server-common.c` with versioned server RPC FOP files.

## Risks and test signals

The public helper signatures must remain synchronized with generated XDR types and callback code. Compile failures are the first signal for signature drift. Runtime tests should exercise every helper indirectly through the corresponding FOP response.
