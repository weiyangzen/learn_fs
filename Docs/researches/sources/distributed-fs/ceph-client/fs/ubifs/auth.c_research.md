# sources/distributed-fs/ceph-client/fs/ubifs/auth.c

## Purpose
This file implements UBIFS authentication helpers: node hashes, HMAC insertion/verification, authentication-node preparation, superblock signature verification, key setup, and cleanup.

## Important APIs, Types, and Functions
Important functions include `__ubifs_node_calc_hash()`, `ubifs_prepare_auth_node()`, `__ubifs_hash_get_desc()`, `ubifs_bad_hash()`, `__ubifs_node_check_hash()`, `ubifs_sb_verify_signature()`, `ubifs_init_authentication()`, `__ubifs_exit_authentication()`, `__ubifs_node_insert_hmac()`, `__ubifs_node_verify_hmac()`, `__ubifs_shash_copy_state()`, `ubifs_hmac_wkm()`, and `ubifs_hmac_zero()`. It uses `crypto_shash`, logon keys, PKCS#7 verification, and fixed-size UBIFS hash/HMAC arrays.

## Control Flow and State
Initialization validates `auth_hash_name`, maps it to a hash algorithm, builds `hmac(<hash>)`, requests the configured logon key, allocates hash and HMAC transforms, checks digest sizes against UBIFS limits, sets the HMAC key from the key payload, marks `c->authenticated`, and creates the running log hash descriptor. Node hash calculation covers the node length from the common header. Auth-node preparation finalizes a copied hash state, HMACs that digest, fills `UBIFS_AUTH_NODE`, and prepares the UBIFS node header.

HMAC insertion/verification hashes a node excluding magic/CRC and the embedded HMAC field, using constant-time comparison for verification. Superblock signature verification scans behind the superblock node for a `UBIFS_SIG_NODE`, validates length/type, and verifies a PKCS#7 signature over the superblock.

## Persistence, Dependencies, and Integration
Authentication state lives in `ubifs_info` crypto transforms and descriptors, while hashes/HMACs/signatures are persisted in UBIFS on-flash nodes. Dependencies include the kernel crypto API, keyrings, asymmetric verification, UBIFS scan/read/write node helpers, and mount-time superblock handling.

## Risks and Test Signals
Risks include wrong key type or revoked key handling, digest size mismatch, HMAC offset mistakes, non-constant comparisons, malformed signature nodes, and failing to clean transforms on partial init errors. Tests should mount authenticated images with correct/wrong keys, corrupt node hashes/HMACs, validate PKCS#7 signed superblocks, exercise memory-failure paths, and run fuzzed scan data through signature parsing.
