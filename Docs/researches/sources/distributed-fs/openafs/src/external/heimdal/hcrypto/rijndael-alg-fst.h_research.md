# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rijndael-alg-fst.h

Purpose: declares the fast Rijndael/AES core API and maximum key/block/round constants.

Important APIs/types/functions: defines `RIJNDAEL_MAXKC`, `RIJNDAEL_MAXKB`, and `RIJNDAEL_MAXNR`; renames `rijndaelKeySetupEnc`, `rijndaelKeySetupDec`, `rijndaelEncrypt`, and `rijndaelDecrypt`; declares key setup and single-block encrypt/decrypt prototypes.

Control flow: callers prepare an encryption or decryption round-key array, then pass it with the returned round count to block operations.

State and persistence: no state is declared except caller-owned round-key arrays.

Dependencies and integration points: used by `rijndael-alg-fst.c` and AES provider wrappers.

Risks and test signals: callers must allocate sufficient round-key space and respect valid AES key sizes. Compile coverage and AES known-answer vectors validate integration.
