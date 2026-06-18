# sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_caam.c

## Purpose

`trusted_caam.c` implements the trusted-key backend for NXP CAAM blob generation. It seals trusted key payloads into CAAM blobs tied to hardware and can also expose protected-key material for consumers expecting CAAM pkey metadata plus the blob.

## Important APIs, Types, and Functions

`trusted_key_caam_ops` provides `.init`, `.seal`, `.unseal`, and `.exit` callbacks with `.migratable = 0`. `trusted_caam_init()` obtains a CAAM blob generator with `caam_blob_gen_init()` and registers `key_type_trusted`; `trusted_caam_exit()` unregisters and releases the blobifier. `trusted_caam_seal()` calls `caam_encap_blob()`, and `trusted_caam_unseal()` calls `caam_decap_blob()` unless protected-key mode is requested. `get_pkey_options()` parses `key_enc_algo=...`, and `is_key_pkey()` detects a `pk` option in the datablob tail.

## Control Flow

The common trusted core chooses this backend and calls `.init`. For a new key, the core fills `p->key`; CAAM seal builds a `caam_blob_info` with key modifier `SECURE_KEY`, optional protected-key metadata, and output buffer `p->blob`. On success it records `p->blob_len`; in protected-key mode it rewrites `p->key` as `struct caam_pkey_info` followed by the blob. For load, unseal either returns protected-key metadata plus blob without decrypting, or decapsulates the CAAM blob into the payload key.

## State and Persistence Behavior

The backend keeps one global `blobifier` handle. Payload persistence is the sealed CAAM blob stored in `trusted_key_payload.blob`; protected-key mode stores provider metadata in the key payload visible to kernel consumers. Keys are non-migratable because CAAM blobs are tied to the local hardware/key modifier.

## Dependencies and Integration Points

Dependencies include `<soc/fsl/caam-blob.h>`, CAAM blob-gen support, key type registration, and trusted-key core static calls. It is selected by `CONFIG_TRUSTED_KEYS_CAAM`.

## Risks and Test Signals

The protected-key parser currently returns success on option parse failure in two branches, which is behavior worth preserving or reviewing carefully. Other risks are blob size assumptions, hardware binding surprises, and returning blob-backed key material with the wrong length. Test with normal and `pk` datablobs, unsupported `key_enc_algo`, CAAM probe failure, and keyctl load/read cycles across reboot or hardware state changes.
