# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-mem.c

Purpose: allocates, initializes, expands, maps, and frees CDNSP hardware-visible memory. The complete 1336-line file was read. It manages DMA rings/segments, context memory, stream context arrays, event ring segment tables, port discovery, and memory init/cleanup.

Important APIs/types/functions: `cdnsp_mem_init()`, `cdnsp_mem_cleanup()`, `cdnsp_setup_addressable_priv_dev()`, `cdnsp_copy_ep0_dequeue_into_input_ctx()`, `cdnsp_endpoint_zero()`, `cdnsp_endpoint_init()`, `cdnsp_ring_expansion()`, `cdnsp_dma_to_transfer_ring()`, `cdnsp_alloc_stream_info()`, stream/ring free helpers, and context accessors `cdnsp_get_input_control_ctx()`, `cdnsp_get_slot_ctx()`, `cdnsp_get_ep_ctx()`.

Control flow: init programs CONFIG, allocates DCBAA, creates DMA pools, allocates command/event rings, writes command-ring, doorbell, interrupter, ERST, and event-dequeue registers, scans extended capabilities for USB2/USB3 ports, and allocates the private device plus EP0 ring. Endpoint init computes descriptor-derived context fields and allocates streams for SuperSpeed bulk endpoints.

State and persistence: persistent state includes coherent DCBAA/ERST memory, DMA-pool context blocks, ring segment DMA buffers and bounce buffers, stream context arrays, radix mappings from TRB DMA to stream rings, port descriptors, and `pdev` ring/context pointers.

Dependencies/integration: Linux DMA/pool/slab/USB helpers, radix trees, `cdnsp-gadget.h`, and tracepoints. Used by gadget setup, endpoint enable, ring queueing, and event handling.

Risks: allocation unwind order is complex; stream radix mapping assumes segment-aligned DMA keys; stream context arrays are limited by `CDNSP_CTX_SIZE`; ring expansion must preserve cycle state and mappings; interval/burst/ESIT calculations vary by speed and endpoint type.

Test signals: fault injection through allocation steps, init/cleanup leak checks, USB2/USB3 port detection, EP0 setup for each speed, descriptor-to-context traces, stream allocation limits, ring expansion, bounce-buffer paths, and gadget unbind/probe failure cleanup.
