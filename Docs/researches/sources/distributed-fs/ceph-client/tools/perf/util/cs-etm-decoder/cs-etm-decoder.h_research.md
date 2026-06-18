# sources/distributed-fs/ceph-client/tools/perf/util/cs-etm-decoder/cs-etm-decoder.h

Purpose: declares CoreSight ETM decoder configuration structures, protocol/operation enums, callback types, and lifecycle/data APIs.

Important APIs/types: `cs_etm_mem_cb_type`, ETMv3/ETMv4/ETE trace parameter structs, `struct cs_etm_trace_params`, `struct cs_etm_decoder_params`, `CS_ETM_PROTO_*`, `enum cs_etm_decoder_operation`, and decoder APIs.

Control flow: callers prepare trace params and decoder params, create a decoder, feed AUX data blocks, drain packet queues with `cs_etm_decoder__get_packet`, and reset/free as needed.

State and persistence: decoder objects are opaque; packet queues and ETM queues are external. Trace parameter structs carry hardware register snapshots.

Dependencies and integration: Linux types, OpenCSD interface types, and stdio; integrates with perf CS-ETM auxtrace session code.

Risks: protocol enum values intentionally start at 1 to align with OpenCSD. Callback signatures must match OpenCSD memory-space semantics. Register sets must match the selected protocol.

Test signals: create decoders for each protocol, feed chunked data, register memory callbacks, reset, and verify empty/non-empty packet retrieval.
