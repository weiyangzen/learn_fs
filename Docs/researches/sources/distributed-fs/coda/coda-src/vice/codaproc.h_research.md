# sources/distributed-fs/coda/coda-src/vice/codaproc.h

## Purpose
`codaproc.h` is a small shared header for repair and recursive directory-removal support in the vice server. It declares two C-style parameter blocks used to carry volume, vnode-list, store-id, RPC, and client context through directory enumeration callbacks.

## Important APIs, types, and functions
- `rmBlk` carries a `VListStruct *vlist`, volume ID, `Volume *`, `ViceStoreId *`, and `ClientEntry *` for recursive removes during repairs.
- `semBlk` carries an RPC handle, client pointer, volume pointer, parent fid, and accumulated error code for recursive semantic checking.

## Control flow
The header itself has no functions. Its structs are intended to be filled by caller code before invoking directory traversal helpers whose callback signatures only accept `void *` context. Related implementation in `codaproc.cc` and `treeremove.h` uses similar blocks to pass mutation and semantic-check state through `DH_EnumerateDir`.

## State and persistence behavior
The structs do not own persistent state. They carry borrowed pointers into persistent volume/vnode structures and store IDs, so correctness depends on the caller keeping locks and object lifetimes valid for the traversal.

## Dependencies and integration points
The header assumes prior visibility of `VListStruct`, `Volume`, `ViceStoreId`, `ClientEntry`, `RPC2_Handle`, and `ViceFid`. It is included by vice server repair/reintegration code that already includes the Coda/RPC/volume headers defining those types.

## Risks
Because the header has no include guard in the visible file and no includes of its own, it depends on include order. The callback context structs expose raw pointers and do not encode ownership or lock requirements, so misuse can lead to stale pointers or operations on unlocked vnodes.

## Test signals
Compile coverage through repair and tree-remove code is the main signal. Runtime tests should exercise recursive remove/semantic-check paths, especially nested directories and error propagation through callback context.
