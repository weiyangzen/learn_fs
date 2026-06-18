# File Research: sources/cow-pools/openzfs/module/zfs/edonr_zfs.c

## Role

Adapts the Edon-R 512-bit hash implementation to the OpenZFS ABD-backed `zio_checksum` interface and provides salted checksum template setup/free functions.

## Key Functions

- `edonr_incremental()` feeds ABD chunks into `EdonRUpdate()` in bits.
- `abd_checksum_edonr_native()` copies a prepared Edon-R state template, iterates the ABD payload into it, finalizes the digest, and copies the first checksum words into `zio_cksum_t`.
- `abd_checksum_edonr_byteswap()` calls the native checksum path and is intended to publish byteswapped words for opposite-endian checksum handling.
- `abd_checksum_edonr_tmpl_init()` expands the ZFS checksum salt into one full Edon-R block by hashing the salt and then hashing that digest, initializes an Edon-R state, and feeds the expanded salt block as the MAC key/template.
- `abd_checksum_edonr_tmpl_free()` zeroes and frees the template state.

## Research Notes

The salt expansion relies on `EDONR_BLOCK_SIZE == 2 * digest_size` and uses a static assertion for that invariant. One notable implementation detail is that the byteswap function computes a temporary native checksum; the assignment lines should be checked carefully by maintainers because the visible code byteswaps from `zcp->zc_word` rather than from the temporary checksum variable.
