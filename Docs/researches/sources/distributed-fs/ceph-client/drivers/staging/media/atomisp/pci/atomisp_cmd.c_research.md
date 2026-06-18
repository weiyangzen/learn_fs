# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_cmd.c

## Purpose

`atomisp_cmd.c` is the central command, control, interrupt, buffer, parameter, and format-negotiation implementation for the staging AtomISP PCI camera driver. It bridges Linux V4L2/videobuf2 operations, sensor subdevices, PCI/MSI register control, IOSF/PMC dynamic frequency scaling, and Intel CSS/IA firmware APIs. The file is broad: it owns ISP reset/recovery, event delivery, CSS buffer dequeue completion, userspace ISP parameter ingestion, per-frame parameter association, sensor crop/format propagation, CSS pipe configuration, raw-buffer locking, and feature controls such as noise reduction, color effects, digital zoom, GDC/CAC, DIS/DVS, 3A statistics, metadata, and shading/morph tables.

## Important APIs, Types, and Functions

- `atomisp_to_sensor_mipi_info()` and `atomisp_to_video_pipe()` are container/hostdata helpers used by other driver paths to recover sensor MIPI metadata and the owning `atomisp_video_pipe`.
- `atomisp_freq_scaling()` and private `write_target_freq_to_hw()` implement dynamic frequency scaling. They select a frequency from `isp->dfs` rules based on sensor FPS, output resolution, and run mode, then program `ISPSSPM1` through `iosf_mbi_read()`/`iosf_mbi_write()`.
- `atomisp_reset()` power-cycles the ISP through `atomisp_power_off()` and `atomisp_power_on()`, setting `isp_fatal_error` if power-on fails.
- `atomisp_isr()` is the hard IRQ handler. It translates CSS IRQ info, clears PCI interrupt state, emits SOF/EOF/error events, handles CSI receiver errors, and wakes `atomisp_isr_thread()` for CSS event processing.
- `atomisp_assert_recovery_work()` performs assert recovery by stopping sensor/CSS state, notifying userspace, resetting hardware, recreating CSS streams, restarting CSS and sensor streaming, forcing DFS, flushing errored buffers, and recovering per-frame parameters.
- `atomisp_buf_done()` dequeues one CSS buffer by type and routes it to the right V4L2/CSS state: 3A stats ready list, metadata ready list, DIS stats list, or output/VF video buffer completion.
- `atomisp_buffer_done()`, `atomisp_flush_video_pipe()`, `atomisp_flush_params_queue()`, and `atomisp_handle_parameter_and_buffer()` manage vb2 completion, active queues, in-CSS queues, and per-frame parameter matching.
- ISP feature controls include GDC/CAC, low-light, XNR, NR/TNR, black level, edge enhancement, gamma/CTC/gamma correction, color effects, bad pixel, video stabilization, fixed pattern, false color, white balance, 3A config, and digital zoom.
- Complex parameter-copy helpers are `atomisp_cp_general_isp_parameters()`, `atomisp_cp_lsc_table()`, `atomisp_css_cp_dvs2_coefs()`, `atomisp_cp_dvs_6axis_config()`, `atomisp_cp_morph_table()`, `atomisp_makeup_css_parameters()`, `atomisp_apply_css_parameters()`, and `atomisp_free_css_parameters()`.
- Sensor/CSS format integration is handled by `atomisp_try_fmt()`, `atomisp_set_fmt()`, `atomisp_set_fmt_to_snr()`, `atomisp_set_fmt_to_isp()`, `atomisp_set_sensor_crop_and_fmt()`, `atomisp_set_sensor_mipi_to_isp()`, `css_input_resolution_changed()`, `atomisp_get_padding()`, `atomisp_get_dis_envelop()`, and `atomisp_check_copy_mode()`.

## Control Flow

The interrupt flow starts in `atomisp_isr()`. The handler takes `isp->lock`, rejects interrupts before CSS initialization, asks CSS to translate IRQ bits, clears the PCI interrupt register, and ignores most events if streaming is already stopped. SOF updates `asd->sof_count`, emits `V4L2_EVENT_FRAME_SYNC`, and advances `sequence_temp` only when frame processing has kept up. ISYS EOF events are dequeued and converted into `V4L2_EVENT_FRAME_END`. CSI receiver or input-system errors are printed and cleared for each MIPI port. Remaining events wake the threaded handler, which locks `isp->mutex` and lets CSS process queued firmware events.

The buffer-completion flow is CSS-driven. `atomisp_buf_done()` builds an `atomisp_css_buffer`, dequeues from CSS by stream, pipe, and buffer type, and then dispatches by `IA_CSS_BUFFER_TYPE_*`. Statistics and metadata are moved from in-CSS lists to ready lists and accompanied by V4L2 events. Output frames are completed through `atomisp_buffer_done()` under the owning pipe's `irq_lock`, which timestamps the vb2 buffer, sets field and sequence, updates payload for successful buffers, removes the frame from the driver list, and calls `vb2_buffer_done()`.

The parameter flow has global and per-frame paths. Global `atomisp_set_parameters()` copies userspace fields into `asd->params.css_param`, marks `css_update_params_needed`, and later `atomisp_buf_done()` applies the CSS parameter set and calls `atomisp_css_update_isp_params()`. Per-frame parameters allocate an `atomisp_css_params_with_list`, copy requested parameter objects into it, enqueue it on `pipe->per_frame_params`, and let `atomisp_handle_parameter_and_buffer()` match `isp_config_id` values against `pipe->frame_request_config_id[]` for buffers waiting in `buffers_waiting_for_param`.

The format-setting flow begins with `atomisp_set_fmt()`, which validates the pipe, calls `atomisp_try_fmt()` to clamp/adjust the requested V4L2 pix format via a TRY-format call into the sensor, updates AtomISP subdevice sink/source media-bus formats, calculates padding and optional DVS envelope, sets active sensor crop/format, configures CSI lanes, determines ISP2401 copy mode, updates compose rectangles, configures CSS input/pipe/output/frame-info objects, refreshes grid/stat buffers, and fills `pipe->pix`.

Recovery flow in `atomisp_assert_recovery_work()` is a coordinated stream reset. It stops streaming under both mutex and spinlock protection, stops the remote source, resets CSS counters and firmware state, emits reset notification, resets the PCI device side, reinitializes CSS input mode and streams, restarts CSS, reconfigures CSI2 and SOF IRQs, forces DFS recalculation, marks outstanding buffers as error, recovers unprocessed per-frame parameters, and restarts the sensor.

## State and Persistence Behavior

This file does not persist state to disk. It mutates live kernel driver state in `struct atomisp_device`, `struct atomisp_sub_device`, `struct atomisp_video_pipe`, and CSS-owned allocation objects. Persistent hardware state is limited to PCI configuration registers, IOSF/PMC frequency registers, ISP/CSS firmware state, HMM-backed frame data, and sensor subdevice register state reached through V4L2 calls.

Important live state includes `isp->css_initialized`, `isp->running_freq`, `isp->hpll_freq`, `isp->isp_fatal_error`, `isp->inputs[]`, `isp->sensor_lanes[]`, `asd->streaming`, `asd->params`, `asd->stream_env[]`, `asd->copy_mode`, `asd->input_curr`, `asd->sof_count`, `asd->sequence`, `asd->sequence_temp`, statistics/metadata ready and free lists, raw-buffer bitmap/count, and the video pipe queues `buffers_in_css`, `activeq`, `buffers_waiting_for_param`, and `per_frame_params`.

The locking model uses `isp->lock` for IRQ-visible streaming and sequence state, `isp->mutex` for most CSS operations, pipe `irq_lock` for vb2 frame lists, `asd->dis_stats_lock` for DIS moves, and `raw_buffer_bitmap_lock` for exposure ID bitmaps.

## Dependencies and Integration Points

The file depends on Linux PCI, interrupt, runtime PM, timer, firmware, kfifo, V4L2 event/subdev, videobuf2, media-controller, IOSF MBI, HMM memory helpers, and many local AtomISP headers. The CSS/IA integration is deep: `atomisp_css_*`, `ia_css_*`, `sh_css_*`, `irq_*`, `cnd_sp_irq_enable()`, and `hmm_store()` calls make this file a high-level coordinator for firmware-visible ISP objects.

Primary integration points are V4L2 ioctls and controls, V4L2 subdev pad operations, sensor control handlers, vb2 queue completion, media graph link flags, PCI config space, CSI2 port configuration, CSS stream/pipe configuration, CSS IRQ translation/dequeue APIs, AtomISP internal format bridge tables, and user ABI structures from `include/linux/atomisp.h`.

## Risks and Edge Cases

- The userspace-copy surface is large: shading, morph, DVS coefficients, DVS 6-axis coordinates, 3A data, and framebuffers all copy pointer-rich structures.
- Allocation-heavy error paths can leak, double-free, or leave stale pointers if CSS table lifetimes are changed without matching free helpers.
- Interrupt and recovery behavior depends on correct lock ordering between `isp->lock`, `isp->mutex`, pipe `irq_lock`, and CSS callbacks.
- `atomisp_buf_done()` decrements in-CSS counters after list searches; malformed CSS events or unexpected missing buffers could underflow counters or leave lists inconsistent.
- Raw formats are intentionally disabled in `atomisp_try_fmt()` because comments describe them as broken.
- Sensor crop/format propagation is a high regression area because it spans old sensor behavior, active/try states, optional sensor ISP subdevices, CSI ports, padding, binning, and DVS fallback.

## Test Signals

Useful validation includes kernel build coverage, sparse/smatch checks for user pointer and address-space annotations, lockdep while streaming and changing formats, KASAN/KFENCE for parameter/table allocation paths, and V4L2 compliance focused on format negotiation, stream on/off, event subscription, and buffer completion. Hardware integration should cover IRQ SOF/EOF delivery, stream recovery, sensor selection/media-link updates, DFS frequency changes, DVS fallback, per-frame parameter matching by `isp_config_id`, metadata/3A/DIS dequeue, and repeated resolution changes.
