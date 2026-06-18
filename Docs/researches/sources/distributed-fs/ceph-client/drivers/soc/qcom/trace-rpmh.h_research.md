# sources/distributed-fs/ceph-client/drivers/soc/qcom/trace-rpmh.h

## Purpose

`trace-rpmh.h` defines tracepoints for Qualcomm RPMh TCS command transmission and acknowledgment. It captures command address/data, TCS slot, message header, RPMh state, and completion wait flag for low-level power-resource debugging.

## Important APIs, Types, and Functions

The header includes `rpmh-internal.h` for `struct rsc_drv`, `struct tcs_request`, `struct tcs_cmd`, and `enum rpmh_state`. It declares `rpmh_tx_done(struct rsc_drv *d, int m, const struct tcs_request *r)` and `rpmh_send_msg(struct rsc_drv *d, int m, enum rpmh_state state, int n, u32 h, const struct tcs_cmd *c)`.

## Control Flow

RPMh code emits `rpmh_send_msg` while programming a TCS command and `rpmh_tx_done` when an ACK arrives. The trace event copies only the first command's address/data for the done path and one command pointer for the send path.

## State and Persistence Behavior

The file stores no state. Trace payloads are transient records in ftrace/perf buffers and reflect the RPMh request state at trace-call time.

## Dependencies and Integration Points

It integrates tightly with internal RPMh data structures and the trace event generator. The symbolic state printer maps sleep, wake-only, and active-only state enum values to readable strings.

## Risks and Edge Cases

The tracepoints dereference `r->cmds[0]` and `c`, so callers must pass non-empty requests and valid command pointers. Structure changes in `rpmh-internal.h` can silently break trace semantics. Include-path assumptions require the header to remain alongside RPMh sources.

## Test Signals

Build with RPMh tracing enabled. Generate active, wake-only, and sleep requests, then verify trace output for resource driver name, TCS index, command index, header, address, data, and wait flag. Include tests for multi-command requests to confirm intended first-command reporting.
