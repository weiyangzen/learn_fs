# File Research: sources/cow-pools/openzfs/module/zfs/skein_zfs.c

## Summary
Provides ABD-backed Skein MAC checksum support for ZFS.

## Main Responsibilities
- Computes native 256-bit Skein MAC checksums over ABD buffers.
- Provides a byteswapped checksum wrapper.
- Allocates and frees salted Skein context templates.

## Key APIs
- `abd_checksum_skein_native()`.
- `abd_checksum_skein_byteswap()`.
- `abd_checksum_skein_tmpl_init()`.
- `abd_checksum_skein_tmpl_free()`.

## Important Behavior
The native checksum requires a non-NULL context template. Each checksum copies the template, iterates ABD chunks through `Skein_512_Update()`, finalizes into `zio_cksum_t`, and clears the working context. Template initialization uses `Skein_512_InitExt()` with the checksum salt as key material.

## Risks
Callers must provide the template created by `abd_checksum_skein_tmpl_init()`. Contexts are explicitly zeroed before free or after use; that cleanup is part of the security-sensitive MAC handling.
