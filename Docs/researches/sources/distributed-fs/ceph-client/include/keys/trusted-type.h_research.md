# sources/distributed-fs/ceph-client/include/keys/trusted-type.h

Source read summary: 106 lines, 2369 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/keys/trusted-type.h` defines trusted-key payload/options structures, common size limits, backend operation callbacks, and trusted-key source selection for TPM, TEE, CAAM, DCP, or PKWM providers.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: `trusted_key_payload`, `trusted_key_options`, `trusted_key_ops`, `trusted_key_source`. Important constants/macros: `MIN_KEY_SIZE`, `MAX_KEY_SIZE`, `MAX_BLOB_SIZE`, `MAX_PCRINFO_SIZE`, `MAX_DIGEST_SIZE`, `TRUSTED_DEBUG`, `pr_fmt`.

Control flow: The trusted key type parses options, selects backend ops, seals/unseals blobs through the active secure hardware/provider, and stores decrypted key material plus sealed blobs in `struct trusted_key_payload`.

State and persistence behavior: Sealed blobs persist in the key payload; decrypted key bytes are in memory while the key is active and must be cleared on destroy. Backend selection is global/configuration-driven.

Dependencies and integration points: It includes `linux/key.h`, `linux/rcupdate.h`, `linux/tpm.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Size limits, PCR/options parsing, RNG quality, backend availability, and secret zeroization are the major risks.

Test signals: Exercise trusted key add/load/update for every enabled backend, PCR policy options, invalid option parsing, and secure cleanup under revoke/destroy.
