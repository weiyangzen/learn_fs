# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/accessories/link_dp_trace.h

Purpose: header for DP trace helper functions.

Important APIs/types/functions: declares initialization/reset helpers, detect/commit LT trace reset, link-loss and LT count updates, logged-flag accessors, LT result/timestamp accessors, eDP power timestamp accessors, and `dp_trace_source_sequence()`.

Control flow and integration: included by DP link training, diagnostics, and eDP power sequencing code to update `dc_link.dp_trace` without exposing implementation details.

State and persistence: no header state; declared functions read/write `struct dc_link` trace fields.

Dependencies, risks, and test signals: includes `link_service.h` for link and training result types. Build coverage catches prototype drift; runtime signals are correct diagnostic output and debug DPCD behavior.
