# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/bufq/interface/ia_css_bufq_comm.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/bufq/interface/ia_css_bufq_comm.h` defines the shared queue ID enum, maximum queue count, dynamic-buffer limit per thread, and reserved parameter/per-frame parameter queue IDs.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `sh_css_queue_id`; `_IA_CSS_BUFQ_COMM_H`, `SH_CSS_MAX_NUM_QUEUES`, `SH_CSS_MAX_DYNAMIC_BUFFERS_PER_THREAD`, `IA_CSS_PARAMETER_SET_QUEUE_ID`, `IA_CSS_PER_FRAME_PARAMETER_SET_QUEUE_ID`

Control flow: Both host queue mapping and SP firmware agree that queues A and B are reserved for parameter sets and per-frame parameter sets.

State and persistence behavior: State is static in-memory queue handles, buffer-type-to-queue maps, availability bitmaps, and SP-resident circular queues. No data persists after driver/runtime reset.

Dependencies and integration points: The queue layer depends on SP firmware queue offsets, `ia_css_queue`, `ia_css_eventq`, buffer type enums, SP thread constants, tagger commands, and CSS debug tracing.

Risks and edge cases: Adding buffer types without increasing queues can exhaust the C-H dynamic mapping range.

Test signals: Test map/unmap lifecycle, reserved parameter queues, queue exhaustion, invalid thread/queue IDs, enqueue full/dequeue empty behavior, psys/isys event payload ordering, tagger command delivery, and queue-info dump output.
