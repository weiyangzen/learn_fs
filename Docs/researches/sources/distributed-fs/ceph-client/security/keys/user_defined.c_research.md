# sources/distributed-fs/ceph-client/security/keys/user_defined.c

## Purpose

`user_defined.c` implements the generic `user` key type and the non-readable `logon` key type. These key types store arbitrary user-provided payload bytes in keyrings, with `logon` intended for secrets such as credentials that must not be readable back to userspace.

## Important APIs, Types, and Functions

`key_type_user` includes read support through `user_read()`. `key_type_logon` reuses the same payload operations but omits `.read` and adds `logon_vet_description()`. `user_preparse()` validates and copies incoming payloads into `struct user_key_payload`. `user_update()` reserves quota, swaps payloads under RCU, and preserves expiry. `user_revoke()` clears quota and defers payload freeing. `user_destroy()` frees final payload state. `user_describe()` prints description and payload length.

## Control Flow

Instantiation uses `user_preparse()` followed by `generic_key_instantiate()`. Update reserves quota for the new length, installs the new payload, nulls the preparsed pointer so the key core will not free it twice, and queues old payload RCU disposal. Read returns the full payload length and copies as many bytes as the caller buffer allows. Logon key creation first vets that descriptions are qualified with a non-leading colon.

## State and Persistence Behavior

The payload is stored as an RCU-protected `struct user_key_payload` attached to the key. Payload memory is freed with `kfree_sensitive()` on preparse failure, revoke, update, and destroy paths. Quota is reserved according to payload length and released on revoke.

## Dependencies and Integration Points

The file integrates with key type registration elsewhere, the generic key instantiate helper, key quota accounting, RCU payload accessors, and exported user-key APIs used by encrypted/trusted key helpers.

## Risks and Test Signals

The main risks are exposing `logon` payloads through a read path, accepting invalid zero/oversized payloads, and mishandling RCU swaps. Tests should cover payload sizes 0, 1, 32767, and 32768; updates and revoke/read races; logon descriptions without a colon; and sensitive-memory cleanup paths.
