# sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-custom.h

## Purpose

`sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-custom.h` declares custom XDR routines that replace recursive rpcgen handling for selected GlusterFS directory response lists. The source was read as a complete 21-line file for this report.

## Important APIs, Types, and Functions

The header declares `xdr_gfx_dirlist_custom`, `xdr_gfx_readdir_rsp_custom`, `xdr_gfx_dirplist_custom`, and `xdr_gfx_readdirp_rsp_custom`.

## Control Flow

There is no runtime flow in the header. Including code receives prototypes for custom encode/decode procedures that match the `xdrproc_t` style used by SunRPC XDR.

## State and Persistence Behavior

No state is owned here. The declared functions operate on caller-provided `XDR` streams and generated objects.

## Dependencies and Integration Points

It includes `<rpc/xdr.h>`, generated `glusterfs4-xdr.h`, and `rpc-pragmas.h`. It is included by `glusterfs3.h` and built into `libgfxdr`.

## Risks and Edge Cases

Prototype drift from the implementation or generated types breaks custom XDR substitution. Because this header includes warning-suppression pragmas, include placement can affect diagnostics in downstream files.

## Test Signals

Compile/link coverage of `xdr-custom.c` and any generated protocol code using these prototypes is the main signal, followed by readdir/readdirp round-trip tests.
