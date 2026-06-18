# sources/distributed-fs/ceph-client/include/linux/soc/qcom/apr.h

Purpose: This Qualcomm header defines APR/GPR packet formats, bus/driver registration helpers, and send/port APIs for Qualcomm audio/service packet routing.

Important APIs/types/functions: It exports `aprbus`, APR/GPR header field macros, message type constants, basic response opcodes, packed `struct apr_hdr`, `apr_pkt`, `apr_resp_pkt`, `gpr_hdr`, `gpr_pkt`, `gpr_resp_pkt`, response structs, service-version helpers, `gpr_port_cb`, `struct pkt_router_svc`, `struct apr_device`, `struct apr_driver`, module registration macros, `apr_send_pkt`, `gpr_alloc_port`, `gpr_free_port`, `gpr_send_port_pkt`, and `gpr_send_pkt`.

Control flow: APR/GPR drivers register on `aprbus`, bind to service IDs/domains, receive callback packets, allocate optional GPR ports, send packets with packed headers, and unregister through module helpers.

State and persistence: Device/service state lives in `apr_device`, router services, spinlocks, callback/private pointers, and remote subsystem routing. Packet headers carry token/opcode state for request/response correlation.

Dependencies and integration: Uses driver core, spinlocks, module device tables, and Qualcomm APR/GPR DT bindings. Integrates with audio DSP, remoteproc/rpmsg-like transports, and service routing.

Risks and test signals: Header packing, size fields, domain/port IDs, and callback locking are critical. Test packet round trips, basic response parsing, driver probe/remove, GPR port allocation, remote SSR, and malformed packet sizes.
