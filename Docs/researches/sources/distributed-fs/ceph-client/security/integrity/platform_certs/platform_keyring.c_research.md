# sources/distributed-fs/ceph-client/security/integrity/platform_certs/platform_keyring.c

Purpose: Initializes the platform keyring and provides an init-only helper to import firmware/platform certificates without validating their chain.

Important APIs/types/functions: `add_to_platform_keyring()` calls `integrity_load_cert(INTEGRITY_KEYRING_PLATFORM, ...)` with broad positional permissions minus setattr and user view permission. `platform_keyring_init()` initializes the keyring via `integrity_init_keyring()`.

Control flow: Device initcall creates the keyring before late platform cert loaders. Import failures are logged but not fatal to callers.

State and persistence: Platform keyring is global integrity state. This file does not keep local state.

Dependencies and integration: Used by UEFI, s390 IPL, powerpc secure variable, and machine fallback loaders. Depends on integrity keyring/cert APIs.

Risks and test signals: Risks include accepting firmware trust anchors without chain validation by design, late init ordering, and non-fatal load failures reducing available trust silently. Tests should verify keyring creation order and certificate import error logging.
