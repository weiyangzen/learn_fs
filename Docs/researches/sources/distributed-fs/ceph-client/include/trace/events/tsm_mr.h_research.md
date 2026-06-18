# sources/distributed-fs/ceph-client/include/trace/events/tsm_mr.h

Purpose: Provides tracepoints for trusted security module measurement register read, refresh, and write operations.

Important APIs/types/functions: Defines `tsm_mr_read`, `tsm_mr_refresh`, and `tsm_mr_write`, using `linux/tsm-mr.h` types to expose MR index, provider/device context, and operation result data.

Control flow: TSM MR code emits these events around measurement register accesses. The event assignments snapshot object identity and return/status fields without owning the operation.

State/persistence: Measurement registers remain owned by TSM/provider code. This header only persists operation observations in trace buffers.

Dependencies/integration: Depends on the TSM MR kernel API and tracepoint generator; useful for confidential-computing attestation diagnostics.

Risks: Measurement data may be security-sensitive. Tracepoint payloads should avoid leaking raw secrets and must keep provider/index semantics stable.

Test signals: Build TSM MR support with tracing; perform read/write/refresh operations and verify event emission and result codes.
