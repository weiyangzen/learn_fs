# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/glusterfs-acl.h

## Purpose
Defines GlusterFS POSIX ACL wire/xattr structures and helper mappings. It contains legacy Linux-oriented ACL support plus a newer libacl-style portable interface when `sys/acl.h` is available.

## APIs, Types, and Functions
Legacy constants include ACL RPC program/version, POSIX ACL permission bits, tag values, undefined id, xattr version, and disk xattr names `system.posix_acl_access` and `system.posix_acl_default`. `posix_acl_xattr_header` and `posix_acl_xattr_entry` model xattr layout; inline helpers compute xattr size and entry count. Runtime structures include `posix_ace`, `posix_acl`, `posix_acl_ctx`, and `posix_acl_conf`. New virtual RPC xattrs are `GF_POSIX_ACL_ACCESS` and `GF_POSIX_ACL_DEFAULT`; `GF_POSIX_ACL_REQUEST()` recognizes either. With `HAVE_SYS_ACL_H`, `gf_posix_acl_get_key()` and `gf_posix_acl_get_type()` map between `acl_type_t` and virtual keys.

## Control Flow, State, and Persistence
ACL xattr structures represent persistent ACL metadata; virtual keys are transported over RPC and not stored on disk. `posix_acl_conf` holds process/translator ACL configuration and minimal ACL cache under a lock.

## Dependencies and Integration
Depends on `locking.h`, uid/gid/mode types, optional `sys/acl.h`, and `SLEN` from `glusterfs.h` via include order. Integrated with POSIX ACL xlator, server/client xattr paths, and permission checking.

## Risks and Test Signals
Risks include endian/layout mismatches, Linux-specific legacy assumptions, invalid ACL size/count parsing, virtual xattrs leaking to disk, and unsupported NetBSD behavior. Test signals include ACL xattr encode/decode tests, access/default mapping tests, permission enforcement cases, cross-platform build coverage, and malformed ACL rejection.
