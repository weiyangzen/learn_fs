# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen2_command.c

## Purpose
`iris_hfi_gen2_command.c` implements the Gen2 HFI command operation table. It builds Gen2 header/sub-packet commands and properties for system init, session open/close/start/stop/pause/resume/drain, property configuration, subscribe mode, and buffer queue/release.

## Important APIs, Types, And Functions
System functions allocate packet buffers sized for init, no-payload, or IFPC messages and call packet helpers. Port mapping helpers convert V4L2 planes and Iris buffer types to HFI ports. Property setters cover raw/bitstream resolution, crop offsets, bit depth, coded frames, min output count, POC, colorspace, profile/level/tier, OPB, color format, linear stride/scanline, frame rate, AV1 film grain, and super-block. Session functions include `session_open()`, codec/default-header setup, subscribe-mode helpers, start/stop/pause/resume/drain, buffer conversion, COMV count setup, queue, and release.

## Control Flow
Open allocates a 4 KiB packet buffer, sends `HFI_CMD_OPEN` with response/interrupt flags, then sends codec and decoder default-header properties. Start first subscribes to port-setting-change and property notifications, then sends `HFI_CMD_START` for the plane. Subscribe-change stores input PSC params, and for output PSC copies source params to destination then sends current property values back on the raw port. Buffer queue converts `struct iris_buffer` into `struct iris_hfi_buffer`, aligns decoder bitstream size to 256, sets non-secure callback flag, optionally sets AV1 COMV count, and sends `HFI_CMD_BUFFER`.

## State And Persistence Behavior
The file updates Gen2 wrapper booleans `ipsc_properties_set`/`opsc_properties_set`, `src_subcr_params`, `dst_subcr_params`, and the reusable packet buffer. It also reuses generic state through completions, `inst->sub_state`, buffer attrs, timestamps, and `inst->hfi_rc_type` set by controls.

## Dependencies And Integration Points
It depends on Gen2 packet helpers/defines, common HFI ops, platform config/property arrays, format/crop/compose fields, VPU buffer counts, and controls. It is consumed through `core->hfi_ops` by common stream and buffer paths.

## Risks And Test Signals
The reusable packet buffer assumes all command/property packets fit in 4 KiB; platform arrays used for subscribe payloads should stay within the fixed local `payload[32]`. `iris_hfi_gen2_get_port_from_buf_type()` maps `BUF_PERSIST` to `HFI_PORT_NONE`, but response validation only accepts `HFI_PORT_NONE` for persist after an early port check that rejects non-bitstream/raw ports; release handling should be tested for persist buffers. Tests should cover every codec-specific config list, rotation/crop resolution packing, AV1 COMV count, subscribe idempotence, open failure cleanup, drain resume, and internal buffer release.
