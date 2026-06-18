# sources/distributed-fs/ceph-client/crypto/echainiv.c

## Purpose
`echainiv.c` implements the `echainiv` AEAD geniv template, an encrypted chained IV generator. It derives an IV from a sequence number and salt and places the encrypted IV into the ciphertext/AAD layout used by authenc-style AEADs.

## Important APIs, Types, And Functions
- `echainiv_encrypt()` generates the IV from request IV sequence number and `aead_geniv_ctx` salt, copies source to destination for out-of-place requests, embeds the IV in output, and delegates encryption.
- `echainiv_decrypt()` extracts the IV from input AAD/ciphertext layout and delegates decryption.
- `echainiv_aead_create()` allocates a geniv AEAD instance, requires nonzero IV size aligned to 64-bit words, wires encrypt/decrypt/init/exit, and registers the instance.

## Control Flow
Encryption requires `cryptlen >= ivsize`. It forwards the request to the child AEAD over `req->dst`, with associated data unchanged. It reads a big-endian 64-bit sequence number from the tail of `req->iv`, zeroes the IV buffer, copies the existing IV-sized block into the output after AAD, and then fills each 64-bit IV word by multiplying the salt tail value, forced odd, by the sequence number. Decryption reverses the layout by mapping the IV from source at `assoclen`, then decrypting with `assoclen + ivsize`.

## State And Persistence
Persistent transform state comes from generic AEAD geniv context: child AEAD and salt stored after `struct aead_geniv_ctx`. Per-request state is the embedded child request.

## Dependencies And Integration Points
The file depends on `<crypto/internal/geniv.h>`, AEAD request helpers, scatterwalk, and authenc-like usage where authentication is performed after encryption. It registers the `echainiv` template.

## Risks And Edge Cases
The algorithm assumes block size equals IV size and IV size is a nonzero multiple of 8. It is only suitable for constructions where authentication occurs after encryption; misuse with other AEAD layouts could authenticate the wrong bytes. Sequence-number uniqueness is essential. Scatterlist copying on out-of-place encrypt must preserve AAD and plaintext/ciphertext layout exactly.

## Test Signals
Useful tests include IV-size rejection, cryptlen shorter than IV, in-place and out-of-place encrypt, decrypt IV extraction from AAD extension, and authenc integration tests that verify authentication covers the generated IV.
