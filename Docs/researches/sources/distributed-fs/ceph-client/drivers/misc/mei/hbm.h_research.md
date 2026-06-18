<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hbm.h -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/hbm.h

Purpose: declares the HBM protocol state enum and the public HBM helpers used by MEI core, interrupt handling, client operations, and hardware power-management code.

Important APIs and types: `enum mei_hbm_state` names the HBM lifecycle: idle, starting, capabilities setup, DMA-ring setup, enum clients, client properties, started, and stopped. The header exposes `mei_hbm_state_str()`, `mei_hbm_dispatch()`, start/reset/idle helpers, client control requests, protocol-version support check, power-gating message helpers, notification request, and client DMA map/unmap request.

Control flow: consumers call `mei_hbm_start_req()` during reset/start, wait with `mei_hbm_start_wait()`, and pass inbound host-bus messages to `mei_hbm_dispatch()` from the read interrupt path. Client operations enqueue callbacks elsewhere and use these request helpers when the write interrupt path has space. Runtime PM invokes `mei_hbm_pg()` for PG entry/exit handshakes and `mei_hbm_pg_resume()` when firmware asks the host to wake.

State and persistence: this header owns no storage; it defines state symbols used in `struct mei_device`. Persistence is volatile and reset-driven.

Dependencies and integration: forward-declares `struct mei_device`, `struct mei_msg_hdr`, `struct mei_cl`, and `struct mei_dma_data`, so it can be included without pulling the full MEI object graph. The implementations depend on HBM command structs in `hw.h`.

Risks: adding an HBM state in the implementation without updating this enum and string conversion would reduce observability and may break state-machine checks. Public prototypes make this a cross-file contract; signature changes require coordinated updates in client, interrupt, and init code.

Test signals: compile coverage from all MEI objects, runtime sysfs `hbm_ver`, and logs that print HBM state names during timeout or mismatch paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hbm.h -->
