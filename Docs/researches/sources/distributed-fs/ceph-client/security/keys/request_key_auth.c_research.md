# sources/distributed-fs/ceph-client/security/keys/request_key_auth.c

## Purpose

`request_key_auth.c` implements the internal `.request_key_auth` key type used by the Linux key request upcall path. It creates short-lived authorization keys that let `/sbin/request-key` or another user-mode helper instantiate a pending key while preserving the original requester credentials, target key, callout data, and destination keyring. This is not a normal user-facing key type; it is glue between the keyring request path, credentials, and the userspace instantiation helper.

## Important APIs, Types, and Functions

The file defines `key_type_request_key_auth` with `.instantiate`, `.describe`, `.revoke`, `.destroy`, and `.read` operations. `request_key_auth_instantiate()` attaches the `struct request_key_auth` payload prepared by the caller. `request_key_auth_read()` exposes the callout info to the upcall helper. `request_key_auth_new()` allocates a payload, captures the correct servicing credentials and PID, references the target and destination keyring, allocates an authorization key named by the target serial, and instantiates it. `key_get_instantiation_authkey()` searches the current process keyrings for the authorization key matching a target serial.

## Control Flow

Creation starts with `request_key_auth_new()`. It copies callout bytes, records the operation string, and either inherits an existing request-key servicing context from `current_cred()->request_key_auth` or captures current credentials and PID. It then pins the target key and destination keyring, allocates a `.request_key_auth` key with view/read/search/link permissions, and links the `request_key_auth` payload through `key_instantiate_and_link()`. Consumers later call `key_get_instantiation_authkey()`, which builds the hexadecimal target-key description, searches process keyrings under RCU, maps `-EAGAIN` to `-ENOKEY`, and rejects revoked authorization keys.

## State and Persistence Behavior

Authorization state lives in `struct request_key_auth` and is referenced by the key payload under RCU. The payload owns references to the target key, destination keyring, and captured credentials. Revoke and destroy clear the key payload with `rcu_assign_keypointer()` and defer freeing via `call_rcu()`, which protects readers walking key payload state. The key is created outside normal quota accounting with `KEY_ALLOC_NOT_IN_QUOTA`, consistent with its internal authorization role.

## Dependencies and Integration Points

This file depends on keyring internals from `internal.h`, credential lifetime rules, RCU key payload accessors, and `keys/request_key_auth-type.h`. It integrates with the request-key upcall mechanism documented under keyring documentation, `search_process_keyrings_rcu()`, `key_alloc()`, and `key_instantiate_and_link()`.

## Risks and Test Signals

The sensitive risks are stale credential references, authorization keys surviving revoke, and leaking callout information to the wrong helper. RCU ordering and semaphore-guarded revoked checks are central. Useful validation includes keyutils request-key upcall tests, revocation races, nested request-key upcalls, negative key instantiation, and checks that revoked auth keys return `-EKEYREVOKED` or `-ENOKEY` as expected.
