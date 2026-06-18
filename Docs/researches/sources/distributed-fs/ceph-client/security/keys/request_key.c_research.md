<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/request_key.c -->
# sources/distributed-fs/ceph-client/security/keys/request_key.c

## Purpose
`request_key.c` implements the kernel request-key mechanism. It searches process keyrings for a key and, if missing and allowed, allocates an under-construction key and asks a key-type actor or `/sbin/request-key` to instantiate it.

## Important APIs, Types, and Functions
Public APIs are `complete_request_key()`, `request_key_and_link()`, `wait_for_key_construction()`, `request_key_tag()`, `request_key_with_auxdata()`, and `request_key_rcu()`. Internal helpers include `check_cached_key()`, `cache_requested_key()`, `call_sbin_request_key()`, `construct_key()`, `construct_get_dest_keyring()`, `construct_alloc_key()`, and `construct_key_and_link()`.

## Control Flow
`request_key_and_link()` preparses match data, checks the per-task requested-key cache, searches process keyrings, optionally links a found key to the destination, or starts construction on `-EAGAIN` when callout info is supplied. Construction selects a destination keyring based on explicit input or the caller's `jit_keyring`, allocates a key under the per-user construction lock, links it early to avoid duplicate races, creates a request-key auth key, and invokes the actor. The default actor builds a temporary `_req.<serial>` session keyring containing the auth key and executes `/sbin/request-key`.

## State and Persistence
Under-construction keys carry `KEY_FLAG_USER_CONSTRUCT` until instantiated or rejected. Negative construction results use a default 60-second timeout. Optional `CONFIG_KEYS_REQUEST_CACHE` stores the last successful requested key on the task until resume cleanup. The temporary request session keyring and auth key are reference-counted and cleaned after the upcall completes.

## Dependencies and Integration Points
This file depends on process keyring search, key allocation/linking, request-key auth key type, usermode helper execution, credentials, current task flags, namespace-aware user keyrings, and optional key type `request_key` callbacks.

## Risks
The duplicate construction race is handled by re-searching under `key_construction_mutex`; changes there can create multiple simultaneous upcalls for the same key. The usermode helper receives key serials and default keyring serials as ABI. Destination keyring permission is skipped only for requestor-keyring reuse, which is a deliberate upcall exception.

## Test Signals
Test successful usermode construction, custom key-type actor construction, negative construction, interrupted waits, duplicate concurrent requests, destination default selection for every `jit_keyring` value, request-key cache hits, RCU non-sleeping requests, and failure paths where the actor does not instantiate the key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/request_key.c -->
