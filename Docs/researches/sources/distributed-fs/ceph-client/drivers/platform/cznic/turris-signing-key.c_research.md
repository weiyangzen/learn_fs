<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-signing-key.c -->
# sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-signing-key.c

## Purpose

This helper module implements a kernel key type for Turris device signing keys and creates a global built-in keyring `.turris-signing-keys`. Device drivers register keys whose signing operation is delegated to device-specific callbacks.

## Important APIs, Types, And Functions

`turris_signing_key_type` defines instantiate, describe, read, asymmetric query, and asymmetric EDS operation callbacks. `turris_signing_key_asym_valid_params()` enforces raw encoding and the subtype's hash algorithm. `turris_signing_key_asym_query()` reports sign-only capabilities. `turris_signing_key_asym_eds_op()` dispatches sign requests to the subtype. `devm_turris_signing_key_create()` creates a built-in key, stores the device pointer and subtype, and registers devm cleanup.

## Control Flow

Module init registers the key type and allocates the global keyring. A device driver calls `devm_turris_signing_key_create()`, which creates a key in that keyring, associates subtype callbacks under RCU, and arranges unlink/put on device removal. Userspace keyctl operations query/read/sign the key and are routed through the key type callbacks.

## State And Persistence

Global state is the key type and keyring. Per-key state is the key payload's device pointer and subtype pointer. Public keys are read from the device-specific subtype; private keys are not stored here.

## Dependencies And Integration Points

It depends on Linux keyrings, asymmetric key operation hooks, device-managed cleanup, and `linux/turris-signing-key.h`. The Omnia MCU keyctl feature is one consumer.

## Risks

`turris_signing_key_read()` copies `public_key_size` bytes even if it reduces local `buflen`, which makes short user buffers a review hotspot. The key payload stores a raw device pointer, so devm cleanup order must ensure keys are unlinked before device data disappears. The key type supports only signing, not verify/encrypt/decrypt.

## Test Signals

Test module init/exit, keyring allocation failure, key creation/removal, key description, public-key read with full and short buffers, asymmetric query parameter validation, sign op dispatch, unsupported op rejection, and cleanup on device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-signing-key.c -->
