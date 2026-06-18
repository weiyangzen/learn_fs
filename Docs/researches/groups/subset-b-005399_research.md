# Research: subset-b-005399

Work item `subset-b-005399` covers four AtomISP PCI command/compatibility files. Each source section below is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_cmd.c

## Purpose

`atomisp_cmd.c` is the central command, control, interrupt, buffer, parameter, and format-negotiation implementation for the staging AtomISP PCI camera driver. It bridges Linux V4L2/videobuf2 operations, sensor subdevices, PCI/MSI register control, IOSF/PMC dynamic frequency scaling, and Intel CSS/IA firmware APIs. The file is broad: it owns ISP reset/recovery, event delivery, CSS buffer dequeue completion, userspace ISP parameter ingestion, per-frame parameter association, sensor crop/format propagation, CSS pipe configuration, raw-buffer locking, and feature controls such as noise reduction, color effects, digital zoom, GDC/CAC, DIS/DVS, 3A statistics, metadata, and shading/morph tables.

## Important APIs, Types, and Functions

- `atomisp_to_sensor_mipi_info()` and `atomisp_to_video_pipe()` are container/hostdata helpers used by other driver paths to recover sensor MIPI metadata and the owning `atomisp_video_pipe`.
- `atomisp_freq_scaling()` and private `write_target_freq_to_hw()` implement dynamic frequency scaling. They select a frequency from `isp->dfs` rules based on sensor FPS, output resolution, and run mode, then program `ISPSSPM1` through `iosf_mbi_read()`/`iosf_mbi_write()`.
- `atomisp_reset()` power-cycles the ISP through `atomisp_power_off()` and `atomisp_power_on()`, setting `isp_fatal_error` if power-on fails.
- `atomisp_msi_irq_init()` and `atomisp_msi_irq_uninit()` configure PCI MSI, interrupt control, PCI command memory/master bits, and INTx disable state.
- `atomisp_isr()` is the hard IRQ handler. It translates CSS IRQ info, clears PCI interrupt state, emits SOF/EOF/error events, handles CSI receiver errors, and wakes `atomisp_isr_thread()` for CSS event processing.
- `atomisp_isr_thread()` serializes CSS ISR work under `isp->mutex` and calls `atomisp_css_isr_thread()`.
- `atomisp_assert_recovery_work()` performs assert recovery: disables SOF IRQs, marks streaming false, stops the sensor, clears CSS counters, stops CSS, notifies userspace of reset, resets hardware, recreates CSS streams, invalidates caches, restarts CSS and sensor streaming, runs DFS, flushes errored video buffers, and recovers per-frame parameters.
- `atomisp_buf_done()` dequeues one CSS buffer by type and routes it to the right V4L2/CSS state: 3A stats ready list, metadata ready list, DIS stats list, or output/VF video buffer completion.
- `atomisp_buffer_done()`, `atomisp_flush_video_pipe()`, `atomisp_buffers_in_css()`, `atomisp_flush_params_queue()`, `atomisp_handle_parameter_and_buffer()`, and `atomisp_move_frame_to_activeq()` manage videobuf2 completion and the relationship between active buffers, buffers waiting for per-frame parameters, and buffers already queued to CSS.
- Format conversion helpers include `v4l2_fmt_to_sh_fmt()`, `raw_output_format_match_input()`, `atomisp_get_pixel_depth()`, `atomisp_is_mbuscode_raw()`, `atomisp_fill_pix_format()`, and `atomisp_bytesperline_to_padded_width()`.
- ISP feature controls include `atomisp_gdc_cac()`, `atomisp_low_light()`, `atomisp_xnr()`, `atomisp_nr()`, `atomisp_tnr()`, `atomisp_black_level()`, `atomisp_ee()`, `atomisp_gamma()`, `atomisp_ctc()`, `atomisp_gamma_correction()`, `atomisp_formats()`, `atomisp_color_effect()`, `atomisp_bad_pixel()`, `atomisp_bad_pixel_param()`, `atomisp_video_stable()`, `atomisp_fixed_pattern()`, `atomisp_fixed_pattern_table()`, `atomisp_false_color()`, `atomisp_false_color_param()`, `atomisp_white_balance_param()`, `atomisp_3a_config_param()`, and `atomisp_digital_zoom()`.
- Complex parameter-copy helpers are `atomisp_cp_general_isp_parameters()`, `atomisp_cp_lsc_table()`, `atomisp_css_cp_dvs2_coefs()`, `atomisp_cp_dvs_6axis_config()`, `atomisp_cp_morph_table()`, `atomisp_makeup_css_parameters()`, `atomisp_apply_css_parameters()`, and `atomisp_free_css_parameters()`.
- Sensor/CSS format integration is handled by `atomisp_try_fmt()`, `atomisp_set_fmt()`, `atomisp_set_fmt_to_snr()`, `atomisp_set_fmt_to_isp()`, `atomisp_set_sensor_crop_and_fmt()`, `atomisp_set_sensor_mipi_to_isp()`, `css_input_resolution_changed()`, `atomisp_get_padding()`, `atomisp_get_dis_envelop()`, and `atomisp_check_copy_mode()`.
- Sensor selection and media topology are managed by `atomisp_s_sensor_power()`, `atomisp_select_input()`, and `atomisp_setup_input_links()`.
- Raw buffer lock operations are implemented by `atomisp_init_raw_buffer_bitmap()`, `atomisp_exp_id_capture()`, `atomisp_exp_id_unlock()`, and private bitmap helpers.

## Control Flow

The interrupt flow starts in `atomisp_isr()`. The handler takes `isp->lock`, rejects interrupts before CSS initialization, asks CSS to translate IRQ bits, clears the PCI interrupt register, and ignores most events if streaming is already stopped. SOF updates `asd->sof_count`, emits `V4L2_EVENT_FRAME_SYNC`, and advances `sequence_temp` only when frame processing has kept up. ISYS EOF events are dequeued and converted into `V4L2_EVENT_FRAME_END`. CSI receiver or input-system errors are printed and cleared for each MIPI port. Remaining events wake the threaded handler, which locks `isp->mutex` and lets CSS process queued firmware events.

The buffer-completion flow is CSS-driven. `atomisp_buf_done()` builds an `atomisp_css_buffer`, dequeues from CSS by stream, pipe, and buffer type, and then dispatches by `IA_CSS_BUFFER_TYPE_*`. Statistics and metadata are moved from in-CSS lists to ready lists and accompanied by V4L2 events. Output frames are completed through `atomisp_buffer_done()` under the owning pipe's `irq_lock`, which timestamps the vb2 buffer, sets field and sequence, updates payload for successful buffers, removes the frame from the driver list, and calls `vb2_buffer_done()`. After successful completions it may call `atomisp_qbuffers_to_css()` to refill CSS.

The parameter flow has global and per-frame paths. Global `atomisp_set_parameters()` copies userspace fields into `asd->params.css_param`, marks `css_update_params_needed`, and later `atomisp_buf_done()` applies the CSS parameter set and calls `atomisp_css_update_isp_params()`. Per-frame parameters allocate an `atomisp_css_params_with_list`, copy only the requested parameter objects into it, enqueue it on `pipe->per_frame_params`, and let `atomisp_handle_parameter_and_buffer()` match `isp_config_id` values against `pipe->frame_request_config_id[]` for buffers waiting in `buffers_waiting_for_param`. Once matched, frames move to `activeq` and are queued to CSS in order.

The format-setting flow begins with `atomisp_set_fmt()`, which validates the pipe, calls `atomisp_try_fmt()` to clamp/adjust the requested V4L2 pix format via a TRY-format call into the sensor, updates AtomISP subdevice sink/source media-bus formats, calculates padding and optional DVS envelope, sets the active sensor crop/format, configures CSI lanes, determines ISP2401 copy mode, updates compose rectangles, configures CSS input/pipe/output/frame-info objects, refreshes grid/stat buffers, and finally fills `pipe->pix` for the user-visible V4L2 format.

Recovery flow in `atomisp_assert_recovery_work()` is a coordinated stream reset. It stops streaming under both mutex and spinlock protection, stops the remote source, resets CSS counters and firmware state, emits reset notification, resets the PCI device side, reinitializes CSS input mode and streams, restarts CSS, reconfigures CSI2 and SOF IRQs, forces DFS recalculation, marks outstanding buffers as error, recovers unprocessed per-frame parameters, and restarts the sensor.

## State and Persistence Behavior

This file does not persist state to disk. It mutates live kernel driver state in `struct atomisp_device`, `struct atomisp_sub_device`, `struct atomisp_video_pipe`, and CSS-owned allocation objects. Persistent hardware state is limited to PCI configuration registers, IOSF/PMC frequency registers, ISP/CSS firmware state, HMM-backed frame data, and sensor subdevice register state reached through V4L2 calls.

Important live state includes `isp->css_initialized`, `isp->running_freq`, `isp->hpll_freq`, `isp->isp_fatal_error`, `isp->inputs[]`, `isp->sensor_lanes[]`, `asd->streaming`, `asd->params`, `asd->stream_env[]`, `asd->copy_mode`, `asd->input_curr`, `asd->sof_count`, `asd->sequence`, `asd->sequence_temp`, statistics/metadata ready and free lists, raw-buffer bitmap/count, and the video pipe queues `buffers_in_css`, `activeq`, `buffers_waiting_for_param`, and `per_frame_params`.

The locking model is explicit but fragile. `isp->lock` protects IRQ-visible streaming and sequence state. `isp->mutex` protects most CSS operations, parameter work, and buffer processing paths that call into CSS. Per-pipe `irq_lock` protects vb2 frame lists. `asd->dis_stats_lock` protects DIS statistics list moves. `raw_buffer_bitmap_lock` protects raw exposure ID bitmap state. Several functions assert the expected lock with `lockdep_assert_held()`, which is a useful test signal for call-site correctness.

Memory ownership is mixed. CSS table allocations for shading, morph, DVS coefficients, and DVS 6-axis data must be released by matching CSS free helpers. Per-frame parameter objects are `kvzalloc()`/`kvfree()` objects and may own nested CSS allocations. Metadata buffers are freed on input resolution change. Output frames are owned by vb2/CSS integration and are moved through list heads until completion.

## Dependencies and Integration Points

The file depends on Linux PCI, interrupt, runtime PM, timer, firmware, kfifo, V4L2 event/subdev, videobuf2, media-controller, IOSF MBI, HMM memory helpers, and many local AtomISP headers. The CSS/IA integration is especially deep: calls such as `atomisp_css_*`, `ia_css_*`, `sh_css_*`, `irq_*`, `cnd_sp_irq_enable()`, and `hmm_store()` make this file a high-level coordinator for firmware-visible ISP objects.

Primary upstream/downstream integration points are V4L2 ioctls and controls, V4L2 subdev pad operations, sensor control handlers, vb2 queue completion, media graph link flags, PCI config space, CSI2 port configuration, CSS stream/pipe configuration, CSS IRQ translation/dequeue APIs, AtomISP internal format bridge tables, and user ABI structures from `include/linux/atomisp.h`.

## Risks and Edge Cases

- The file has a large userspace-copy surface. Shading tables, morph tables, DVS coefficients, DVS 6-axis coordinates, 3A data, and framebuffers all copy pointer-rich structures. Size validation exists in several paths but should be reviewed for multiplication overflow and ABI layout differences, especially under `IS_ISP2401` branches that first copy wrapper structures.
- Error paths in allocation-heavy functions are subtle. For example, DVS/morph/shading copies free newly allocated CSS objects on copy failure, while some direct feature setters replace pointers and free old objects. Double-free, stale pointer, or leak regressions are plausible.
- Interrupt and recovery behavior depends on correct lock ordering between `isp->lock`, `isp->mutex`, pipe `irq_lock`, and CSS callbacks. Incorrect call sites can deadlock or race streamoff/IRQ processing.
- `atomisp_buf_done()` decrements in-CSS counters after list searches; malformed CSS events or unexpected missing buffers could underflow counters or leave lists inconsistent.
- Format negotiation intentionally disables raw output in `atomisp_try_fmt()` with a comment saying raw formats are broken. Any raw-format restoration must audit `raw_output_format_match_input()` and CSS output configuration.
- Sensor crop/format propagation touches old and new sensor-driver behavior, active/try states, optional sensor ISP subdevices, CSI ports, padding, binning, and DVS envelope fallback. This is a high regression area for sensor-specific bugs.
- `atomisp_assert_recovery_work()` uses broad cache invalidation (`wbinvd()`) and tries to recover without fully dequeuing CSS-owned buffers. This is hardware-sensitive and difficult to exercise in unit tests.
- Color effect control first tries the sensor control handler and falls back to ISP tables. Different sensors may therefore observe the same V4L2 request at different layers.

## Test Signals

Useful validation includes kernel build coverage for AtomISP staging sources, sparse/smatch checks for user pointer and address-space annotations, lockdep while streaming and changing formats, KASAN/KFENCE for parameter/table allocation paths, and V4L2 compliance focused on format negotiation, stream on/off, event subscription, and buffer completion. Hardware or emulated integration tests should cover IRQ SOF/EOF delivery, stream recovery, sensor selection/media-link updates, DFS frequency changes, DVS enable/disable fallback, per-frame parameter matching by `isp_config_id`, metadata/3A/DIS buffer dequeue, and repeated resolution changes to catch metadata/stat-buffer lifetime bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_cmd.h

## Purpose

`atomisp_cmd.h` is the public internal command header for `atomisp_cmd.c` and related AtomISP PCI driver files. It declares the helper, interrupt, feature-control, parameter-copy, format, sensor, raw-buffer, and power APIs used across the AtomISP staging driver. It also centralizes a few PCI interrupt bit constants used by MSI setup/teardown.

## Important APIs, Types, and Functions

The header forward-declares `struct atomisp_device` and `struct ia_css_frame`, includes the user AtomISP ABI, Linux interrupt/V4L2 headers, local internal driver state, and CSS type headers. It exports:

- PCI/MSI bit constants: `MSI_ENABLE_BIT`, `INTR_DISABLE_BIT`, `BUS_MASTER_ENABLE`, `MEMORY_SPACE_ENABLE`, `INTR_IER`, and `INTR_IIR`.
- Helper APIs: `dump_sp_dmem()`, `atomisp_to_sensor_mipi_info()`, `atomisp_to_video_pipe()`, `atomisp_reset()`, `atomisp_buffers_in_css()`, `atomisp_buffer_done()`, `atomisp_flush_video_pipe()`, and `atomisp_clear_css_buffer_counters()`.
- IRQ and recovery APIs: `atomisp_msi_irq_init()`, `atomisp_msi_irq_uninit()`, `atomisp_assert_recovery_work()`, `atomisp_isr()`, `atomisp_isr_thread()`, and EOF event injection through `atomisp_eof_event()`.
- Format helpers: `get_atomisp_format_bridge_from_mbus()`, `atomisp_is_mbuscode_raw()`, `atomisp_is_viewfinder_support()`, `atomisp_try_fmt()`, `atomisp_set_fmt()`, `atomisp_get_padding()`, and `atomisp_get_pixel_depth()`.
- ISP feature controls for GDC/CAC, low-light, XNR, formats, noise reduction, TNR, black level, edge enhancement, gamma/CTC/gamma correction, GDC/morph and MACC tables, DIS/DVS, 3A stats, parameter blocks, color effects, bad pixel, video stabilization, fixed pattern, false color, white balance, 3A config, digital zoom, array resolution, and shading tables.
- CSS-parameter support: `atomisp_cp_general_isp_parameters()`, `atomisp_cp_lsc_table()`, `atomisp_css_cp_dvs2_coefs()`, `atomisp_cp_morph_table()`, `atomisp_cp_dvs_6axis_config()`, `atomisp_makeup_css_parameters()`, `atomisp_apply_css_parameters()`, and `atomisp_free_css_parameters()`.
- Sensor and topology APIs: `atomisp_s_sensor_power()`, `atomisp_select_input()`, `atomisp_setup_input_links()`, and `atomisp_port_to_mipi_port()`.
- Buffer and per-frame APIs: `atomisp_buf_done()`, `atomisp_handle_parameter_and_buffer()`, and `atomisp_flush_params_queue()`.
- Raw exposure and event helper APIs: `atomisp_exp_id_unlock()`, `atomisp_exp_id_capture()`, `atomisp_init_raw_buffer_bitmap()`, `atomisp_enable_dz_capt_pipe()`, `atomisp_inject_a_fake_event()`, and `atomisp_get_invalid_frame_num()`.
- Power hooks: `atomisp_power_off()` and `atomisp_power_on()`.

## Control Flow and Integration

This header defines cross-file call boundaries rather than executable control flow. It exposes the commands used by ioctl/control paths, fops/streaming paths, IRQ registration, media graph setup, CSS compatibility layers, and power management. Most APIs take `struct atomisp_sub_device *`, `struct atomisp_device *`, `struct video_device *`, or `struct atomisp_video_pipe *`, making the subdevice/device/pipe split the organizing contract for callers.

The parameter-copy declarations reveal the two-stage parameter flow: user ABI structures are copied into `struct atomisp_css_params`, optional per-frame makeup combines partial parameter sets, then `atomisp_apply_css_parameters()` maps update flags into the active CSS configuration. The format declarations show a similar staged flow: try format, set sensor/input topology, configure CSS, and fill V4L2 pix format state.

## State and Persistence Behavior

The header itself has no persisted state and defines no storage except preprocessor constants. Its declarations mutate driver runtime state owned elsewhere: vb2 frame lists, CSS parameter allocations, sensor power state, media links, raw-buffer lock bitmaps, and hardware registers. Because many functions return `int` Linux error codes and operate on pointer-rich user ABI objects, callers must observe the locking and lifetime requirements implemented in `atomisp_cmd.c`.

## Dependencies and Integration Points

`atomisp_cmd.h` depends on `../../include/linux/atomisp.h`, `<linux/interrupt.h>`, `<linux/videodev2.h>`, V4L2 subdev declarations, `atomisp_internal.h`, `ia_css_types.h`, and `ia_css.h`. It is an internal driver header, not a stable external ABI; the stable-ish userspace structs come from `include/linux/atomisp.h`. It integrates the command implementation with AtomISP ioctl/fops/subdev files, CSS wrappers from `atomisp_compat.h`, and power-management functions that may be implemented outside `atomisp_cmd.c`.

## Risks and Edge Cases

- The header is very broad, so unrelated subsystems can easily grow dependencies on command-layer internals.
- Several prototypes expose raw user ABI structures and CSS allocation-bearing structures; wrong callers can leak memory or bypass expected locking.
- Some comments contain outdated spelling or behavior hints, so implementation should be treated as authoritative.
- `atomisp_power_off()` and `atomisp_power_on()` are declared here despite not being part of the command implementation body, creating a cross-module dependency that can be easy to miss during refactors.

## Test Signals

Compile coverage is the main signal for this header. Useful additional checks are include-what-you-use style dependency review, sparse address-space checking for functions that accept user pointers indirectly, and call-site audits for functions whose implementation asserts `isp->mutex`, pipe `irq_lock`, media graph mutex, or other locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_common.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_common.h

## Purpose

`atomisp_common.h` contains small shared definitions used by AtomISP PCI driver code: debug/padding globals, CSS trace and zoom constants, an ISP pipe-version flag, and two format-description structs. It is a lightweight common header that connects V4L2 media-bus pixel formats to CSS frame formats and user-visible V4L2 pixelformats.

## Important APIs, Types, and Constants

- External globals `dbg_level`, `dbg_func`, `pad_w`, and `pad_h` are declared here. `pad_w` and `pad_h` are used by command/format paths as default sensor padding when crop-aware padding cannot be derived.
- `ISP2400_MIN_PAD_W` and `ISP2400_MIN_PAD_H` define minimum padding requirements for BYT/ISP2400 paths. `atomisp_get_padding()` uses these as lower bounds when not running ISP2401.
- `CSS_DTRACE_VERBOSITY_LEVEL` and `CSS_DTRACE_VERBOSITY_TIMEOUT` define debug trace verbosity levels used by CSS diagnostic paths elsewhere.
- `MRFLD_MAX_ZOOM_FACTOR` is the digital zoom scale constant used by `atomisp_digital_zoom()`.
- `ATOMISP_CSS_ISP_PIPE_VERSION_2_7` identifies the ISP2401 CSS pipe version used by conditional code paths.
- `struct atomisp_format_bridge` maps a V4L2 `pixelformat`, bit `depth`, media-bus code, CSS `ia_css_frame_format`, textual description, and planar flag. It is the core format bridge used by try/set format paths.
- `struct atomisp_fmt` records concrete format dimensions and sizes: pixelformat, depth, bytesperline, framesize, imagesize, width, height, and bayer order.

## Control Flow and Integration

This header defines data contracts, not executable flow. `struct atomisp_format_bridge` is consumed by format lookup helpers such as `atomisp_get_format_bridge()` and `get_atomisp_format_bridge_from_mbus()`, then used by `atomisp_try_fmt()`, `atomisp_set_fmt()`, and `atomisp_fill_pix_format()` to translate V4L2 requests into CSS pipe configuration. The padding and zoom constants feed command-layer calculations.

## State and Persistence Behavior

The header declares global debug/padding variables but does not define them. Runtime state is held by the defining compilation unit and by the caller's format structures. There is no disk persistence. The values influence live sensor/ISP setup: padding affects requested sensor dimensions and crop behavior, while format bridge records determine bytesperline, sizeimage, CSS frame format, and media-bus propagation.

## Dependencies and Integration Points

The header includes the AtomISP userspace ABI header, Linux V4L2 media-bus definitions, videobuf2 V4L2 definitions, `atomisp_compat.h`, and `ia_css.h`. This makes it a shared bridge between Linux V4L2/vb2 types and Intel CSS types. It is included by `atomisp_cmd.c` and likely other AtomISP files that need common format metadata.

## Risks and Edge Cases

- Global `pad_w`/`pad_h` are externally mutable module parameters or globals; invalid values can affect sensor requests and format negotiation.
- `description[32]` mirrors V4L2 format descriptions and must stay bounded by table initializers.
- `struct atomisp_format_bridge` mixes user-visible and firmware-visible formats, so table mistakes can produce subtle bytesperline, padding, raw-order, or CSS output bugs.
- Constants are hardware-generation-specific; applying ISP2400 padding rules to ISP2401 paths, or vice versa, can regress format setup.

## Test Signals

Format enumeration, `VIDIOC_TRY_FMT`, `VIDIOC_S_FMT`, and sensor media-bus propagation tests are the best behavioral signals. Static checks should verify that all bridge table entries have consistent depth, planar flag, media-bus code, and CSS format. Runtime debug around `atomisp_get_padding()` and `atomisp_fill_pix_format()` can catch mismatches between bridge metadata and generated V4L2 `bytesperline`/`sizeimage`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_compat.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_compat.h

## Purpose

`atomisp_compat.h` declares the AtomISP compatibility interface to the CSS 2.0/IA firmware layer. It is the command layer's abstraction boundary for CSS initialization, IRQ translation, buffer queue/dequeue, statistics/metadata allocation, input-system configuration, stream/pipe lifecycle, output/viewfinder frame-info configuration, ISP parameter get/set helpers, DVS/DIS controls, shading/morph table allocation, and CSS ISR processing.

## Important APIs, Types, and Functions

- `struct atomisp_metadata_buf` wraps a CSS metadata object, a host virtual pointer, and a list node. `atomisp_cmd.c` moves these objects through metadata free/in-CSS/ready lists and frees them when input resolution changes.
- Low-level access helpers `atomisp_css2_hw_store_32()` and `atomisp_load_uint32()` expose 32-bit hardware/CSS memory access by `hrt_address`.
- Lifecycle APIs include `atomisp_css_init()`, `atomisp_css_uninit()`, `atomisp_css_init_struct()`, `atomisp_create_pipes_stream()`, `atomisp_destroy_pipes_stream()`, `atomisp_css_start()`, `atomisp_css_stop()`, and `atomisp_css_update_stream()`.
- IRQ APIs include `atomisp_css_irq_translate()`, `atomisp_css_rx_get_irq_info()`, `atomisp_css_rx_clear_irq_info()`, `atomisp_css_irq_enable()`, `atomisp_css_isr_thread()`, and `atomisp_css_valid_sof()`.
- Buffer APIs include `atomisp_q_video_buffer_to_css()`, `atomisp_q_s3a_buffer_to_css()`, `atomisp_q_metadata_buffer_to_css()`, `atomisp_q_dis_buffer_to_css()`, `atomisp_css_queue_buffer()`, and `atomisp_css_dequeue_buffer()`.
- Statistics and metadata allocation/free APIs include `atomisp_css_allocate_stat_buffers()`, `atomisp_css_free_stat_buffers()`, `atomisp_css_free_3a_buffer()`, `atomisp_css_free_dis_buffer()`, `atomisp_css_free_metadata_buffer()`, `atomisp_css_get_grid_info()`, `atomisp_alloc_3a_output_buf()`, `atomisp_alloc_dis_coef_buf()`, `atomisp_alloc_metadata_output_buf()`, and `atomisp_free_metadata_output_buf()`.
- Input-system configuration APIs include ISYS resolution/link/valid/format setters, default/two-stream config helpers, input resolution/binning/bayer/format/effective-resolution setters, two-pixels-per-clock, input mode, capture/preview online toggles, and MIPI port configuration.
- Pipe/output APIs configure copy, preview, capture, video, viewfinder, pp-input, offline capture, output frame info, and viewfinder frame info.
- ISP parameter helpers cover XNR, CTC table, DIS vector/coefs/stat, DVS2 coefs, zoom factor, white balance, OB, DP, DE, NR, EE, TNR, gamma, GC, 3A, format config, shading table, morph table, and capture-pipe digital zoom.
- Raw exposure ID APIs `atomisp_css_exp_id_capture()` and `atomisp_css_exp_id_unlock()` connect command-layer raw-buffer locking to CSS capture/unlock operations.

## Control Flow and Integration

This header defines the CSS-facing side of most control flows in `atomisp_cmd.c`. The command layer calls IRQ translation from the hard IRQ handler, then CSS ISR processing from the threaded IRQ handler. Format negotiation configures input systems and output pipes through this interface. Buffer completion dequeues CSS buffers and may queue more buffers through these declarations. Parameter copying creates local CSS parameter objects, then applies them by setting `asd->params.config` pointers and invoking CSS update calls. Recovery stops and restarts CSS streams through this API.

## State and Persistence Behavior

`atomisp_compat.h` itself stores no state, but nearly every function mutates CSS firmware state, CSS stream/pipe configuration, CSS-owned buffer queues, or allocation objects referenced by `atomisp_sub_device`. CSS state is volatile and must be reconstructed across reset/recovery. Some functions allocate objects whose lifetime is owned by AtomISP command state, especially stats, metadata, shading tables, morph tables, DVS2 coefficients, and DVS 6-axis configs.

## Dependencies and Integration Points

The header includes `atomisp_compat_css20.h` and the AtomISP userspace ABI header. It forward-declares AtomISP device/subdevice types and V4L2 video device, but relies on CSS types such as `ia_css_frame`, `ia_css_pipe`, `ia_css_frame_info`, `ia_css_metadata`, `ia_css_shading_table`, `ia_css_morph_table`, `ia_css_dvs2_coefficients`, and related enums being available through the CSS compatibility include. It is the main boundary between staging driver logic and Intel CSS firmware wrappers.

## Risks and Edge Cases

- The API surface is large and stateful; incorrect call ordering can leave CSS streams configured with stale dimensions, stale metadata buffers, or mismatched grid information.
- Queue/dequeue APIs take stream ID, pipe ID, and buffer type. Mismatches can return the wrong buffer or fail, especially in multi-stream cases noted by `atomisp_cmd.c`.
- Allocation/free ownership is split across command and compat layers. Callers must use the matching CSS free helper for every CSS allocation.
- Input-system setup differs by hardware generation and sensor metadata support. Fallback paths for sensors without pad media-bus formats depend on `camera_mipi_info`.
- Some APIs return `int` while others are `void`; void setters can hide CSS-side failures unless the implementation logs them.

## Test Signals

Integration tests should exercise CSS init/start/stop/restart, IRQ translation and threaded handling, buffer queue/dequeue for every supported `IA_CSS_BUFFER_TYPE_*`, stats/metadata allocation and resolution-change freeing, stream creation/destruction, format changes across preview/video/capture/copy modes, DVS/DIS grid updates, and raw exposure lock/unlock. Static analysis should focus on matching allocation/free pairs and verifying that every command-layer CSS call occurs under the intended `isp->mutex` or IRQ protection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_compat.h -->
