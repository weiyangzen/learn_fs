
# sources/distributed-fs/ceph-client/include/trace/events/sunvnet.h

## Purpose
Defines tracepoints for the Sun virtual network driver, focused on receive walking, stopped-ACK transmission/deferral/pending state, received stopped ACKs, transmit triggers, and skipped triggers.

## Important APIs, Types, and Functions
Events are `vnet_rx_one`, `vnet_tx_send_stopped_ack`, `vnet_tx_defer_stopped_ack`, `vnet_tx_pending_stopped_ack`, `vnet_rx_stopped_ack`, `vnet_tx_trigger`, and `vnet_skip_tx_trigger`. The stopped-ACK variants share `vnet_tx_stopped_ack_template`.

## Control Flow
Sunvnet code emits receive-walk traces with local/remote session ids, ring index, and ACK need; transmit paths emit stopped-ACK and trigger traces as they decide whether to notify peers or skip redundant triggers.

## State and Persistence
No driver state is stored here. Trace records persist session ids, ring indexes, ACK ranges, packet counts, trigger starts, and errors as scalar snapshots.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h` and sunvnet driver call sites. Integrates with SPARC logical-domain virtual networking diagnostics and ring/ACK flow-control debugging.

## Risks
Trace output is driver-specific and assumes local/remote session id semantics. High packet rates can make receive/trigger tracing noisy. The closing comment references `_TRACE_SOCK_H`, a harmless but misleading copy-paste label.

## Test Signals
Signals include virtual network traffic under sunvnet, stopped-ring/ACK scenarios, trigger send failures, skipped trigger cases, and trace correlation with packet counters.
