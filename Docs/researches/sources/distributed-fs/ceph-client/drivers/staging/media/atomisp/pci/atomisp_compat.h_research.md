# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_compat.h

## Purpose

`atomisp_compat.h` declares the AtomISP compatibility interface to the CSS 2.0/IA firmware layer. It is the command layer's abstraction boundary for CSS initialization, IRQ translation, buffer queue/dequeue, statistics/metadata allocation, input-system configuration, stream/pipe lifecycle, output/viewfinder frame-info configuration, ISP parameter get/set helpers, DVS/DIS controls, shading/morph table allocation, and CSS ISR processing.

## Important APIs, Types, and Functions

- `struct atomisp_metadata_buf` wraps a CSS metadata object, a host virtual pointer, and a list node. `atomisp_cmd.c` moves these objects through metadata free/in-CSS/ready lists and frees them when input resolution changes.
- Low-level access helpers `atomisp_css2_hw_store_32()` and `atomisp_load_uint32()` expose 32-bit hardware/CSS memory access by `hrt_address`.
- Lifecycle APIs include `atomisp_css_init()`, `atomisp_css_uninit()`, `atomisp_css_init_struct()`, `atomisp_create_pipes_stream()`, `atomisp_destroy_pipes_stream()`, `atomisp_css_start()`, `atomisp_css_stop()`, and `atomisp_css_update_stream()`.
- IRQ APIs include `atomisp_css_irq_translate()`, `atomisp_css_rx_get_irq_info()`, `atomisp_css_rx_clear_irq_info()`, `atomisp_css_irq_enable()`, `atomisp_css_isr_thread()`, and `atomisp_css_valid_sof()`.
- Buffer APIs include `atomisp_q_video_buffer_to_css()`, `atomisp_q_s3a_buffer_to_css()`, `atomisp_q_metadata_buffer_to_css()`, `atomisp_q_dis_buffer_to_css()`, `atomisp_css_queue_buffer()`, and `atomisp_css_dequeue_buffer()`.
- Statistics and metadata allocation/free APIs include `atomisp_css_allocate_stat_buffers()`, `atomisp_css_free_stat_buffers()`, CSS buffer-specific free helpers, grid-info queries, and allocation/free helpers for 3A, DIS, and metadata output.
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
