# sources/distributed-fs/lustre-release/lustre/mdt/mdt_lib.c

## Purpose
This file provides shared MDT request helper logic. Its largest responsibilities are initializing and validating request credentials, integrating nodemap/root-squash/identity/RBAC/capability policy, checking resource IDs, shaping reply buffers, handling HSM remove-on-last-unlink policy, and unpacking all reintegration request variants into `mdt_thread_info`.

## Important APIs, Types, And Functions
Credential APIs include `mdt_init_ucred()`, `mdt_init_ucred_reint()`, `mdt_check_ucred()`, `mdt_exit_ucred()`, `allow_client_chgrp()`, and `mdt_enable_gid_deny()`. Request/reply helpers include `mdt_name_unpack()`, `mdt_close_unpack()`, `mdt_reint_unpack()`, `mdt_fix_lov_magic()`, `mdt_fix_reply()`, `mdt_pack_secctx_in_reply()`, `mdt_pack_encctx_in_reply()`, `mdt_layout_version_check()`, `mdt_fids_different_target()`, and `mdt_is_remote_object()`. Policy helpers include `mdt_check_resource_ids()` and `mdt_handle_last_unlink()`. Static unpackers cover setattr, create, link, unlink/rmentry, rename, migrate, open, setxattr, and FLR resync.

## Control Flow
Credential initialization first exits any previous credential state, chooses old or new initialization based on GSS/user descriptor availability, maps client IDs and supplementary groups through nodemap, sets original and effective IDs, fetches identity upcall data when enabled, enforces setuid/setgid/setgroups permissions, applies deny-unknown and root-squash policy, intersects or assigns capabilities based on nodemap/server configuration, handles Kerberos group trust, and records jobid/NID/audit/RBAC fields. Reintegration unpacking clears `mti_rr`, dispatches by opcode, copies wire records into attributes/op specs/FID/name fields, maps supplementary groups, validates optional security/encryption contexts and sepol, handles replay/no-create flags, and unpacks optional LDLM requests. Reply fixing shrinks unused optional buffers and grows/re-packs large LOV/LMV/ACL buffers when the initially allocated reply was too small.

## State And Persistence
Most state is per-request in `lu_ucred`, `mdt_thread_info::mti_attr`, `mti_rr`, and `mti_spec`. Identity references and group_info references are held until `mdt_exit_ucred()`. `mdt_handle_last_unlink()` can persist an HSM `HSMA_REMOVE` request into the action llog when RAoLU policy is active and the last open reference of an archived unlinked file closes. Reply buffer sizes are transient RPC capsule state, but `mdt_max_mdsize` may be updated when larger metadata is observed.

## Dependencies And Integration Points
This code depends on request capsules, ptlrpc authentication fields, nodemap, identity upcall cache, root-squash configuration, Linux capabilities, Lustre layout/LMV/LOV formats, security and encryption xattrs, FLD lookup, linkEA parsing, HSM coordinator action logging, and lower MD/DT xattr/attribute operations. It is a central dependency for MDT metadata handlers and close/open/reint paths.

## Risks
Credential code is security-critical and mutates wire/body fields after nodemap mapping; callers must not assume original client IDs remain in those structures. Error paths must drop identity and group_info references. Kerberos mode intentionally distrusts client supplementary groups and requires identity consistency. Request unpackers rely on exact wire record sizes and optional field presence; accepting malformed names, xattr sizes, encryption contexts, or layout EAs would affect filesystem integrity. `mdt_fix_reply()` must coordinate with all handlers that add optional reply fields, or clients may see missing/oversized metadata. RAoLU last-unlink logging intentionally returns success even if remove logging fails, so operational monitoring must catch CERRORs.

## Test Signals
High-value tests cover old and new credential paths, Kerberos setuid/setgid/setgroups rejection, deny-unknown nodemap behavior, root-squash/nosquash NIDs, capability masks, RBAC role propagation, resource-id denial, all reint unpackers with malformed and optional fields, encryption/security context packing, large LOV/LMV/ACL reply growth, remote-object detection through FLD/linkEA, layout-version mismatch, replay/no-create behavior, and RAoLU remove request creation on last unlink.
