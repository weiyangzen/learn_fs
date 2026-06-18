# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_cli_upcall.c

Purpose: bridges user-space GSS negotiation (`lgssd`/keyring upcall data) to kernel PTLRPC security-context initialization and destruction RPCs.

Important APIs/types/functions: `gss_do_ctx_init_rpc()` validates an `lgssd_ioctl_param`, finds a client OBD/import, builds a `SEC_CTX_INIT` request, sends it, parses the reply, and copies result fields back to user space. `gss_do_ctx_fini_rpc()` sends `SEC_CTX_FINI` for an uptodate context. Helpers `ctx_init_pack_request()` and `ctx_init_parse_reply()` serialize request and reply payloads.

Control flow: initialization validates ioctl size and interface version, copies the target OBD name from user space, rejects invalid/stopping/non-client devices, gets a live import, ensures the security id still matches, allocates `RQF_SEC_CTX`, packs the GSS header, optional user descriptor, target UUID, reverse handle, and user token, then waits synchronously. Queue failures other than `-EACCES` are reported to user space as `-ETIMEDOUT` so negotiation can retry. Reply parsing checks GSS version/bufcount, writes status, major/minor, sequence window, context handle, and output token to the supplied user buffer.

State/persistence: no durable storage. Mutates a transient request, user output buffer, context procedure field for destroy, and import/request refs.

Dependencies/integration: depends on PTLRPC request allocation/packing, `RQF_SEC_CTX`, `SEC_CTX_INIT`, `SEC_CTX_FINI`, OBD/import lookup, GSS raw object serialization, security flavor packing, and user-space `lgssd` ABI structures.

Risks/test signals: user pointer handling, output size checks, stale imports, changed `secid`, and request lifetime cleanup are primary risks. Tests should cover bad ioctl versions/sizes, invalid OBD names, unsupported device types, deactivated imports, oversized tokens, user copy failures, server denial, timeout remapping, swabbed replies, and destroy RPC suppression for non-uptodate/error contexts.
