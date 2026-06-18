# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/bufq/src/bufq.c

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/bufq/src/bufq.c` implements CSS host/SP queue mapping and remote queue handle initialization, plus enqueue/dequeue wrappers for buffers, psys/isys events, and tagger commands.

Important APIs, types, and functions: Important local symbols: `map_buffer_type_to_queue_id`, `unmap_buffer_type_to_queue_id`, `ia_css_queue_map_init`, `ia_css_queue_map`, `ia_css_query_internal_queue_id`, `init_bufq`, `ia_css_bufq_init`, `ia_css_bufq_enqueue_buffer`, `ia_css_bufq_dequeue_buffer`, `ia_css_bufq_enqueue_psys_event`, `ia_css_bufq_dequeue_psys_event`, `ia_css_bufq_dequeue_isys_event`, `ia_css_bufq_enqueue_isys_event`, `ia_css_bufq_enqueue_tag_cmd` Types and constants: `sh_css_queues`; `BUFQ_DUMP_FILE_NAME_PREFIX_SIZE`

Control flow: `ia_css_queue_map_init()` marks queues free and maps invalid. `ia_css_queue_map()` reserves fixed queues for parameter buffers or first available C-H queue. `ia_css_bufq_init()` builds remote queue handles from SP firmware offsets. Enqueue/dequeue functions validate IDs, resolve handles, and call `ia_css_queue_*` or `ia_css_eventq_*` helpers.

State and persistence behavior: State is static in-memory queue handles, buffer-type-to-queue maps, availability bitmaps, and SP-resident circular queues. No data persists after driver/runtime reset.

Dependencies and integration points: The queue layer depends on SP firmware queue offsets, `ia_css_queue`, `ia_css_eventq`, buffer type enums, SP thread constants, tagger commands, and CSS debug tracing.

Risks and edge cases: Mapping relies on assertions for duplicate/exhausted allocation, `deinit` is a no-op, and polled dequeue functions intentionally suppress tracing.

Test signals: Test map/unmap lifecycle, reserved parameter queues, queue exhaustion, invalid thread/queue IDs, enqueue full/dequeue empty behavior, psys/isys event payload ordering, tagger command delivery, and queue-info dump output.
