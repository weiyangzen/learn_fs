# sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_pkwm.c

## Purpose

`trusted_pkwm.c` implements a trusted-key backend for IBM PowerVM Key Wrapping Module through pSeries PLPKS hypervisor interfaces. It wraps and unwraps trusted key payloads with a platform-generated wrapping key.

## Important APIs, Types, and Functions

`pkwm_trusted_key_ops` supplies non-migratable `.init`, `.seal`, `.unseal`, and `.exit` callbacks. `trusted_pkwm_init()` checks `plpks_wrapping_is_supported()`, generates a default wrapping key with `plpks_gen_wrapping_key()`, and registers `key_type_trusted`. `trusted_pkwm_seal()` parses `wrap_flags=...`, copies the payload into an aligned buffer, and calls `plpks_wrap_object()`. `trusted_pkwm_unseal()` calls `plpks_unwrap_object()`. `trusted_options_alloc()` allocates shared trusted options plus PKWM-private options.

## Control Flow

Init prepares the PLPKS wrapping environment before trusted keys can be created. Seal allocates option state, parses optional wrapping flags, creates an aligned input buffer from `p->key`, asks PLPKS to wrap it, and copies the returned object into `p->blob`. Unseal copies the sealed blob into an aligned input buffer, unwraps it through PLPKS, and copies returned plaintext into `p->key`.

## State and Persistence Behavior

The sealed object in `p->blob` is the persistent representation. The backend has no long-lived C state beyond the platform wrapping key managed by PLPKS. Temporary input and output buffers are freed after use; option structures are freed with sensitive-free helpers.

## Dependencies and Integration Points

Dependencies include `asm/plpks.h`, pSeries platform firmware, and common trusted-key types. It is selected by `CONFIG_TRUSTED_KEYS_PKWM` and invoked through `trusted_core.c`.

## Risks and Test Signals

Potential risks include output length exceeding `MAX_BLOB_SIZE`, incorrect assumptions about page-aligned buffers, and PLPKS support changing under firmware. Tests should cover unsupported firmware, wrapping-key generation failure, invalid `wrap_flags`, create/load round trips, and large key sizes near trusted-key limits.
