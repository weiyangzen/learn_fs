# File Research: sources/block-storage/cryptsetup/lib/luks1/af.c

This file implements the LUKS1 anti-forensic splitter.

Core functions:
- `XORblock` XORs two byte buffers into a destination buffer.
- `hash_buf` hashes a big-endian block index IV followed by source data, producing a digest-sized or padding-sized output.
- `diffuse` spreads information across a block by hashing digest-sized chunks and a final partial chunk.
- `AF_split` expands one block of key material into `blocknumbers` stripes:
  - Generates random stripes for all but the last stripe.
  - XORs each random stripe into an accumulator.
  - Diffuses the accumulator after each random stripe.
  - Computes the final stripe as `src XOR accumulator`.
- `AF_merge` reverses the process:
  - Replays XOR+diffuse across all but the last stripe.
  - XORs the final stripe with the accumulator to recover the original block.
- `AF_split_sectors` computes the sector-rounded size of split data.

Filesystem/block-storage relevance:
- LUKS1 stores encrypted key material in anti-forensic stripes, so securely destroying enough stripe data destroys recoverability of the keyslot.
- The sector-rounded size is used for keyslot area layout on the metadata device.

Important notes:
- Temporary accumulator buffers use `crypt_safe_alloc` and `crypt_safe_free`.
- Hash failures propagate as negative errors.
- The code assumes caller supplies matching `blocksize`, `blocknumbers`, and hash for split and merge.
