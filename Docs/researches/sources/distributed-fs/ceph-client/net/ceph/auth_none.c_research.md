# sources/distributed-fs/ceph-client/net/ceph/auth_none.c

## Purpose
Implements the `CEPH_AUTH_NONE` backend for clusters or connections that do not use a secret. It provides a minimal monitor auth state and service authorizer containing the client entity name and global id.

## Important APIs, Types, and Functions
The public initializer is `ceph_auth_none_init()`. Backend ops are `reset()`, `destroy()`, `is_authenticated()`, `should_authenticate()`, `build_request()`, `handle_reply()`, and `ceph_auth_none_create_authorizer()`. `ceph_auth_none_build_authorizer()` encodes the authorizer into `struct ceph_none_authorizer`.

## Control Flow
Initialization allocates `struct ceph_auth_none_info`, marks it starting, sets protocol to `CEPH_AUTH_NONE`, and installs `ceph_auth_none_ops`. There is no auth request payload. On monitor reply, `handle_reply()` clears `starting` and records the generic decoded global id. Service authorizer creation allocates a small object, encodes version byte, entity name, and global id, then exposes the buffer through `struct ceph_auth_handshake`.

## State and Persistence
State is limited to the `starting` boolean in `ac->private` and one allocated authorizer per handshake. The authorizer buffer is fixed at 128 bytes. No secrets or persistent tickets exist.

## Dependencies and Integration Points
Depends on generic auth encoding, Ceph entity-name encoding, and the generic authorizer destroy callback contract. It is selected by `auth.c` when protocol `CEPH_AUTH_NONE` is chosen.

## Risks
The fixed authorizer buffer assumes client names remain small enough after entity encoding. `build_request()` always returns 0, so protocol peers must accept an empty monitor payload. This backend provides identity but no cryptographic authentication or message signing.

## Test Signals
Authenticate without a key, verify `should_authenticate()` transitions from true to false after reply, create authorizers for monitor/OSD/MDS peer types, test long client names against the 128-byte buffer, and confirm secure-mode or signature requirements reject auth-none when the server disallows it.
