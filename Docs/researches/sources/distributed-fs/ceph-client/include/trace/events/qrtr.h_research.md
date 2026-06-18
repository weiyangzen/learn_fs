# sources/distributed-fs/ceph-client/include/trace/events/qrtr.h

Purpose: Defines QRTR namespace and message tracepoints for Qualcomm IPC Router service discovery and namespace traffic.

Important APIs/types/functions: Events include `qrtr_ns_service_announce_new`, `qrtr_ns_service_announce_del`, `qrtr_ns_server_add`, and `qrtr_ns_message`. Fields capture service, instance, node, port, endpoint node/port, message type, and SQ family data.

Control flow: QRTR namespace code emits announce events when services appear/disappear, server-add events when namespace servers are registered, and message events for namespace messages. Trace records track discovery propagation.

State and persistence: No state is owned. It observes QRTR node/port/service records and namespace messages, which are runtime IPC state.

Dependencies and integration points: Depends on `linux/qrtr.h` and tracepoints. It integrates with Qualcomm remoteproc/subsystem IPC, QRTR sockets, and service discovery.

Risks and test signals: Risks include confusing node/port lifetimes, missing delete events, malformed message decoding, and high trace volume in service churn. Test QRTR service announce/delete, remote subsystem restart, namespace server registration, malformed messages, and tracing across network namespaces if supported.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/qrtr.h` completely for this pass (118 lines, 2590 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/qrtr.h_research.md`.
