# sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_tee.c

## Purpose

`trusted_tee.c` implements a trusted-key backend backed by an OP-TEE trusted application. It delegates random generation, sealing, and unsealing to a TEE session using shared memory.

## Important APIs, Types, and Functions

`struct trusted_key_tee_private` stores the TEE device, context, session ID, and shared-memory pool pointer. `trusted_tee_seal()`, `trusted_tee_unseal()`, and `trusted_tee_get_random()` invoke TA commands `TA_CMD_SEAL`, `TA_CMD_UNSEAL`, and `TA_CMD_GET_RANDOM`. `optee_ctx_match()` restricts contexts to OP-TEE with registered memory support. `trusted_key_probe()` opens the context/session and registers `key_type_trusted`; `trusted_key_remove()` unregisters and closes them. `trusted_key_tee_ops` exposes the callbacks to the core.

## Control Flow

The TEE client driver binds to a fixed TA UUID. Probe opens an OP-TEE context, opens a kernel-login session to the TA, then registers the trusted key type. Seal and unseal register a kernel buffer spanning `p->key` and `p->blob`, set input/output memrefs at the correct offsets, invoke the TA, and update `blob_len` or `key_len` from the returned memref size. Random generation registers the caller-provided key buffer and invokes the random command.

## State and Persistence Behavior

Backend state is the global `pvt_data` session/context. Per-key persistence is the TA-produced sealed blob. Keys are non-migratable because the TA is expected to use a hardware unique key. Shared-memory registrations are temporary and freed after each invocation.

## Dependencies and Integration Points

The backend depends on TEE client devices, OP-TEE generic capabilities, a TA with the hard-coded UUID, and the trusted-key core. It is selected by `CONFIG_TRUSTED_KEYS_TEE`.

## Risks and Test Signals

The correctness boundary includes TA behavior, memref sizing, and shared buffer layout. Probe must clean up contexts on partial failure. Test signals include TA absence, session open failure, command return codes, short random output, seal/unseal round trips, driver unbind cleanup, and concurrent key operations sharing the global session.
