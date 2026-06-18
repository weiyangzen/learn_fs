<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/process_keys.c -->
# sources/distributed-fs/ceph-client/security/keys/process_keys.c

## Purpose
`process_keys.c` manages keyrings attached to credentials: thread, process, session, user, user-session, requestor, and request-key authorization keyrings. It also implements lookup of user-supplied key serials and special key IDs.

## Important APIs, Types, and Functions
Important APIs are `look_up_user_keyrings()`, `get_user_session_keyring_rcu()`, `install_thread_keyring_to_cred()`, `install_process_keyring_to_cred()`, `install_session_keyring_to_cred()`, `key_fsuid_changed()`, `key_fsgid_changed()`, `search_cred_keyrings_rcu()`, `search_process_keyrings_rcu()`, `lookup_user_key_possessed()`, `lookup_user_key()`, `join_session_keyring()`, and `key_change_session_keyring()`.

## Control Flow
User keyrings are found or created under the current user namespace register. Thread/process/session install functions prepare new credentials and commit them. Lookup handles special negative IDs by creating keyrings when allowed, falling back from session to user-session keyring, resolving request-key auth/requestor keyrings, or looking up positive serials in `key_serial_tree`. It then waits for construction unless partial lookup is requested, validates state, checks permission, marks last-used time, and returns a possessed reference when reachable from process keyrings.

## State and Persistence
Credential objects hold keyring references. User namespaces pin the hidden `.user_reg` register. `root_key_user` seeds root accounting. Named sessions can outlive a process while referenced. Session-to-parent replacement is stored as a prepared credential in task work until the parent resumes userspace.

## Dependencies and Integration Points
This file integrates with credentials, user namespaces, user_struct, keyring allocation/search, request-key auth payloads, permission checks, LSM credential transfer, and late init creation of root keyrings.

## Risks
Credential replacement must never mutate live creds directly; helper functions operate on prepared creds or commit new ones. `lookup_user_key()` combines many special cases and must preserve construction/partial/auth override semantics. User namespace register creation and named session joins use locks to avoid duplicate keyrings and disappearing names.

## Test Signals
Test all `KEY_SPEC_*` IDs with and without create flags, setuid/fsuid/fsgid changes, named and anonymous session joins, user-session fallback, requestor keyring during upcalls, lookup of under-construction and negative keys, possessor detection, and parent session replacement constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/process_keys.c -->
