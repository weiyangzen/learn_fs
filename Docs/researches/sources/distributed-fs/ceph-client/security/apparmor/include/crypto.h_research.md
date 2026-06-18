# sources/distributed-fs/ceph-client/security/apparmor/include/crypto.h

## Purpose
This header exposes optional AppArmor SHA-256 policy hash helpers and provides no-op stubs when hash support is not compiled.

## Important APIs
When `CONFIG_SECURITY_APPARMOR_HASH` is enabled, it declares `init_profile_hash`, `aa_hash_size`, `aa_calc_hash`, and `aa_calc_profile_hash`. Otherwise `aa_calc_hash` returns `NULL`, `aa_calc_profile_hash` returns success, and `aa_hash_size` returns zero.

## Control flow and integration
Callers can invoke hash helpers without local `#ifdef`s. AppArmorfs and policy load code use these functions to create or display profile/rawdata hashes only when available.

## State and persistence
The header owns no state. It determines whether callers can allocate and persist hash buffers in profiles/load data.

## Dependencies
It includes `policy.h` for `struct aa_profile` and configuration symbols from Kconfig.

## Risks
The disabled stub for `aa_calc_hash` returning `NULL` must not be mistaken for an allocated digest or ERR_PTR. Callers need to branch on compiled/runtime feature availability before displaying hashes.

## Test signals
Build with hash support disabled and verify callers compile and avoid dereferencing zero-size hashes. Build enabled and verify exported hash sizes are 32 bytes.
