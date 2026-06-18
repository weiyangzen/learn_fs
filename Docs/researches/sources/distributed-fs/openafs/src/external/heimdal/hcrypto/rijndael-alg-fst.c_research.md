# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rijndael-alg-fst.c

Purpose: provides the fast table-based Rijndael/AES block cipher core used by hcrypto AES wrappers.

Important APIs/types/functions: exported routines are `rijndaelKeySetupEnc`, `rijndaelKeySetupDec`, `rijndaelEncrypt`, and `rijndaelDecrypt`. The file contains large precomputed encryption/decryption T-tables, S-box derived tables, inverse tables, and round constants. `GETU32`/`PUTU32` map between byte arrays and 32-bit state words.

Control flow: encryption key setup reads 128/192/256-bit keys, expands round keys using S-box table lookups and `rcon`, and returns 10/12/14 rounds. Decryption setup first creates encryption keys, reverses round-key order, and applies inverse MixColumns to inner round keys. Encrypt/decrypt map a 16-byte block into four state words, add the initial round key, run table-driven full rounds either fully unrolled or looped depending on `FULL_UNROLL`, then perform a final S-box-only round and write 16 output bytes.

State and persistence: no global mutable state exists. Callers own round-key arrays sized for up to `4 * (RIJNDAEL_MAXNR + 1)` words. Tables are static const data.

Dependencies and integration points: includes `rijndael-alg-fst.h`, `krb5-types.h` under `KRB5`, and `config.h`. Higher AES APIs in the hcrypto provider wrap this core for CBC/CFB and Fortuna uses AES through the higher AES interface.

Risks and test signals: table-based AES can leak through cache timing on hostile local platforms, invalid `keyBits` returns zero and callers must handle it, and unaligned word access paths differ by compiler. Tests should cover NIST AES ECB known-answer vectors for 128/192/256-bit keys, decrypt inverse, key setup return values, endian/compiler variants, and provider CBC/CFB vectors.
