# sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-common.h

## Purpose

`client-common.h` declares the protocol/client v2 marshalling and unmarshalling API. It is the contract between high-level client fop handlers in `client-rpc-fops_v2.c`, fd/reopen helpers, and the generated `gfx_*` XDR protocol types.

## Important APIs, types, and functions

- Common response decoders are declared for dictionary, one-iatt, two-iatt, three-iatt, and common response shapes.
- Request builders are declared for path-based fops (`stat`, `lookup`, `mknod`, `mkdir`, `rename`, `link`, xattrs, locks, lease, put) and fd-based fops (`readv`, `writev`, `flush`, `fsync`, `fstat`, `ftruncate`, fd locks, readdir, allocation, seek, copy-file-range).
- Post-decoders are declared for readv, create, lease, lk, readdir, readdirp, and rename.
- `set_fd_reopen_status()` is exported so lock callbacks and error paths can report whether an fd can be reopened after anonymous-fd fallback.

## Control flow

The header itself has no runtime control flow. Its shape shows the intended two-stage fop pipeline: a `client_pre_*_v2()` function prepares an XDR request, `client_submit_request()` sends it, and a callback decodes with either a common post helper or an fop-specific `client_post_*_v2()` function before `CLIENT_STACK_UNWIND()`.

## State and persistence behavior

The header defines no storage. Ownership conventions are implicit in the signatures: request builders fill caller-owned `gfx_*_req` structs and may allocate XDR dictionary buffers inside them; response decoders allocate or fill caller-owned output structures and pass dictionary references back through `dict_t **`.

## Dependencies and integration points

It includes `<glusterfs/dict.h>`, `glusterfs3.h`, and `client.h`, binding this API to Gluster dicts, protocol XDR structures, fop frame-local state, fd contexts, and `enum gf_fd_reopen_status`. It is included by `client-rpc-fops_v2.c`, `client-helpers.c`, and other client protocol files needing the v2 conversion API.

## Risks and edge cases

- The API surface is broad and manually kept in sync with `client-common.c`; prototype drift would be caught only by compilation.
- Several functions take mutable request structs plus borrowed pointers, so callers must respect the allocate-submit-free lifecycle.
- The distinction between `dict_t *xdata` and `dict_t **xdata` in request builders matters: writev/copy-file-range can mutate or allocate xdata in test paths, while most builders only serialize an existing dict.
- The header names these as "version 4" functions while symbols use `_v2`, reflecting Gluster protocol naming history that can confuse maintainers.

## Test signals

Build coverage with all fop handlers enabled is the primary interface test. Runtime tests should verify each declared pre/post helper is exercised through its corresponding actor in `clnt4_0_fop_actors`, with sanitizers or leak checks around XDR dictionary allocation/free paths.
