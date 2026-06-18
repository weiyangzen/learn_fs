# sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/allegro-core.c

## Purpose

`allegro-core.c` is the main V4L2 mem2mem encoder driver for Allegro DVT AL5E/VCU hardware. It probes a platform device, loads MCU and codec firmware, initializes mailbox communication, exposes a `/dev/video*` mem2mem encoder, accepts raw NV12 output buffers, returns H.264 or HEVC elementary streams, and injects generated VPS/SPS/PPS/filler NAL units around firmware-produced frame payloads.

## Important APIs, Types, And Functions

- Device/channel state: `struct allegro_dev` owns V4L2 device/video device state, regmaps, clocks, firmware buffers, mailboxes, runtime init state, and the channel list. `struct allegro_channel` owns one open file context, V4L2 controls, negotiated formats, MCU channel ids, internal buffer lists, vb2 shadow lists, and completion/error state.
- Firmware compatibility: `struct fw_info` and `supported_firmware[]` identify known firmware pairs by firmware file size and set mailbox offsets, message version, and suballocator size.
- Address conversion helpers: `to_mcu_addr()`, `to_mcu_size()`, and `to_codec_addr()` translate CPU DMA addresses to MCU/codec address spaces and warn if an address is outside expected windows.
- Mailbox helpers: `allegro_mbox_init()`, `allegro_mbox_write()`, `allegro_mbox_read()`, `allegro_mbox_send()`, and `allegro_mbox_notify()` implement ring-buffer transfer through SRAM-backed mailbox registers.
- MCU message senders: `allegro_mcu_send_init()`, `allegro_mcu_send_create_channel()`, `allegro_mcu_send_destroy_channel()`, `allegro_mcu_send_put_stream_buffer()`, and `allegro_mcu_send_encode_frame()`.
- Channel creation/destruction: `fill_create_channel_param()`, `allegro_create_channel()`, `allegro_destroy_channel()`, `allegro_handle_create_channel()`, and buffer allocation helpers create firmware channels and push firmware-requested internal buffers.
- Bitstream header generation: `allegro_h264_write_sps()`, `allegro_h264_write_pps()`, `allegro_hevc_write_vps()`, `allegro_hevc_write_sps()`, and `allegro_hevc_write_pps()` fill NAL helper structs from V4L2 state.
- Frame completion: `allegro_channel_finish_frame()` validates firmware partition offsets, copies metadata, writes non-VCL NAL units into reserved capture-buffer space, marks source and destination buffers done, and emits EOS/keyframe flags.
- V4L2/vb2 entry points: `allegro_open()`, `allegro_release()`, format ioctls, stream parameter ioctls, `allegro_queue_setup()`, `allegro_buf_prepare()`, `allegro_buf_queue()`, `allegro_start_streaming()`, `allegro_stop_streaming()`, and `allegro_device_run()`.
- Platform/power flow: `allegro_probe()`, `allegro_remove()`, `allegro_fw_callback()`, `allegro_mcu_hw_init()`, `allegro_mcu_hw_deinit()`, `allegro_runtime_resume()`, and `allegro_runtime_suspend()`.

## Control Flow

Probe allocates `allegro_dev`, maps named `regs` and `sram` resources through regmap, looks up Xilinx VCU settings, gets core and MCU clocks, registers an IRQ thread, registers a V4L2 device, and starts asynchronous firmware loading. The firmware callback requests both `al5e_b.fw` and `al5e.fw`, matches their sizes against `supported_firmware[]`, enables runtime PM, resets the MCU, copies MCU firmware into SRAM, copies codec firmware into coherent DMA memory, initializes mailboxes, waits for firmware `INIT`, sends suballocator configuration, initializes the V4L2 mem2mem core, and registers the video node.

On open, the driver creates an `allegro_channel`, initializes controls for H.264, HEVC, bitrate, QP, GOP size, and the Allegro encoder-buffer control, creates source and destination vb2 queues via `v4l2_m2m_ctx_init()`, and links the channel into the device list. Capture stream-on triggers `allegro_create_channel()`: controls are grabbed, a unique user id is allocated, the create-channel blob is encoded and DMA-addressed, and the driver waits up to 5 seconds for firmware response. The response sets `mcu_channel_id`, decodes firmware-adjusted config, allocates intermediate and reference buffers, and sends those buffers back to firmware.

For each mem2mem job, `allegro_device_run()` removes one destination and one source buffer, sends the destination as a stream buffer, sends the source as an encode-frame request, records pointer handles in shadow lists, and finishes the mem2mem job immediately; actual completion is asynchronous through the IRQ thread. `allegro_irq_thread()` drains status mailbox messages and dispatches them. Encode-frame responses call `allegro_channel_finish_frame()`, which maps handles back to vb2 buffers, checks firmware error code and partition table bounds, writes parameter-set/filler NAL units into the pre-reserved offset area, sets payload/data-offset/keyframe metadata, and completes buffers.

Stop streaming tears down shadow lists and queued buffers; capture stop also destroys the firmware channel. Removal unregisters the video device, releases mem2mem state, deinitializes MCU hardware, frees codec firmware DMA memory, disables runtime PM, and unregisters V4L2 state.

## State And Persistence

Persistent runtime state is in memory and hardware registers. Device-level state includes firmware compatibility, suballocator/coherent firmware buffers, mailbox ring positions in SRAM, runtime PM clock state, and registered channels. Channel-level state includes negotiated raw and encoded formats, codec choice, frame rate, V4L2 control values, MCU channel id, firmware-requested internal buffers, source and stream shadow lists, frame sequences, and last error. The driver stores no data across module unload or reboot.

Mailbox state persists in the device SRAM head/tail words while the device is initialized. Firmware files are requested from the kernel firmware loader but not modified. V4L2 controls become immutable for a channel while the MCU channel exists via `v4l2_ctrl_grab()`.

## Dependencies And Integration Points

The driver depends on V4L2 core, V4L2 controls/events/ioctls, V4L2 mem2mem, videobuf2 DMA-contig, regmap MMIO, runtime PM, firmware loading, platform resources, IRQs, clocks, and Xilinx VCU syscon settings. It integrates with `allegro-mail.h/.c` for mailbox protocol serialization and `nal-h264`/`nal-hevc` helpers for generated parameter-set/filler NALs. Device tree integration is through compatible string `allegro,al5e-1.1`, named memory resources `regs` and `sram`, clocks `core_clk` and `mcu_clk`, and one IRQ.

## Risks

The firmware match uses firmware file sizes as ids, which is simple but fragile if firmware binaries change size without an intended protocol change. Mailbox wrap handling assumes message headers do not wrap and requires size alignment; corruption in SRAM head/tail values can lead to `-EIO`. `v4l2_cpb_size_to_mcu()` divides by bitrate in kbps, so zero bitrate or inconsistent control ranges would be dangerous. Parameter-set generation assumes enough reserved bytes before the firmware partition offset; frame completion fails if firmware chooses a too-small offset. Shadow-list handles are raw kernel pointers cast to `u64`, safe only inside this driver instance and protected by `shadow_list_lock`. Runtime PM depends on a valid `xlnx,vcu-settings` regmap; missing settings can block resume.

## Test Signals

Compile-test with `CONFIG_VIDEO_ALLEGRO_DVT=m` and allmodconfig catches API and link problems. Runtime validation should cover firmware loading success/failure, probe resource failures, stream-on timeout/error paths, H.264 and HEVC encoding, EOS commands, buffer underrun/stop-streaming cleanup, VBR/CBR and QP control clamping, generated SPS/PPS/VPS parsing with standard decoders, IRQ/mailbox drain behavior, and runtime suspend/resume. V4L2 compliance tools and mem2mem encode smoke tests with malformed buffer sizes are high-value signals.
