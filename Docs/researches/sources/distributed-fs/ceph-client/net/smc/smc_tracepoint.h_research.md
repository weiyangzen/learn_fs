# sources/distributed-fs/ceph-client/net/smc/smc_tracepoint.h

Purpose: Declares SMC trace events for fallback, transmit, receive, and SMC-R link-down diagnostics.

Important APIs/types/functions: `TRACE_EVENT(smc_switch_to_fallback)` records SMC socket, CLC socket, net cookie, and fallback reason. `DECLARE_EVENT_CLASS(smc_msg_event)` and two `DEFINE_EVENT`s record TX/RX message length and device name. `TRACE_EVENT(smcr_link_down)` records link, link group, net cookie, link state, device name, and call-site location.

Control flow: SMC runtime code calls generated `trace_smc_*` helpers at important state transitions. The trace macros collect stable fields from socket/link structures and format them for trace buffers only when enabled.

State and persistence behavior: The header defines trace metadata, not SMC state. Emitted records are transient tracing data controlled by kernel tracing buffers.

Dependencies and integration points: Depends on `linux/tracepoint.h`, IPv6/TCP headers, and SMC core structures. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` point trace generation to this header, while `smc_tracepoint.c` creates the definitions.

Risks and test signals: Risks include dereferencing fields that may be null in unusual fallback or link teardown states, format ABI churn visible to tracing tools, and missing net/device context for diagnosis. Test by enabling each event, forcing fallback, sending/receiving SMC-D and SMC-R data, triggering link-down paths, and validating trace fields under module builds.
