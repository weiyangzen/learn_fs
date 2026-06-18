# sources/distributed-fs/ceph-client/drivers/media/cec/usb/extron-da-hd-4k-plus/cec-splitter.c

## Purpose
This file implements high-level CEC policy for an HDMI splitter with one input and multiple outputs. It makes the splitter look coherent to upstream and downstream CEC devices by forwarding selected messages, tracking power/latency, and synthesizing replies.

## Important APIs, Types, and Functions
Exported local functions are `cec_splitter_unconfigured_output`, `cec_splitter_configured_output`, `cec_splitter_received_input`, `cec_splitter_received_output`, `cec_splitter_nb_transmit_canceled_output`, and `cec_splitter_poll`. Internal helpers send Active Source, Standby, wakeup, power-status requests, current-latency requests, averaged latency replies, and Feature Abort replies.

## Control Flow
Input-side received messages are filtered: standby/wakeup/active-source are propagated to outputs, power-status and latency requests fan out to outputs, and unsupported relevant messages return `-ENOMSG` for normal CEC handling. Output-side received messages update per-port power or latency state, answer sink requests, and handle active-source/set-stream-path logic. Non-blocking transmit callbacks and periodic polling clear timed-out pending requests and synthesize fallback state.

## State and Persistence
State is in `struct cec_splitter` and `struct cec_splitter_port`: standby flag, per-output active-source, sink presence, pending sequence IDs, timestamps, video latency, and power status. No persistent storage exists.

## Dependencies and Integration Points
The file depends on CEC core helpers such as `cec_msg_*`, `cec_ops_*`, `cec_transmit_msg`, adapter configuration state, and adapter locks for timeout updates. It is used by the Extron driver when `vendor_id` enables driver-managed splitter behavior.

## Risks and Test Signals
Risks include stale sequence tracking, timeout behavior tied to adapter `xfer_timeout_ms`, and lock ordering around adapter locks from poll context. Test standby/wakeup propagation, unavailable sink handling after HPD-low timeout, aggregated power-status and latency replies, Feature Abort for unavailable fanout, and canceled non-blocking transmit paths.
