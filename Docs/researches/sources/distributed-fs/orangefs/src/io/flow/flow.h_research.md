# sources/distributed-fs/orangefs/src/io/flow/flow.h

Purpose: public flow subsystem interface and descriptor schema for OrangeFS I/O transfers among BMI network endpoints, Trove storage endpoints, and memory buffers.

Important APIs/types: endpoint types and unions describe BMI address, Trove collection/handle, and memory buffer. `enum flow_state` exposes initial/transmitting/complete states. Set/get info options include data sync mode, protocol type query, and amount-complete query. `flow_descriptor` contains caller-set callback, endpoints, tag, user pointer, requested protocol type, file and memory requests, aggregate size, file distribution data, buffer tuning, completion status, mutex, protocol id/private data, release hook, request states, result scratch, and hints. Function prototypes define initialize/finalize, allocation/reset/clear/free, post/cancel, setinfo/getinfo.

Control flow/state: callers fill public fields, call `PINT_flow_post()`, then protocol callbacks eventually set `state`, `error_code`, and `total_transferred` and invoke the caller callback after `release`.

Dependencies/integration: includes BMI, Trove storage, distribution, request, locks, quicklist, and PVFS types. The job layer stores `flow_descriptor *` in `JOB_FLOW`; flow protocols consume this struct deeply.

Risks/test signals: `aggregate_size` is optional but must be supplied when `mem_req` is absent. The descriptor is both public API and internal protocol state, so layout changes ripple widely. The current header lacks queue-link fields required by disabled `flow-queue`. Tests should verify endpoint combinations, callback/cancel path expectations, buffer tuning defaults, hint propagation, and ABI compatibility for code that embeds or allocates descriptors.
