# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/bufq/interface/ia_css_bufq.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/bufq/interface/ia_css_bufq.h` declares the host/SP buffer queue and event queue API: queue mapping, module init/deinit, buffer enqueue/dequeue, psys/isys event enqueue/dequeue, tagger command enqueue, and queue diagnostics.

Important APIs, types, and functions: Important local symbols: `ia_css_query_internal_queue_id`, `ia_css_queue_map`, `ia_css_queue_map_init`, `ia_css_bufq_init`, `ia_css_bufq_enqueue_buffer`, `ia_css_bufq_dequeue_buffer`, `ia_css_bufq_enqueue_psys_event`, `ia_css_bufq_dequeue_psys_event`, `ia_css_bufq_enqueue_isys_event`, `ia_css_bufq_dequeue_isys_event`, `ia_css_bufq_enqueue_tag_cmd`, `ia_css_bufq_deinit`, `ia_css_bufq_dump_queue_info` Types and constants: No named structs or enums are introduced here.; `_IA_CSS_BUFQ_H`, `BUFQ_EVENT_SIZE`

Control flow: CSS initialization maps buffer types to per-thread queues, initializes remote SP queue handles, and uses these APIs to pass buffers/events between host and SP firmware.

State and persistence behavior: State is static in-memory queue handles, buffer-type-to-queue maps, availability bitmaps, and SP-resident circular queues. No data persists after driver/runtime reset.

Dependencies and integration points: The queue layer depends on SP firmware queue offsets, `ia_css_queue`, `ia_css_eventq`, buffer type enums, SP thread constants, tagger commands, and CSS debug tracing.

Risks and edge cases: Queue IDs are shared ABI values with SP firmware; mismatched thread or queue IDs cause lost buffers or blocked pipelines.

Test signals: Test map/unmap lifecycle, reserved parameter queues, queue exhaustion, invalid thread/queue IDs, enqueue full/dequeue empty behavior, psys/isys event payload ordering, tagger command delivery, and queue-info dump output.
