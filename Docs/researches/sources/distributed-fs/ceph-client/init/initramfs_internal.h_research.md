# sources/distributed-fs/ceph-client/init/initramfs_internal.h

## Purpose
This small internal header exposes the initramfs extractor to nearby init code and tests without making it a broad public kernel API.

## Important APIs, Types, And Functions
- `char *unpack_to_rootfs(char *buf, unsigned long len);` declares the extractor implemented by `initramfs.c`.
- `CPIO_HDRLEN` defines the fixed 110-byte `newc` cpio header length used by the extractor and its KUnit tests.

## Control Flow
There is no runtime logic. Including files compile against the extractor contract and agree on header sizing.

## State And Persistence
No state is stored here. The persistence behavior belongs to `initramfs.c`, which creates rootfs entries.

## Dependencies And Integration Points
`initramfs_test.c` includes this header to build synthetic cpio records with the same header length as production code. `initramfs.c` includes it for its exported internal prototype.

## Risks And Edge Cases
Changing `CPIO_HDRLEN` would desynchronize archive packing/parsing assumptions. Exposing `unpack_to_rootfs()` here is intentionally narrow; making it more public would invite use outside early init constraints.

## Test Signals
The header is covered when `initramfs_test.c` compiles and when synthetic cpio streams align with production parsing.
