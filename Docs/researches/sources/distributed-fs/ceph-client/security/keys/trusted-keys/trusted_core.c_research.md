# sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_core.c

## Purpose

`trusted_core.c` defines the common `trusted` key type and dispatches sealing, unsealing, and random generation to one selected trust source. It parses user datablobs, manages trusted-key payload lifetime, supports update/reseal for migratable backends, exports sealed blobs, and selects the active backend at module init.

## Important APIs, Types, and Functions

`key_type_trusted` provides `.instantiate`, `.update`, `.destroy`, `.describe`, and `.read`. `trusted_key_sources[]` lists compiled backend operation tables. Static calls `trusted_key_seal`, `trusted_key_unseal`, and `trusted_key_get_random` are updated to the selected provider for fast dispatch. `datablob_parse()` recognizes `new <len>`, `load <hexblob>`, and `update`. `trusted_instantiate()` handles new/load requests; `trusted_update()` reseals an existing migratable key; `trusted_read()` returns the sealed blob as hex. `init_trusted()` selects a source and RNG, calls provider `.init`, updates static calls, and records the provider `.exit` and migratable default.

## Control Flow

Instantiation copies the keyctl payload into a NUL-terminated buffer, allocates a `trusted_key_payload`, parses the command, and either unseals a provided blob or asks the selected RNG to fill a new secret before sealing it. Successful payloads are attached with RCU key payload assignment. Update requires a positive, migratable key, parses only `update`, clones the old key bytes into a new payload, reseals with new options, swaps payloads, and frees the old payload via RCU. Module initialization iterates backend candidates, respecting `trusted.source` and `trusted.rng`, stops on first successful backend or on hard errors, and registers the common key type through the provider.

## State and Persistence Behavior

Per-key persistent state is `struct trusted_key_payload`: clear key bytes while resident, sealed blob bytes, lengths, migratable flag, and provider-specific flags. The external persistence boundary is the hex sealed blob returned by `trusted_read()`. Global state includes selected static-call targets, `trusted_key_exit`, module parameters, and the default migratable value inherited from the backend.

## Dependencies and Integration Points

The core integrates with the keyring subsystem, `keys/trusted-type.h`, user key describe helpers, random bytes, module parameters, and provider headers for TPM, TEE, CAAM, DCP, and PKWM. It relies on provider callbacks to register/unregister `key_type_trusted`.

## Risks and Test Signals

Incorrect datablob parsing or payload length handling can leak secrets, accept malformed blobs, or break compatibility. Static-call targets must only be used after a provider succeeds. Tests should cover `keyctl add trusted ... "new N"`, `load`, `update`, read hex length, unsupported source/RNG parameters, provider probe failure, migratable versus non-migratable update behavior, and memory sanitization on failure paths.
