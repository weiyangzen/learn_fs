# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen1_response.c

## Purpose
`iris_hfi_gen1_response.c` parses Gen1 firmware messages, handles system/session errors, sequence changes, buffer completion, flush completion, image-version responses, and debug queue output.

## Important APIs, Types, And Functions
The installed response op is `iris_hfi_gen1_response_handler()`. Important helpers include `iris_hfi_gen1_read_changed_params()`, `iris_hfi_gen1_event_seq_changed()`, system/session error handlers, `iris_hfi_gen1_sys_init_done()`, image-version parsing, `iris_hfi_gen1_session_etb_done()`, `iris_hfi_gen1_session_ftb_done()`, and `iris_hfi_gen1_handle_response()`.

## Control Flow
The handler drains the message queue into `core->response_packet`, dispatches each packet by `hdr->pkt_type`, then drains debug queue. Packet type metadata in `pkt_infos[]` provides minimum-size validation. System init completes `core_init_done`; system property info logs firmware version. Event notify is routed to an instance if its session id matches, otherwise treated as system error. Sequence-change events parse changed properties, update source/destination formats, color metadata, crop, buffer size/min-count, and V4L2 min-buffer control, then trigger output flush and `iris_vdec_src_change()`. ETB done finds source buffers by input tag and completes them. FTB done handles decoder/encoder output, split-mode DPB matching, EOS/drain flags, picture type flags, corrupt/drop errors, and vb2 completion.

## State And Persistence Behavior
The file mutates `core->state`, all instance states on system error, `inst->fmt_src`, `fmt_dst`, `crop`, `fw_min_count`, buffer sizes/counts, V4L2 controls, queue min allocations, buffer attrs, sequence metadata through `iris_vb2_buffer_done()`, `flush_responses_pending`, and completions. Fatal session errors mark vb2 queues errored.

## Dependencies And Integration Points
It depends on Gen1 defines, V4L2 mem2mem, decoder source-change notification, VPU buffer counts, common HFI color conversion, queue read functions, state helpers, and buffer lifecycle functions.

## Risks And Test Signals
Parsing variable changed-parameter payloads has limited bounds checking beyond message minimum size; malformed firmware payloads could advance `data_ptr` incorrectly. Tests should cover all sequence-change property combinations, unsupported bit depth/pic structure, EOS with zero filled length, split-mode DPB return, corrupt/drop flags, flush response counting, image-version packet length validation, and unknown packet handling.
