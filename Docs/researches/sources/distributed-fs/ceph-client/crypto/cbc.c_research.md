<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cbc.c -->
# sources/distributed-fs/ceph-client/crypto/cbc.c

## Purpose

`cbc.c` implements the CBC block cipher mode template for the linear skcipher API. It wraps a block cipher-like lskcipher child and provides encrypt/decrypt operations with IV chaining.

## Important APIs, Types, and Flow

Encryption has separate segment and in-place paths. Out-of-place encryption XORs each plaintext block into the IV buffer, encrypts the IV into destination, then updates IV from ciphertext. In-place encryption XORs each source block with the current IV, encrypts in place, and updates the original IV from the final ciphertext block.

Decryption also has segment and in-place paths. Out-of-place decryption decrypts each block then XORs with the previous IV/ciphertext, finally storing the last input ciphertext block as the new IV. In-place decryption walks backward from the last complete block so previous ciphertext is still available for XOR, saving the last ciphertext as the updated IV.

`crypto_cbc_create()` allocates a simple lskcipher instance, requires power-of-two block size and zero child state size, installs CBC encrypt/decrypt callbacks, and registers the template instance.

## State, Dependencies, and Integration

State is the mutable IV passed by callers; the transform context stores the child lskcipher pointer allocated by template helpers. Dependencies are internal skcipher APIs, `crypto_xor()`, and lskcipher template allocation. It integrates as the `cbc(...)` template.

## Risks and Test Signals

Risks include partial-block handling, `FINAL` returning `-EINVAL` on remainders, in-place backward decrypt correctness, IV update semantics, and rejection of stateful children. Test signals are CBC known-answer vectors, multi-call partial updates, in-place and out-of-place equivalence, invalid final lengths, and IV chaining after calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cbc.c -->
