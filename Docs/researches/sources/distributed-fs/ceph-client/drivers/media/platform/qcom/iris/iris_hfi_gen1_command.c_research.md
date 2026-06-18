# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen1_command.c

## Purpose
`iris_hfi_gen1_command.c` implements the Gen1 HFI command operation table. It builds legacy Gen1 packet structs for system init/properties, session open/start/stop/close, buffer queue/release, drain, and session configuration properties.

## Important APIs, Types, And Functions
The file installs `iris_hfi_gen1_command_ops`. Key functions include system packet builders (`sys_init`, image version, IFPC, PC prep), `iris_hfi_gen1_session_open()`, `session_start()`, `session_stop()`, `session_continue()`, input/output/internal buffer queue functions, internal buffer release, drain, and `iris_hfi_gen1_session_set_config_params()`. Property helpers translate common config into Gen1-specific structs such as `hfi_framesize`, `hfi_uncompressed_format_select`, `hfi_buffer_count_actual`, `hfi_multi_stream`, `hfi_buffer_size_actual`, `hfi_framerate`, and encoder rate/QP structs.

## Control Flow
Session open maps V4L2 codec and domain to Gen1 codec/session values, writes `HFI_CMD_SYS_SESSION_INIT`, and waits for response. Decoder/encoder start on output plane sends load-resources then start and sets `IRIS_INST_SUB_LOAD_RESOURCES`. Stop handles decoder streaming flush, decoder loaded-but-not-streaming stop/release, and encoder stop/release, completing queued vb2 buffers with error as needed. Queueing dispatches by `buf->type`: input uses empty-buffer packets, output/DPB uses fill-buffer packets, internals use set-buffers packets. Release sends `HFI_CMD_SESSION_RELEASE_BUFFERS` for non-input buffers and destroys internals after firmware response.

## State And Persistence Behavior
The file mutates `inst->sub_state`, waits on `inst->completion` or `flush_completion`, increments `flush_responses_pending`, and destroys released internal buffers. Gen1 packets are stack or temporary heap allocations. Split-mode decoder maps visible output and DPB streams across `HFI_BUFFER_OUTPUT`/`OUTPUT2`.

## Dependencies And Integration Points
It depends on Gen1 defines, `iris_instance`, `iris_vpu_buffer`, HFI queues, state helpers, controls, and buffer lifecycle code. It is invoked by common streaming and controls through `core->hfi_ops`.

## Risks And Test Signals
Risks include packet size calculation errors for flexible arrays, buffer type translation gaps, stop/flush response accounting, and split-mode stream-id mistakes. Test with decoder and encoder streamon/streamoff, drain, DRC, internal buffer release, unsupported codec, queue-full failure, and all platform config parameter lists. A code-level risk is that `iris_set_profile_level_gen1()` in controls passes `sizeof(u32)` for a `struct hfi_profile_level`; property packing should be verified against firmware expectations.
