# sources/distributed-fs/ceph-client/arch/sh/lib/ashiftrt.S

Purpose: provides fixed-count arithmetic right-shift helper entry points for values in `r4`.

Important symbols: `__ashiftrt_r4_32` down through `__ashiftrt_r4_0`.

Control flow: labels form a fall-through shift sequence, applying signed right shifts one step at a time until the requested count is reached and returning to the caller.

State and persistence: only register state is transformed; no memory persistence.

Dependencies and integration: called by compiler-generated code or other assembly helpers needing arithmetic shifts on SH cores without direct variable helpers.

Risks: symbol naming/count conventions must match compiler expectations. Signedness errors here corrupt arithmetic in many callers.

Test signals: compiler runtime arithmetic tests for negative and positive values across all shift counts.
