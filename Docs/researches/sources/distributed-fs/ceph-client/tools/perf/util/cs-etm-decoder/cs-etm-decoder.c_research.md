# sources/distributed-fs/ceph-client/tools/perf/util/cs-etm-decoder/cs-etm-decoder.c

Purpose: wraps the OpenCSD C API to decode CoreSight ETM/PTM/ETE trace streams into perf packet queues, including memory callbacks, timestamp handling, discontinuities, exceptions, PE context updates, and lifecycle.

Important APIs/functions: `cs_etm_decoder__new`, `cs_etm_decoder__free`, `cs_etm_decoder__process_data_block`, `cs_etm_decoder__reset`, `cs_etm_decoder__add_mem_access_cb`, `cs_etm_decoder__get_packet`, and `cs_etm_decoder__get_name`.

Control flow: construction creates an OpenCSD decode tree, configures formatter flags, initializes logging, and creates one protocol decoder per trace parameter block. Data processing alternates data and flush operations based on prior wait responses, stops on queue-full/wait, records consumed bytes, and stores the response. Trace callbacks buffer ranges, discontinuities, exceptions, timestamps, and PE context TID/EL updates into perf queues.

State and persistence: decoder holds caller data, packet printer, suppress flag, OpenCSD tree handle, memory callback, previous datapath response, and decoder name. Packet queue state is external and updated through ETM queue helpers.

Dependencies and integration: OpenCSD C API, CoreSight PMU UAPI, `cs-etm.h` queue helpers, packet structures, timestamp conversion, intlist/debug utilities, and zalloc. Bridges raw AUX trace bytes to synthesized perf samples.

Risks: ring management increments head/tail before use and assumes power-of-two buffer sizing. Timestamp estimation uses `INSTR_PER_NS = 10` and affects ordering. Memory callback must be installed before memory decode needs it. Construction requires a packet printer because logging setup fails without it.

Test signals: ETMv3/PTM/ETMv4i/ETE, formatted/unformatted streams, print vs decode, queue full/wait, discontinuity reset, hard/soft timestamps including zero/underflow, PE context formats, memory callbacks, reset after partial decode, and OpenCSD fatal errors.
