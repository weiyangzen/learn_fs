# sources/distributed-fs/ceph-client/arch/s390/kernel/cert_store.c

## Purpose
Implements s390 DIAG 0x320 certificate-store support. It queries firmware-provided verification certificates, validates them, imports valid certificates into a kernel keyring, and exposes refresh/status controls under `/sys/firmware/cert_store`.

## Important APIs, Types, And Functions
Firmware block layouts are `vcssb`, `vcb_header`, `vcb`, `vce_header`, and `vce`. `fill_cs_keyring()` orchestrates refresh. `query_diag320_subcodes()`, `get_vcssb()`, `get_sevcb()`, and `create_key_from_sevcb()` perform diagnose queries. `check_certificate_valid()` and `check_certificate_hash()` validate entries. Keyring helpers include `create_cs_keyring()`, `cleanup_cs_keys()`, and `create_key_from_vce()`. Sysfs handlers are `cs_status_show()` and `refresh_store()`.

## Control Flow
Device init registers debug features, creates the firmware sysfs directory, and registers the `cert_store_key` key type. A sysfs refresh locks `cs_refresh_lock`, retries `fill_cs_keyring()` on `-EAGAIN`, queries supported DIAG 320 subcodes, reads storage size metadata, creates a fresh `cert_store` keyring, iterates certificate indices, fetches one VCB per certificate, extracts and validates the VCE, then links the certificate payload as a restricted key.

## State And Persistence
Persistent runtime state is the keyring and its keys, `cs_status_val`, debug feature buffers, and firmware certificate-store token. Refresh first cleans old keys and keyring state. Certificates live as kernel keys until invalidated or refreshed.

## Dependencies And Integration Points
Depends on s390 DIAG 320, SCLP feature bits, EBCDIC conversion, SHA256, keyrings, sysfs firmware kobjects, vmalloc, and s390 debug feature. It integrates firmware certificate material with Linux key consumers.

## Risks And Edge Cases
Risks include firmware token mismatch, insufficient VCB buffer size, invalid hashes, EBCDIC descriptions, key type unregister on cleanup failure, and user-visible keyring cleanup races. Some debug hexdumps intentionally expose certificate bytes to s390dbf.

## Test Signals
Signals include DIAG 320 feature probing, sysfs refresh/status tests, keyring contents after refresh, invalid certificate/hash rejection, token mismatch retry, no-certificate behavior, and cleanup on repeated refreshes.
