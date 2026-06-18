## sources/distributed-fs/ceph-client/fs/nfsd/auth.h

Purpose: declares the NFSD authentication helper `nfsd_setuser`, which applies an RPC request's user/group identity to the current kernel thread for export-backed filesystem access.

The header has no runtime control flow and exists to share the auth implementation with NFSD request handlers. State effects are in `auth.c`: current task credential overrides, groups, squash policy, and capabilities. Dependencies are `struct svc_cred` and `struct svc_export` definitions from NFSD/SunRPC headers included by consumers. Risks are prototype mismatch and misuse by callers that do not later restore credentials through the standard NFSD request lifecycle. Test signals: compile coverage for NFSD auth users and request handling that verifies user identity switching across exports.
