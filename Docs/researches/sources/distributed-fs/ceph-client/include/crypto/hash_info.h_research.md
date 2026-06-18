# sources/distributed-fs/ceph-client/include/crypto/hash_info.h

Purpose: hash algorithm metadata constants and lookup arrays.

Important APIs/types/functions: digest-size constants for RIPEMD, Whirlpool, Tiger, and SM3-256 not defined elsewhere; external arrays `hash_algo_name` and `hash_digest_size`.

Control flow: consumers index arrays by `HASH_ALGO_*` IDs from UAPI to map IDs to names and digest lengths.

State and persistence: arrays are read-only global metadata defined elsewhere.

Dependencies and integration points: includes SHA, MD5, Streebog, and UAPI hash info headers. Used by integrity, signature, and key subsystems that serialize hash algorithm IDs.

Risks: array ordering must match UAPI `HASH_ALGO__LAST`; mismatches break ABI interpretation of signatures or measurements.

Test signals: compile-time/boot checks for array length, integrity subsystem tests, and hash ID/name/digest-size mapping tests.
