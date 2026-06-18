# sources/distributed-fs/ceph-client/crypto/xctr.c

## Purpose
This file implements the `xctr(...)` skcipher template, a CTR-like XOR-counter mode used by HCTR2. It encrypts `IV XOR little-endian counter` rather than `IV + counter`.

## Important APIs, Types, And Functions
`crypto_xctr_crypt()` is both encrypt and decrypt because the mode is a stream cipher. `crypto_xctr_crypt_segment()` handles out-of-place full blocks, `crypto_xctr_crypt_inplace()` handles in-place full blocks with an aligned temporary keystream buffer, and `crypto_xctr_crypt_final()` handles the final partial block. `crypto_xctr_create()` builds the skcipher instance and restricts child ciphers to 16-byte blocks.

## Control Flow
The skcipher walk is configured with `chunksize` equal to the child block size so partial blocks appear only at the end. For each block, the code XORs the low 32 bits of the IV with a little-endian block counter, encrypts the modified IV, XORs the keystream with input, restores the IV by XORing the same counter again, and increments the counter. The byte counter tracks continuity across walk segments.

## State, Dependencies, Integration, Risks, And Tests
The request IV is mutated temporarily but restored after each block, so no persistent counter state remains after completion. Dependencies are skcipher template helpers, simple cipher spawns, and CryptoAPI walk helpers. Risks include 32-bit block counter wrap for very large requests, IV restoration bugs across partial/error paths, and the hard-coded 16-byte limitation. Test signals are HCTR2/XCTR vectors, segmented scatterlist tests, in-place/out-of-place parity, partial-tail tests, and invalid child blocksize tests.
