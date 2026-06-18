# sources/compression/zlib/contrib/minizip/crypt.h

Purpose: implements Traditional PKWARE ZIP encryption helpers used by minizip when crypting support is enabled.

Important APIs/types/functions: macro `CRC32`, static helpers `decrypt_byte`, `update_keys`, `init_keys`, macros `zdecode` and `zencode`, and optional `crypthead()` under `INCLUDECRYPTINGCODE_IFCRYPTALLOWED`.

Control flow: key initialization starts from three constants and updates them for each password byte. Decoding XORs a ciphertext byte with the pseudo-random byte and updates keys with plaintext. Encoding computes the pseudo-random byte, updates keys with plaintext, and returns ciphertext. `crypthead()` seeds `rand()`, creates encrypted random header bytes, appends encrypted CRC high bytes, and returns header length.

State and persistence: encryption keys are caller-provided arrays. `crypthead()` uses static `calls` and process-global `rand()` seed/state.

Dependencies/integration: depends on zlib CRC table type `z_crc_t`, time/rand functions when crypt header code is included, and minizip `zip.c`/`unzip.c` encryption paths.

Risks: Traditional PKWARE encryption is weak and explicitly not AES/strong encryption. `rand()` is predictable and global. The code notes potential 16-bit overflow concerns. Defining `NOCRYPT`/`NOUNCRYPT` can remove support.

Test signals: should be covered by encrypted ZIP create/extract fixtures; no such tests are in this subset.
