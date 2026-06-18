# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen2_response.c

## Purpose
`iris_hfi_gen2_response.c` parses Gen2 response headers/sub-packets, dispatches system/session errors, info, properties, commands, source-change events, buffer completions, internal buffer releases, image-version responses, and debug messages.

## Important APIs, Types, And Functions
The installed op is `iris_hfi_gen2_response_handler()`. Key helpers validate headers and packets, translate HFI buffer/picture/info flags to driver flags, handle session info/error/system error/init/close/stop/drain, handle input/output/internal buffer returns, dequeue completed vb2 buffers, read subscription params into V4L2 formats/caps, handle source change, handle properties, parse image version, and flush debug queue.

## Control Flow
The response handler first checks VPU watchdog and synthesizes a system error on watchdog timeout. It drains message packets from the queue, validates each Gen2 header and sub-packet against `IFACEQ_CORE_PKT_SIZE`, then dispatches to system or session handling based on `hdr->session_id`. System handling iterates packets by range and completes `core_init_done` for successful init. Session handling finds the instance, clears transient frame info, initializes source-change defaults when a settings-change packet appears, then makes ordered passes over session-error, info, property, and command ranges. If any buffer packet was handled, it completes all Iris buffers marked `DEQUEUED`.

## State And Persistence Behavior
The file mutates core error state, all instance states on system error, Gen2 `hfi_frame_info`, subscription params, source/destination V4L2 formats, crop, firmware caps, output buffer min-count/size, V4L2 min-buffer controls, queue min allocation, buffer attrs, payload/timestamp/flags, completions, and drain/DRC sub-states. Internal release responses remove and free internal DMA buffers.

## Dependencies And Integration Points
It depends on Gen2 packet/defines, V4L2 mem2mem, decoder source-change notification, VPU watchdog, VPU buffer counts, common HFI color conversion, queue read functions, state helpers, and `iris_vb2_buffer_done()`.

## Risks And Test Signals
Validation is stronger than Gen1 but still trusts `hdr->num_packets` after checking each packet stays inside the fixed response buffer. `iris_hfi_gen2_is_valid_hfi_port()` returns false for `HFI_PORT_NONE` before considering persist-buffer allowance, which may affect persist release responses. Tests should cover watchdog error, malformed packet sizes, multi-packet ordering where info/properties precede buffer command, no-output/corrupt/overflow picture flags, source-change subscription properties, AV1 film grain/super-block updates, zero-sized output frames, last/PSC-last flags, and internal buffer release for every internal type.
