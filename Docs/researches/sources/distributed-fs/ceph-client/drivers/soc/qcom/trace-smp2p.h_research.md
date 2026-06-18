# sources/distributed-fs/ceph-client/drivers/soc/qcom/trace-smp2p.h

## Purpose

`trace-smp2p.h` defines tracepoints for Qualcomm SMP2P shared-memory peer state negotiation, inbound notifications, SSR acknowledgments, and outbound bit updates.

## Important APIs, Types, and Functions

It sets `TRACE_SYSTEM` to `qcom_smp2p` and declares `smp2p_ssr_ack()`, `smp2p_negotiate()`, `smp2p_notify_in()`, and `smp2p_update_bits()`. The latter two take `struct smp2p_entry *` and use fields such as `smp2p_entry->smp2p->dev` and `smp2p_entry->name`.

## Control Flow

The SMP2P implementation calls these generated trace functions around feature negotiation, incoming status updates, outgoing value changes, and subsystem-restart acknowledgment handling. The tracepoint fast paths copy device/client names and status/value fields.

## State and Persistence Behavior

No persistent state is defined. Events are emitted only when tracing is enabled and live in tracing buffers.

## Dependencies and Integration Points

The header depends on tracepoint infrastructure and the private SMP2P structures being visible at include time. `SMP2P_FEATURE_SSR_ACK` is used in flag printing, so the provider must define it before expansion.

## Risks and Edge Cases

The trace macros dereference nested SMP2P pointers, so callers must not trace after entry teardown. Private-structure coupling means refactors of SMP2P internals require matching trace header updates. Include guard and path macros must remain exact for trace generation.

## Test Signals

Build the SMP2P driver with tracing. Exercise SSR ACK negotiation, inbound remote writes, and local `update_bits()` calls, then verify event fields and flag decoding under `/sys/kernel/tracing/events/qcom_smp2p`.
