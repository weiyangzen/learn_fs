# sources/distributed-fs/ceph-client/include/linux/key-type.h

## Purpose
Declares the key type implementation interface used by the kernel key retention service. Key types provide parsing, instantiation, update, matching, revocation, destruction, reading, request handling, restrictions, and asymmetric crypto operations.

## Important APIs, Types, And Functions
With `CONFIG_KEYS`, the header defines `struct key_preparsed_payload`, `request_key_actor_t`, `struct key_match_data`, and `struct key_type`. Key type callbacks include `vet_description`, `preparse`, `free_preparse`, `instantiate`, `update`, `match_preparse`, `match_free`, `revoke`, `destroy`, `describe`, `read`, `request_key`, `lookup_restriction`, and asymmetric query/encrypt-decrypt-sign/verify hooks. APIs include `register_key_type()`, `unregister_key_type()`, `key_payload_reserve()`, `key_instantiate_and_link()`, `key_reject_and_link()`, `key_negate_and_link()`, `complete_request_key()`, and `generic_key_instantiate()`.

## Control Flow
When adding/updating a key, the core fills a preparsed payload, calls optional type preparse, then instantiates or updates the key and later frees preparse state. Searches can preparse match data and use a custom comparator. Request-key can be handled by the type or delegated to userspace. Revoke/destroy/read callbacks run under key semaphore rules described in comments.

## State And Persistence
Key payloads live in `union key_payload` inside `struct key` objects, with quota tracked by `quotalen` and payload reservation. Key type registration state is a global type list. Keys persist in kernel keyrings until revoked, expired, garbage-collected, or destroyed.

## Dependencies And Integration Points
Depends on `linux/key.h`, errno, seq_file descriptions, keyrings, auth keys, quota accounting, network namespace domains, asymmetric key parameter structures, and userspace request-key integration.

## Risks
Type callbacks must maintain quota accounting, locking, and payload lifetime correctly. `free_preparse()` must match `preparse()` allocations. Read callbacks must return full readable length even when the buffer is small or NULL. Restriction callbacks must distinguish unknown restrictions from known no-op restrictions.

## Test Signals
Signals include key type registration/unregistration, add/update/instantiate failures, quota accounting, search matching, negative keys via `key_negate_and_link()`, revoke/destroy lifecycle, read sizing semantics, request-key authorization, keyring restrictions, asymmetric operation tests, and disabled `CONFIG_KEYS` builds.
