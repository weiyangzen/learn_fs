# subset-b-005401 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_subdev.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_subdev.h

Purpose: defines the V4L2/media subdevice side of the atomisp driver, including the ISP subdevice, its sink/source pads, the single video output pipe, cached CSS parameter blocks, metadata/statistics queues, streaming flags, and helper prototypes used by the main PCI/V4L2 driver.

Important APIs/types/functions: key types are `atomisp_video_pipe`, `atomisp_pad_format`, `atomisp_css_params`, `atomisp_subdev_params`, `atomisp_css_params_with_list`, and `atomisp_sub_device`. The exported helpers cover media-bus format lookup/conversion, active/try format and selection access, pending event cleanup, entity registration, subdevice initialization, and teardown.

Control flow: this header does not execute logic directly, but it defines the state container that `atomisp_v4l2.c`, format negotiation, vb2 queue handling, CSS parameter setting, and IRQ completion paths share. The video pipe tracks buffers in CSS, buffers pending CSS handoff, and per-frame parameter lists. The subdevice tracks the current input, streaming state, stream preparation, resume recreation, raw-buffer locking, and CSS statistics queues.

State and persistence: all state is runtime-only in the `atomisp_device`/`atomisp_sub_device` graph. Persistent behavior is delegated to sensor firmware, PCI config, and CSS firmware; this header mainly describes in-memory queues, cached frame formats, and cached ISP parameter values.

Dependencies and integration: depends on V4L2 controls/subdevs, media pads/pipelines, videobuf2, atomisp common/compat layers, and the Intel CSS `ia_css` API. It is the central contract between atomisp video nodes, the internal ISP subdevice, MIPI CSI2 entities, and CSS parameter code.

Risks and test signals: lock ordering is explicitly constrained because `vb_queue_mutex` must precede `isp->mutex`. The many lists and IRQ-protected buffer states need stress tests around stream-on/off, per-frame parameter queuing, metadata/statistics dequeue, suspend/resume, and error unwinds. Format negotiation tests should cover compressed/uncompressed media-bus codes and source/sink selection rectangles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_subdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_tables.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_tables.h

Purpose: provides static ISP color/effect tuning tables used by atomisp image effects. It contains color correction matrices for sepia, negative, and mono, MACC tables for skin, blue, and green effects, and a CTC table for vivid rendering.

Important APIs/types/functions: the file exports header-local `static` data objects: `sepia_cc_config`, `nega_cc_config`, `mono_cc_config`, `skin_low_macc_table`, `skin_medium_macc_table`, `skin_high_macc_table`, `blue_macc_table`, `green_macc_table`, and `vivid_ctc_table`. These use CSS types from `sh_css_params.h`.

Control flow: there is no runtime control flow. Inclusion gives a translation unit private copy of the tables and callers select/copy them into CSS parameter structures when enabling user-visible effects.

State and persistence: the tables are compile-time constants in practice, though not declared `const`. They do not persist user state and do not mutate hardware directly.

Dependencies and integration: integrated with CSS color correction, MACC, and CTC configuration paths. The values must match CSS firmware expectations for table shape and fixed-point interpretation.

Risks and test signals: because the objects are `static` in a header and not `const`, each includer can get mutable private storage and accidental writes are possible. Build tests should catch CSS type layout changes; image-effect tests should verify visual output and parameter upload for each effect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_tables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_trace_event.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_trace_event.h

Purpose: declares atomisp tracepoints for camera memory diagnostics, debug breadcrumbs, and IPU C-state/P-state telemetry.

Important APIs/types/functions: trace events are `camera_meminfo`, `camera_debug`, `ipu_cstate`, and `ipu_pstate`. They use standard Linux tracepoint macros, fixed-size string arrays copied with `strscpy()`, and `TRACE_INCLUDE_FILE`/`TRACE_INCLUDE_PATH` metadata for trace generation.

Control flow: when the header is included in the trace definition compilation path, `TRACE_EVENT` expands to event descriptors. Runtime callers emit trace records through generated `trace_*` functions, for example power state code emits `trace_ipu_cstate()`.

State and persistence: trace records are ephemeral kernel tracing data. The file stores no persistent driver state.

Dependencies and integration: depends on `<linux/tracepoint.h>` and the kernel tracing build convention that includes `<trace/define_trace.h>` outside the include guard. It integrates with atomisp memory accounting and runtime power/frequency paths.

Risks and test signals: fixed 24-byte strings truncate names and debug info. Format changes affect trace consumers, so tests are kernel build coverage with tracing enabled, runtime trace capture during power transitions, and verifying event fields remain stable for scripts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_trace_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_v4l2.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_v4l2.c

Purpose: implements the PCI driver and top-level V4L2/media integration for Intel Atom ISP2. It binds supported SoC PCI IDs, selects hardware revision and DFS tables, loads CSS firmware, initializes MIPI CSI2 and ISP subdevices, registers media/video nodes, handles runtime PM through IOSF P-unit control, and tears the device down.

Important APIs/types/functions: exported helpers are `atomisp_video_init()`, `atomisp_video_unregister()`, `atomisp_power_off()`, `atomisp_power_on()`, `atomisp_csi_lane_config()`, `atomisp_register_device_nodes()`, and `atomisp_load_firmware()`. Internal core paths include `atomisp_save_iunit_reg()`, `atomisp_restore_iunit_reg()`, `atomisp_mrfld_pre_power_down()`, `atomisp_mrfld_power()`, `atomisp_suspend()`, `atomisp_resume()`, `atomisp_subdev_probe()`, `atomisp_register_entities()`, `atomisp_init_sensor()`, `atomisp_initialize_modules()`, `atomisp_pm_init()`, `atomisp_pci_probe()`, and `atomisp_pci_remove()`.

Control flow: probe allocates `atomisp_device`, identifies the PCI ID/revision, chooses DFS and HPLL parameters, requests firmware, optionally enters PM-only mode if firmware is missing, enables PCI/MMIO/MSI, applies hardware workarounds, initializes CSI2 and ISP subdevices, creates the media graph, requests IRQs, loads CSS firmware, enables runtime PM, and registers the async notifier. Remove reverses PM, CSS, IRQ, HMM, media entities, module initialization, MSI, and IRQ vector setup. Power-on/off bypass normal PCI PM and directly use IOSF to control IUNIT power, saving/restoring PCI/IUNIT context and coordinating CSS init/uninit.

State and persistence: module parameters `dbg_level`, `dbg_func`, `pad_w`, and `pad_h` affect runtime behavior. Per-device state persists only for the lifetime of the PCI device: saved config registers, media graph, CSS firmware state, PM QoS, sensor lane maps, DFS config, and `pm_only`. Hardware/firmware state is restored from cached registers after power transitions.

Dependencies and integration: depends on PCI, runtime PM, PM domains, PM QoS, IOSF MBI, DMI/GMIN platform helpers, V4L2 fwnode/media/subdev APIs, vb2/video fops/ioctls, atomisp IRQ/CSS/HMM/DFS helpers, and Intel IPU bridge namespaces. It is the root integration point for atomisp user-visible `/dev/video*` nodes and internal CSS firmware.

Risks and test signals: failure unwinds are long and order-sensitive, especially around firmware release, IRQ vectors, HMM, media unregister, and PM-only mode. Power paths rely on hardware-specific workarounds and timeouts; interrupt clearing before power-down can return `-EAGAIN`. CSI lane matching must reject unsupported lane combinations. Test signals are probe/remove with and without firmware, runtime suspend/resume while idle, streaming suspend rejection, media graph links for sensors and sensor-ISP chains, firmware fallback path, IRQ request failure unwinds, and CHT/MRFLD/BYT PCI ID coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_v4l2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_v4l2.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_v4l2.h

Purpose: declares the top-level atomisp V4L2/PCI helpers used by other atomisp components.

Important APIs/types/functions: forward declares `atomisp_video_pipe`, `v4l2_device`, `atomisp_device`, and `firmware`, and declares `atomisp_video_init()`, `atomisp_video_unregister()`, `atomisp_load_firmware()`, `atomisp_csi_lane_config()`, and `atomisp_register_device_nodes()`.

Control flow: no direct runtime flow; it is the shared interface for video device setup, firmware selection, CSI lane programming, and node registration implemented in `atomisp_v4l2.c`.

State and persistence: the header stores no state. All persistent runtime effects occur through `atomisp_device` and hardware touched by the implementation.

Dependencies and integration: included by subdevice and command layers that need to initialize the video pipe or register the complete media graph without including the full PCI implementation.

Risks and test signals: prototype drift is the main risk. Compile tests across atomisp translation units catch signature mismatches; runtime graph registration tests validate the declared lifecycle contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_v4l2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/base/circbuf/interface/ia_css_circbuf.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/base/circbuf/interface/ia_css_circbuf.h

Purpose: defines the public CSS circular-buffer abstraction over a descriptor plus an element array.

Important APIs/types/functions: `ia_css_circbuf_t` stores pointers to `ia_css_circbuf_desc_t` and `ia_css_circbuf_elem_t` arrays. Non-inline APIs include `ia_css_circbuf_create()`, `ia_css_circbuf_destroy()`, `ia_css_circbuf_pop()`, `ia_css_circbuf_extract()`, `ia_css_circbuf_peek()`, `ia_css_circbuf_peek_from_start()`, and `ia_css_circbuf_increase_size()`. Inline helpers set/copy elements, calculate wrapped positions and offsets, test empty/full, push/write values, and compute free/used elements.

Control flow: callers initialize a descriptor size, create the ring with an external element array, push or write values at `end`, pop from `start`, peek relative to `start` or `end`, and optionally grow the descriptor size when backing storage has spare capacity.

State and persistence: ring state is the descriptor's `size`, `start`, `end`, and `step`, plus element values. It is in-memory only and owned by the caller.

Dependencies and integration: depends on CSS support headers for types, assertions, math wrapping, and platform support. Used by CSS queues/taggers where compact firmware-compatible layouts matter.

Risks and test signals: the API relies heavily on assertions and does not provide locking despite comments about lockless use. Full/empty distinction consumes one padding slot, but `get_free_elems()` returns descriptor free slots without subtracting the reserved padding. Tests should cover wraparound, negative offsets, full assertions, extract shifting, growth across wrapped `end`, and descriptor-size overflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/base/circbuf/interface/ia_css_circbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/base/circbuf/interface/ia_css_circbuf_comm.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/base/circbuf/interface/ia_css_circbuf_comm.h

Purpose: defines the portable data layout shared by CSS circular-buffer descriptors and elements.

Important APIs/types/functions: `ia_css_circbuf_desc_t` has `u8 size`, `u8 step`, `u8 start`, and `u8 end`. `ia_css_circbuf_elem_t` stores a single `u32 val`. `IA_CSS_CIRCBUF_PADDING` documents the extra slot used to distinguish full from empty, and `static_assert()` checks firmware-facing structure sizes.

Control flow: no executable control flow. The definitions are consumed by descriptor and ring operations.

State and persistence: structures are caller-owned runtime state; their compact field sizes also imply an on-wire or firmware ABI expectation.

Dependencies and integration: depends on Linux `static_assert` support and CSS type aliases. It is included by both descriptor and full circular-buffer interfaces.

Risks and test signals: descriptor fields are 8-bit, so sizes and indices above 255 cannot be represented. ABI size assertions are important build-time tests. Runtime tests should confirm callers allocate one extra element for `IA_CSS_CIRCBUF_PADDING`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/base/circbuf/interface/ia_css_circbuf_comm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/base/circbuf/interface/ia_css_circbuf_desc.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/base/circbuf/interface/ia_css_circbuf_desc.h

Purpose: provides inline operations on the circular-buffer descriptor independent of the backing element array.

Important APIs/types/functions: functions include `ia_css_circbuf_desc_is_empty()`, `ia_css_circbuf_desc_is_full()`, `ia_css_circbuf_desc_init()`, `ia_css_circbuf_desc_get_pos_at_offset()`, `ia_css_circbuf_desc_get_offset()`, `ia_css_circbuf_desc_get_num_elems()`, and `ia_css_circbuf_desc_get_free_elems()`.

Control flow: helpers compute modular positions with `OP_std_modadd()`, normalize negative offsets by adding `size`, and derive occupancy from `start` to `end`.

State and persistence: only the descriptor's runtime fields are read or initialized. `desc_init()` sets `size` but leaves `start`, `end`, and `step` for `ia_css_circbuf_create()`.

Dependencies and integration: included by the main circular-buffer interface and uses CSS math/assert/platform helpers.

Risks and test signals: callers must avoid zero sizes before modular arithmetic. `get_free_elems()` does not account for the unusable padding slot, which can surprise users of the lockless full/empty convention. Tests should cover zero-size rejection by assertions, wrap offsets, and full/empty boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/base/circbuf/interface/ia_css_circbuf_desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/base/circbuf/src/circbuf.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/base/circbuf/src/circbuf.c

Purpose: implements non-inline CSS circular-buffer operations: create/destroy, pop, arbitrary extraction, peeking, and size growth.

Important APIs/types/functions: public functions are `ia_css_circbuf_create()`, `ia_css_circbuf_destroy()`, `ia_css_circbuf_pop()`, `ia_css_circbuf_extract()`, `ia_css_circbuf_peek()`, `ia_css_circbuf_peek_from_start()`, and `ia_css_circbuf_increase_size()`. Internal helpers are `ia_css_circbuf_read()`, `ia_css_circbuf_shift_chunk()`, and `ia_css_circbuf_elem_get_val()`.

Control flow: create resets descriptor positions and clears all elements. Pop asserts non-empty, reads and clears `start`, then advances it. Extract pops offset zero, returns zero for offsets beyond current occupancy, otherwise reads a target element and shifts older elements toward the hole before adjusting `start`. Growth validates `u8` size addition, optionally appends new elements, and fixes wrapped `end`/`start` placement.

State and persistence: mutates only caller-owned descriptor and element array. Destroy nulls pointers but does not free storage.

Dependencies and integration: built on the inline descriptor/ring API and CSS assertion support. It serves CSS firmware-side queue logic such as taggers.

Risks and test signals: no locking is provided. `extract()` does not explicitly reject negative offsets, so modular offset behavior can expose unexpected positions. Growth assumes preallocated storage and has a FIXME-like comment about maximum size. Unit tests should cover invalid offsets, wrapped extraction, growth when `end < start`, element clearing, and caller-managed storage lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/base/circbuf/src/circbuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/base/refcount/interface/ia_css_refcount.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/base/refcount/interface/ia_css_refcount.h

Purpose: declares a CSS reference-count registry for `ia_css_ptr` allocations, keyed by an integer owner ID.

Important APIs/types/functions: `clear_func` is a callback for freeing/clearing referenced objects. Public functions are `ia_css_refcount_init()`, `ia_css_refcount_uninit()`, `ia_css_refcount_increment()`, `ia_css_refcount_decrement()`, `ia_css_refcount_is_single()`, `ia_css_refcount_clear()`, and `ia_css_refcount_is_valid()`.

Control flow: callers initialize a fixed-size registry, increment entries for shared CSS/HMM pointers, decrement to free when the count reaches zero, clear all objects for an ID, and uninitialize at shutdown.

State and persistence: the implementation owns a process-wide static registry; pointer counts are runtime-only and are lost on driver unload.

Dependencies and integration: depends on CSS type, error, and HMM pointer definitions. It is part of CSS memory ownership around HMM allocations.

Risks and test signals: the interface does not expose locking or capacity management. Tests should exercise double initialization, zero-size init, increment/decrement ID mismatches, capacity exhaustion, clear callbacks, and valid/single queries after free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/base/refcount/interface/ia_css_refcount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/base/refcount/src/refcount.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/base/refcount/src/refcount.c

Purpose: implements the CSS refcount registry over a single static array of `ia_css_refcount_entry` records.

Important APIs/types/functions: `myrefcount` stores `size` and `items`. `refcount_find_entry()` locates an existing pointer or first free slot. Public functions allocate/free the registry with `kvmalloc()`/`kvfree()`, maintain counts, call `hmm_free()` on final decrement, clear entries by owner ID, and validate pointer membership.

Control flow: init rejects size zero and double init, allocates and zeroes entries. Increment locates or creates an entry, checks owner ID, and increments count. Decrement checks pointer and ID, decrements, frees through HMM at zero, and resets entry metadata. Clear iterates all entries matching an ID and calls a supplied callback, then asserts counts are zero. Uninit frees any remaining managed HMM pointers before releasing the registry.

State and persistence: all state lives in the global `myrefcount`. It persists across CSS operations until uninit, but not beyond module lifetime.

Dependencies and integration: uses HMM allocation/freeing, CSS debug tracing, assertions, and CSS error/warning macros. It participates in memory lifetime for CSS buffers.

Risks and test signals: there is no synchronization around the global table, so concurrent CSS users can race. `ia_css_refcount_clear()` asserts callback non-null even though it contains a fallback branch. `ia_css_refcount_is_single()` returns true for untracked non-null pointers, which can mask missing registration. Tests should include concurrent access review, capacity exhaustion, stale pointer decrement, nonzero clear counts, and uninit leak cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/base/refcount/src/refcount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/bits.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/bits.h

Purpose: supplies HRT bit-mask and bitfield helper macros for fixed-width register packing.

Important APIs/types/functions: `_hrt_ones(n)` maps constants 0 through 32 to masks, and helpers `_hrt_mask()`, `_hrt_get_bits()`, `_hrt_set_bits()`, `_hrt_get_bit()`, `_hrt_set_bit()`, `_hrt_set_lower_half()`, and `_hrt_set_upper_half()` build on those masks.

Control flow: all behavior is macro expansion. The macros compute masks, extract shifted fields, and update ranges inside a word.

State and persistence: no state. Effects occur only in expressions evaluated by callers.

Dependencies and integration: depends on Linux `CONCATENATE()` from `<linux/args.h>`. Used by atomisp HRT-generated register configuration code.

Risks and test signals: `_hrt_ones(n)` only works for compile-time tokens with defined mappings. Shift behavior depends on integer width, and `_hrt_set_bit()` uses `1 << b` rather than an unsigned wider literal. Tests are compile-time coverage of generated users and runtime bitfield examples for boundary widths 0, 1, 16, 31, and 32.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/pipe/interface/ia_css_pipe_binarydesc.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/pipe/interface/ia_css_pipe_binarydesc.h

Purpose: declares helpers that construct CSS binary descriptors for copy, preview, video, capture, viewfinder post-processing, scaler, and multi-stage ISP pipelines.

Important APIs/types/functions: exported descriptor builders include `ia_css_pipe_get_copy_binarydesc()`, `ia_css_pipe_get_vfpp_binarydesc()`, `ia_css_pipe_get_preview_binarydesc()`, `ia_css_pipe_get_video_binarydesc()`, `ia_css_pipe_get_yuvscaler_binarydesc()`, `ia_css_pipe_get_capturepp_binarydesc()`, `ia_css_pipe_get_primary_binarydesc()`, `ia_css_pipe_get_pre_gdc_binarydesc()`, `ia_css_pipe_get_gdc_binarydesc()`, `ia_css_pipe_get_post_gdc_binarydesc()`, `ia_css_pipe_get_pre_de_binarydesc()`, `ia_css_pipe_get_pre_anr_binarydesc()`, `ia_css_pipe_get_anr_binarydesc()`, `ia_css_pipe_get_post_anr_binarydesc()`, `ia_css_pipe_get_ldc_binarydesc()`, `sh_css_bds_factor_get_fract()`, and `binarydesc_calculate_bds_factor()`.

Control flow: callers pass a configured `ia_css_pipe` plus input/output/vf frame-info buffers. Implementations populate `ia_css_binary_descr` fields used by binary lookup and may modify frame-info structures.

State and persistence: no state is stored in the header. Implementations can update `pipe->required_bds_factor` as a side effect.

Dependencies and integration: depends on CSS pipe, frame, and binary descriptor types. It is a core interface between high-level pipe configuration and firmware binary selection.

Risks and test signals: output parameters are in/out and some may be nullable by convention, so callers must match each function's expectations. Tests should cover every pipe mode, raw/YUV input changes, BDS/fractional downscale combinations, and descriptor fields that control firmware binary lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/pipe/interface/ia_css_pipe_binarydesc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/pipe/interface/ia_css_pipe_stagedesc.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/pipe/interface/ia_css_pipe_stagedesc.h

Purpose: declares helpers that convert binaries, firmware blobs, or SP functions into CSS pipeline stage descriptors.

Important APIs/types/functions: `ia_css_pipe_get_generic_stage_desc()`, `ia_css_pipe_get_firmwares_stage_desc()`, and `ia_css_pipe_get_sp_func_stage_desc()` fill `ia_css_pipeline_stage_desc` fields for binary-backed, firmware-backed, and SP-function-backed stages.

Control flow: no direct logic in the header. Callers use these helpers while assembling CSS pipelines after binary descriptor lookup.

State and persistence: stage descriptors are caller-owned runtime objects. The helpers do not allocate persistent state.

Dependencies and integration: depends on CSS firmware info, frame, binary, and pipeline-common types.

Risks and test signals: descriptor correctness is crucial because later pipeline execution trusts stage fields. Tests should validate binary, firmware, and SP-only stage assembly, including multi-output arrays and null vf/in frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/pipe/interface/ia_css_pipe_stagedesc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/pipe/interface/ia_css_pipe_util.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/pipe/interface/ia_css_pipe_util.h

Purpose: declares small CSS pipe utility helpers for input-format bit depth and output-frame array handling.

Important APIs/types/functions: `ia_css_pipe_util_pipe_input_format_bpp()` derives bits per pixel from a pipe's stream config. `ia_css_pipe_util_create_output_frames()` initializes a frame pointer array, and `ia_css_pipe_util_set_output_frames()` assigns a frame at a checked output index.

Control flow: no direct header control flow. Implementations are simple wrappers used by pipe descriptor and pipeline assembly code.

State and persistence: no stored state; helpers mutate caller-provided frame pointer arrays.

Dependencies and integration: depends on CSS pipe/frame public types and integrates with binary/stage descriptor code.

Risks and test signals: index bounds rely on assertions. Tests should cover all input formats, two-pixels-per-clock cases, and output arrays sized to `IA_CSS_BINARY_MAX_OUTPUT_PORTS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/pipe/interface/ia_css_pipe_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/pipe/src/pipe_binarydesc.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/pipe/src/pipe_binarydesc.c

Purpose: implements binary descriptor construction for CSS pipeline stages and computes Bayer downscaling factors.

Important APIs/types/functions: the internal `pipe_binarydesc_get_offline()` initializes common descriptor defaults. Public builders specialize descriptor mode, online/continuous/two-ppc flags, stream format, frame formats, BDS info, DVS/DZ/TNR/DPC/YUV downscale flags, high-speed/reduced-pipe flags, and ISP pipe version. `bds_factors_list`, `sh_css_bds_factor_get_fract()`, and `binarydesc_calculate_bds_factor()` map enum factors to rational scales and select a factor by resolution.

Control flow: each builder copies or derives `in_info`, `out_info`, `vf_info`, and optional `bds_out_info`, then calls the common initializer and applies mode-specific fields. Preview/video paths compute effective input size and raw bit depth, choose copy mode for YUV input, optionally compute or default raw binning BDS, update `pipe->required_bds_factor`, and disable BDS info when fractional downscale is enabled. Primary/capture/GDC/ANR helpers adapt frame format and raw bit depth for their stage.

State and persistence: mostly stack/output-parameter mutation. Persistent side effects are `pipe->required_bds_factor` and any caller-observed frame-info changes.

Dependencies and integration: depends on CSS frame format/public APIs, pipe config, input-format utilities, debug tracing, `sh_css_params`, and GDC constants. It feeds firmware binary selection and later stage descriptor assembly.

Risks and test signals: many assertions document non-null expectations, but some comments allow nulls. `binarydesc_calculate_bds_factor()` uses integer division and a fixed rounding margin, so edge resolutions can fail or choose unexpected factors. Tests should cover preview/video raw binning, fractional downscale, YUV copy fallback, online two-ppc streams, primary HQ stage bounds, and each frame-format conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/pipe/src/pipe_binarydesc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/pipe/src/pipe_stagedesc.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/pipe/src/pipe_stagedesc.c

Purpose: fills CSS pipeline stage descriptors from already selected binaries, firmware entries, or SP functions.

Important APIs/types/functions: `ia_css_pipe_get_generic_stage_desc()` validates a binary-backed stage and copies binary mode, input, output, and vf frame pointers. `ia_css_pipe_get_firmwares_stage_desc()` fills a descriptor with both binary and firmware pointers plus an explicit mode. `ia_css_pipe_get_sp_func_stage_desc()` describes a standalone SP function with optional output frame and maximum input width.

Control flow: each helper assigns all relevant descriptor fields and initializes unused fields to null or `IA_CSS_PIPELINE_NO_FUNC`. Generic stage creation logs and returns early on invalid arguments.

State and persistence: no global state. The only mutation is the caller-provided `ia_css_pipeline_stage_desc`.

Dependencies and integration: depends on CSS pipeline common structures, binary metadata, firmware info, assertions, and debug tracing. Called during pipeline construction after binary lookup.

Risks and test signals: generic stage creation assumes `out_frame` has `IA_CSS_BINARY_MAX_OUTPUT_PORTS` entries. Firmware stage creation does not validate inputs. Tests should cover invalid binary info, multi-output copy, firmware mode propagation, and SP-only stage setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/pipe/src/pipe_stagedesc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/pipe/src/pipe_util.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/pipe/src/pipe_util.c

Purpose: implements small CSS pipe helpers used by descriptor and pipeline code.

Important APIs/types/functions: `ia_css_pipe_util_pipe_input_format_bpp()` delegates to `ia_css_util_input_format_bpp()` using the pipe stream format and `pixels_per_clock == 2`. `ia_css_pipe_util_create_output_frames()` nulls each output frame slot. `ia_css_pipe_util_set_output_frames()` assigns one output slot after asserting the index is in range.

Control flow: functions are straight-line wrappers around assertions and assignment.

State and persistence: mutates only caller-provided frame arrays. No persistent state.

Dependencies and integration: depends on CSS pipe/frame public APIs and format utility code. Used before binary descriptor selection and stage descriptor assembly.

Risks and test signals: null pipe/stream and out-of-range indices are assertion-only failures. Tests should include bpp mapping for supported atomisp input formats and output array initialization before stage creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/pipe/src/pipe_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/util/interface/ia_css_util.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/util/interface/ia_css_util.h

Purpose: declares common CSS validation and format utility helpers.

Important APIs/types/functions: public functions include `ia_css_convert_errno()`, `ia_css_util_check_vf_info()`, `ia_css_util_check_input()`, `ia_css_util_check_vf_out_info()`, `ia_css_util_check_res()`, `ia_css_util_res_leq()`, `ia_css_util_resolution_is_zero()`, `ia_css_util_input_format_bpp()`, `ia_css_util_is_input_format_raw()`, and `ia_css_util_is_input_format_yuv()`.

Control flow: no implementation in the header. Callers use these checks before stream/pipe construction and descriptor selection.

State and persistence: none.

Dependencies and integration: depends on CSS error, frame, stream, and atomisp input-format types.

Risks and test signals: validation semantics determine which formats/resolutions reach firmware. Tests should cover raw/YUV requirements, zero and odd dimensions, viewfinder maximum width, and unsupported formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/util/interface/ia_css_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/util/src/util.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/util/src/util.c

Purpose: implements CSS utility validation and atomisp input-format classification.

Important APIs/types/functions: `ia_css_util_input_format_bpp()` maps atomisp input formats to bit depth, `ia_css_util_check_vf_info()` and `ia_css_util_check_vf_out_info()` validate frame info, `ia_css_util_check_res()` rejects zero or odd widths, `ia_css_util_res_leq()` compares dimensions, `ia_css_util_resolution_is_zero()` tests either dimension zero, `ia_css_util_is_input_format_raw()`/`_yuv()` classify formats, and `ia_css_util_check_input()` validates stream configuration against raw/YUV requirements.

Control flow: most helpers are switch or predicate logic. Frame checks delegate to `ia_css_frame_check_info()` and `ia_css_binary_max_vf_width()`. Input validation rejects missing stream configs, zero effective resolution, and mismatched required formats.

State and persistence: no state; all behavior is derived from arguments.

Dependencies and integration: used by pipe descriptor code and stream validation before firmware binary selection.

Risks and test signals: `ATOMISP_INPUT_FORMAT_RGB_565` maps to `65`, likely a typo for 16 and a high-risk value if used. Raw 14/16 are deliberately not raw ISP inputs except copy paths. Tests should cover every enum mapping, two-ppc RAW14/RAW16 behavior, odd width rejection with odd height allowance, and raw/YUV classification drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/camera/util/src/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/cell_params.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/cell_params.h

Purpose: defines SP cell memory/cache/fifo parameter constants for the atomisp CSS build.

Important APIs/types/functions: macros describe SP PMEM log width, icache tag/set/associativity/block address bits, derived `SP_ICACHE_ADDRESS_BITS`, `SP_PMEM_DEPTH`, FIFO depths, and `SP_SLV_BUS_MAXBURSTSIZE`.

Control flow: no executable flow. These constants feed compile-time sizing and hardware model configuration.

State and persistence: none.

Dependencies and integration: uses `BIT()` for `SP_PMEM_DEPTH` and is consumed by CSS/SP low-level code that needs cell dimensions.

Risks and test signals: hardware parameter drift can break firmware memory layout. Build tests and firmware load/boot tests are the main signals; static checks should ensure `BIT()` is available to includers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/cell_params.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/csi_rx_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/csi_rx_global.h

Purpose: defines shared CSI RX frontend/backend configuration structures and declares per-controller capability arrays.

Important APIs/types/functions: `csi_mipi_packet_type_t` classifies undefined, long, short, and reserved MIPI packet types. `csi_rx_backend_lut_entry_t` stores long/short LUT entries. `csi_rx_backend_cfg_t` combines LUT entries with virtual channel, data type, compression scheme, predictor, and bit index. `csi_rx_frontend_cfg_t` stores active lane count. Extern arrays describe short/long LUT counts, frontend data-lane counts, and backend SID width.

Control flow: no direct flow. Host configuration code uses these structures to prepare CSI receiver frontend/backend programming.

State and persistence: structures are caller-owned runtime config; extern arrays are read-only hardware capabilities defined in `host/csi_rx.c`.

Dependencies and integration: depends on system ID enums such as `N_CSI_RX_BACKEND_ID` and `N_CSI_RX_FRONTEND_ID`. It links CSI RX host wrappers with MIPI backend register programming.

Risks and test signals: capability arrays must match actual hardware IDs. Tests should validate lane/LUT bounds for all three CSI receiver instances and compression/custom packet setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/csi_rx_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/csi_rx.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/csi_rx.c

Purpose: defines hardware capability arrays for CSS 2401 CSI RX frontend/backend instances.

Important APIs/types/functions: constants are `N_SHORT_PACKET_LUT_ENTRIES`, `N_LONG_PACKET_LUT_ENTRIES`, `N_CSI_RX_FE_CTRL_DLANES`, and `N_CSI_RX_BE_SID_WIDTH`.

Control flow: no runtime control flow beyond static initialization. Consumers index these arrays by frontend/backend ID.

State and persistence: read-only global constants. They persist for module lifetime.

Dependencies and integration: includes `system_global.h` and `csi_rx_global.h`; used by private state-dump/access helpers and CSI configuration code.

Risks and test signals: incorrect counts cause out-of-range register reads/writes or missing LUT programming. Tests should cover all backend IDs, especially backend0's larger long-packet LUT and three-bit SID width.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/csi_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/csi_rx_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/csi_rx_local.h

Purpose: defines local state snapshot structures for CSI RX frontend and backend controllers.

Important APIs/types/functions: `csi_rx_fe_ctrl_lane_t` stores `termen` and `settle`. `csi_rx_fe_ctrl_state_t` captures frontend enable, lane count, error handling, status, lane status, clock lane, and data lanes. `csi_rx_be_ctrl_state_t` captures backend enable/status, compression registers, raw16/raw18/force-raw8 controls, IRQ status, custom-mode fields, LUT disregard/stall status, and short/long packet LUT entries.

Control flow: none in the header. Private helpers fill these structures from MMIO registers and dump them.

State and persistence: snapshot-only runtime state; not persistent and not authoritative for hardware.

Dependencies and integration: depends on `csi_rx_global.h` capability constants and HRT data types.

Risks and test signals: fixed array sizes must cover maximum hardware counts. State dump tests should verify backend0 long LUT entries do not exceed `N_CSI_RX_BE_LONG_PACKET_LUT` and disabled custom registers remain handled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/csi_rx_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/csi_rx_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/csi_rx_private.h

Purpose: provides inline device-level and native-command helpers for CSI RX frontend/backend register access, state capture, and debug dumps.

Important APIs/types/functions: DLI helpers are `csi_rx_fe_ctrl_reg_load()`, `csi_rx_fe_ctrl_reg_store()`, `csi_rx_be_ctrl_reg_load()`, and `csi_rx_be_ctrl_reg_store()`. NCI helpers include `csi_rx_fe_ctrl_get_dlane_state()`, `csi_rx_fe_ctrl_get_state()`, `csi_rx_fe_ctrl_dump_state()`, `csi_rx_be_ctrl_get_state()`, and `csi_rx_be_ctrl_dump_state()`.

Control flow: register helpers assert valid IDs/base addresses and perform 32-bit MMIO loads/stores using register index times word size. State getters read known registers and loop over lane/LUT counts from global arrays. Dumpers print captured fields.

State and persistence: writes mutate hardware registers. State structures are snapshots. No software persistence beyond caller variables.

Dependencies and integration: depends on generated HRT register indices from `rx_csi_defs.h` and `mipi_backend_defs.h`, CSI ID/base arrays, `device_access`, assertions, and print support.

Risks and test signals: this header defines non-static inline-like functions depending on storage-class macros from public headers; duplicate definition rules matter. Some custom-mode backend reads are disabled under `#if 0` due to device access errors, so diagnostic coverage is incomplete. Tests should validate ID assertions, FE lane loops, BE LUT loops, and register address calculations on all CSI instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/csi_rx_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/ibuf_ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/ibuf_ctrl.c

Purpose: defines per-IBUF-controller process counts for the CSS 2401 input buffer controller block.

Important APIs/types/functions: `N_IBUF_CTRL_PROCS` maps three controller IDs to 8, 4, and 4 supported processes.

Control flow: static initialization only. Consumers use the array to bound process-register loops.

State and persistence: read-only runtime constant.

Dependencies and integration: includes `system_global.h` and `ibuf_ctrl_global.h`; integrates IBUF controller host code with generated system IDs.

Risks and test signals: wrong counts lead to invalid register access or incomplete state collection. Tests should cover all IBUF controller IDs and process loop bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/ibuf_ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/ibuf_ctrl_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/ibuf_ctrl_local.h

Purpose: defines state snapshot structures for IBUF controller shared and per-process registers.

Important APIs/types/functions: `ibuf_ctrl_proc_state_t` records command/ack, item/store counts, DMA channel/command, input-buffer and destination addresses/strides/end addresses, sync/store commands, element packing, current counts/addresses, DMA command count, and FSM states. `ibuf_ctrl_state_t` stores shared recalculation/arbiter status and an array of process states.

Control flow: no direct logic; private/register-dump code fills these structs.

State and persistence: snapshot-only; hardware state remains in registers.

Dependencies and integration: depends on `ibuf_ctrl_global.h` for register definitions and `N_STREAM2MMIO_SID_ID`.

Risks and test signals: the header includes itself after `ibuf_ctrl_global.h`, which is harmless under include guards but suspicious. Tests should validate state capture layout against `_IBUF_CNTRL_*` register definitions and max SID counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/ibuf_ctrl_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_dma.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_dma.c

Purpose: provides CSS 2401 ISYS DMA capability data and a helper to configure maximum burst size.

Important APIs/types/functions: `N_ISYS2401_DMA_CHANNEL_PROCS` exposes the channel count per DMA ID. `isys2401_dma_set_max_burst_size()` writes the DDR connection max burst register with `max_burst_size - 1`.

Control flow: the setter asserts a valid DMA ID and burst size in 1..255, then stores to the DMA device-info register for the DDR connection.

State and persistence: writes persist in the ISYS DMA hardware register until reset/reconfiguration. The channel-count array is read-only module state.

Dependencies and integration: depends on `system_local.h`, `isys_dma_global.h`, `isys_dma_private.h`, DMA register macros, and device access.

Risks and test signals: burst size validation is assertion-only, so production behavior depends on assertion configuration. Tests should verify register index calculation, boundary burst values, and DMA ID bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_dma_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_dma_private.h

Purpose: implements private ISYS DMA register load/store helpers.

Important APIs/types/functions: `isys2401_dma_reg_store()` computes `ISYS2401_DMA_BASE[dma_id] + reg * sizeof(hrt_data)` and stores a 32-bit value. `isys2401_dma_reg_load()` computes the same address, loads a 32-bit value, and prints diagnostics.

Control flow: both helpers assert valid DMA ID and base address, calculate a word-indexed MMIO address, then call `ia_css_device_store_uint32()` or `ia_css_device_load_uint32()`.

State and persistence: store mutates hardware registers; load has no software state except debug output.

Dependencies and integration: depends on ISYS DMA public declarations, `device_access`, assertions, DMA register definitions, and print support.

Risks and test signals: functions are defined in a header, so include/storage-class discipline matters. Register IDs are not range checked beyond the caller's use. Tests should validate address arithmetic, base-address invalid assertions, and noisy print behavior in hot paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_dma_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_irq.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_irq.c

Purpose: implements the public ISYS IRQ controller enable sequence.

Important APIs/types/functions: `isys_irqc_status_enable()` writes mask, clear, and enable registers using constants from `isys_irq_global.h`.

Control flow: the function asserts a valid IRQ controller ID, logs the operation, writes `ISYS_IRQ_MASK_REG_VALUE`, clears pending bits with `ISYS_IRQ_CLEAR_REG_VALUE`, and enables status with `ISYS_IRQ_ENABLE_REG_VALUE`.

State and persistence: modifies ISYS IRQ hardware registers; state persists until disabled, cleared, or reset.

Dependencies and integration: depends on system IDs, device access, assertions, CSS debug tracing, public `isys_irq.h`, and private helpers when not using inline builds.

Risks and test signals: mask/clear/enable values are broad `0xFFFF`, so hardware bit definitions must match. Tests should validate enable sequence ordering, status clearing, and no invalid controller access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_irq_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_irq_local.h

Purpose: defines the ISYS IRQ controller state snapshot structure.

Important APIs/types/functions: `isys_irqc_state_t` stores `edge`, `mask`, `status`, `enable`, and `level_no`. The write-only `clear` register is intentionally omitted/commented.

Control flow: no direct flow; private helpers populate and dump this structure.

State and persistence: snapshot-only runtime state.

Dependencies and integration: depends on `type_support.h` for `hrt_data` and is used by `isys_irq_private.h`.

Risks and test signals: reading a write-only clear register is avoided by design. Tests should confirm state capture covers readable registers and does not attempt invalid reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_irq_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_irq_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_irq_private.h

Purpose: provides private ISYS IRQ controller register access plus state capture and dump helpers.

Important APIs/types/functions: `isys_irqc_state_get()` reads edge, mask, status, enable, and level/no-pulse registers. `isys_irqc_state_dump()` logs the snapshot. `isys_irqc_reg_store()` and `isys_irqc_reg_load()` compute register addresses from `ISYS_IRQ_BASE` and word indexes.

Control flow: state capture calls the load helper for readable register indices. Store/load assert controller and register bounds, calculate address, trace the operation, and access hardware through `ia_css_device_*`.

State and persistence: register stores mutate hardware; snapshots are caller-owned.

Dependencies and integration: depends on global/local IRQ headers, CSS debug tracing, and device access. Used by `isys_irq.c` and diagnostic code.

Risks and test signals: only `reg_idx <= ISYS_IRQ_LEVEL_NO_REG_IDX` is checked; semantic read/write constraints remain caller responsibility. Tests should cover readable state capture, write-only clear behavior, and register address correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_irq_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_stream2mmio.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_stream2mmio.c

Purpose: defines the number of stream IDs supported by each CSS 2401 Stream2MMIO controller.

Important APIs/types/functions: `N_STREAM2MMIO_SID_PROCS` maps controller 0 to all SIDs and controllers 1/2 to four SIDs.

Control flow: static initialization only. Consumers loop up to the count for a controller.

State and persistence: read-only global constant.

Dependencies and integration: includes `isys_stream2mmio.h`; used by private state capture/dump code and input-buffer controller integration.

Risks and test signals: count mismatch causes invalid or missing SID register access. Tests should cover all Stream2MMIO controllers and SID loop bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_stream2mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_stream2mmio_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_stream2mmio_local.h

Purpose: defines Stream2MMIO state snapshot structures.

Important APIs/types/functions: `stream2mmio_sid_state_t` captures receive acknowledgements, pixel width, start/end addresses, stride, number of items, and block-when-no-command for one SID. `stream2mmio_state_t` stores an array of SID states.

Control flow: no direct logic; private helpers fill and print these snapshots.

State and persistence: snapshot-only and caller-owned.

Dependencies and integration: depends on `isys_stream2mmio_global.h` for ID/count types.

Risks and test signals: fixed array size must match the maximum SID enum. Tests should validate state capture for controllers with 8 and 4 active SIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_stream2mmio_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_stream2mmio_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_stream2mmio_private.h

Purpose: provides Stream2MMIO state capture, printing, and MMIO register access helpers.

Important APIs/types/functions: local register IDs define eight registers per SID. NCI helpers are `stream2mmio_get_state()`, `stream2mmio_get_sid_state()`, `stream2mmio_print_sid_state()`, and `stream2mmio_dump_state()`. DLI helpers are `stream2mmio_reg_load()` and `stream2mmio_reg_store()`.

Control flow: state capture loops from SID0 to `N_STREAM2MMIO_SID_PROCS[ID]`, reading each SID's ack, pixel width, addresses, stride, item count, and blocking flag. Loads compute a bank offset of `STREAM2MMIO_REGS_PER_SID * sid_id`; stores accept a flat register index.

State and persistence: stores mutate hardware. Captured state is transient.

Dependencies and integration: depends on public Stream2MMIO declarations, controller bases, device access, assertions, and print support. It feeds diagnostics and IBUF/stream routing code.

Risks and test signals: `stream2mmio_reg_load()` asserts controller ID but not SID or reg bounds, and store takes a flat `reg` rather than SID/reg pair. Tests should verify controller-specific SID limits, address arithmetic, and blocked-input behavior when no command is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_stream2mmio_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/pixelgen_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/pixelgen_local.h

Purpose: defines a state snapshot for the CSS 2401 pixel generator controller.

Important APIs/types/functions: `pixelgen_ctrl_state_t` stores common enable, PRBS seed registers, sync-generator SID/free-run/pause/frame/pixel/line/blanking/status fields, and TPG mode/mask/delta/color registers.

Control flow: no direct flow. Private helpers read these fields from pixelgen registers and dump them.

State and persistence: snapshot-only; actual pixel generator configuration persists in hardware registers.

Dependencies and integration: depends on `pixelgen_global.h` for public config types and HRT data types.

Risks and test signals: state structure must stay aligned with `PixelGen_SysBlock_defs.h`. Tests should capture/dump PRBS, sync generator, and TPG modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/pixelgen_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/pixelgen_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/pixelgen_private.h

Purpose: provides pixel generator register access plus state capture and dump helpers.

Important APIs/types/functions: DLI helpers are `pixelgen_ctrl_reg_load()` and `pixelgen_ctrl_reg_store()`. NCI helpers are `pixelgen_ctrl_get_state()` and `pixelgen_ctrl_dump_state()`.

Control flow: register helpers assert valid pixelgen ID/base and access word-indexed registers. `pixelgen_ctrl_get_state()` reads common, PRBS, sync generator, and TPG register indices from `PixelGen_SysBlock_defs.h`. The dump helper prints the captured values.

State and persistence: stores mutate pixel generator hardware; snapshots are transient.

Dependencies and integration: depends on pixelgen public/local definitions, HRT register indices, and CSS device access. Used for test-pattern/synthetic input diagnostics.

Risks and test signals: dump prints `tpg_hcnt_mask` twice and omits a distinct `tpg_vcnt_mask` line, reducing diagnostic quality. Tests should validate register read order, enable bits for PRBS/TPG/sync generator, and state dump correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/pixelgen_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/hrt/PixelGen_SysBlock_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/hrt/PixelGen_SysBlock_defs.h

Purpose: defines generated register indices, widths, enable values, and magic constants for the pixel generator system block.

Important APIs/types/functions: register index macros cover common enable, PRBS reset values, sync generator configuration/status, and TPG mode/mask/delta/color registers. Width macros document bit widths. Enable values distinguish PRBS, TPG, sync generator, and FIFO enables.

Control flow: no executable flow. Host register access code uses these indices for MMIO.

State and persistence: none in software; constants describe hardware register layout.

Dependencies and integration: included by `pixelgen_private.h` and any pixelgen configuration code.

Risks and test signals: comments include generated/HSS placeholders and typos, so the header should be treated as hardware ABI. Tests should compare register indices against hardware documentation or emulator traces and validate generated test-pattern output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/hrt/PixelGen_SysBlock_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/hrt/ibuf_cntrl_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/hrt/ibuf_cntrl_defs.h

Purpose: defines register indices, command/ack token fields, status fields, and command constants for the input-buffer controller.

Important APIs/types/functions: macros describe register alignment, per-process register counts, timeout bits, stream2mmio token aliasing, ack token layout, shared registers, per-process config/status registers, and commands such as initialize, store online frame, store offline frame, and false ack.

Control flow: no runtime flow; constants drive IBUF MMIO programming and state interpretation.

State and persistence: no software state. Hardware state is represented by registers named here.

Dependencies and integration: includes Stream2MMIO and DMA v2 definitions because IBUF command/ack formats bridge those blocks.

Risks and test signals: off-by-one register definitions can corrupt DMA/IBUF setup. Tests should validate online/offline store command encoding, ack token extraction, and consistency with `ibuf_ctrl_local.h` state field order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/hrt/ibuf_cntrl_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/hrt/mipi_backend_common_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/hrt/mipi_backend_common_defs.h

Purpose: defines common MIPI/CSS receiver data-format IDs, format type mappings, repeat patterns, packet bit fields, compression fields, and custom decoding bit layout used by the MIPI backend.

Important APIs/types/functions: macros map MIPI data IDs for YUV/RGB/RAW/user-defined/short packets, CSS receiver format type IDs, repeat-pattern lengths, compression schemes, RAW16/RAW18 fields, packet SOP/channel/format/payload fields, and custom decoder state/pixel extractor/valid-EOP fields. It also defines `_HRT_MIPI_BACKEND_FMT_TYPE_CUSTOM`.

Control flow: no direct logic. These macros are consumed by backend LUT/configuration code and generated register packing.

State and persistence: no software state; constants describe packet and register bit layout.

Dependencies and integration: shared by `mipi_backend_defs.h` and legacy/common receiver code. Comments note the definitions must stay aligned with hardware design files.

Risks and test signals: many constants are hardware ABI and comments show historical design-time variants. Tests should verify data-type mapping for all supported sensor formats, compression configuration, packet header extraction, and custom decoder setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/hrt/mipi_backend_common_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/hrt/mipi_backend_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/hrt/mipi_backend_defs.h

Purpose: defines the MIPI backend register map, register widths, streaming bus field macros, LUT field macros, and custom decoder bit layout for CSS 2401.

Important APIs/types/functions: macros enumerate enable/status/compression/raw/IRQ/custom/LUT/stall register indices, register widths, SP/LP LUT entry counts, channel/format widths, streaming pixel/value/SOP/EOP bit positions parameterized by SID width, PPC, and pixel width, and LUT packet-disregard/SID/channel/format bit fields.

Control flow: no executable flow. Host code uses these indices and bit positions for MIPI backend programming and state capture.

State and persistence: none in software; register writes by consumers persist in hardware.

Dependencies and integration: includes `mipi_backend_common_defs.h` and is consumed by CSI RX private backend helpers and stream2mmio definitions.

Risks and test signals: several macros lack parentheses around additive expressions, which can surprise composed expressions. Custom decoder comments show changed bit positions versus older definitions. Tests should validate packed LUT values, streaming bus widths for each backend SID width, and raw/custom mode register programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/hrt/mipi_backend_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/hrt/rx_csi_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/hrt/rx_csi_defs.h

Purpose: defines the CSI RX frontend register map, widths, lane-enable encodings, error-handling bits, interrupt bits, lane status bits, and packet/header bit positions.

Important APIs/types/functions: macros define register indices for enable, enabled lanes, error handling, status, lane HS/LP status, clock/data lane delay counters, register count calculation, lane-count encodings, error handling bits, IRQ bit numbers, and packet/header fields.

Control flow: no runtime flow. CSI RX host accessors use these constants to read and program frontend control/status registers.

State and persistence: constants only.

Dependencies and integration: included by `csi_rx_private.h` and tied to CSI frontend hardware.

Risks and test signals: IRQ definitions replace older Arasan frontend definitions, so mixed hardware paths can misinterpret status. Tests should verify lane-enable programming, delay counter access for each lane, and IRQ/status decoding during real or simulated CSI error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/hrt/rx_csi_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/hrt/stream2mmio_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/hrt/stream2mmio_defs.h

Purpose: defines Stream2MMIO register indices and command/ack/packer token layouts.

Important APIs/types/functions: macros cover register alignment, per-SID command/ack/pixel-width/address/stride/count/block registers, SID register spacing, maximum SID count, command token field positions and values, pack acknowledgement item/EOP/EOF/valid bits, ACK token layout, and packer commands for words/long packets/short packets.

Control flow: no direct flow. Stream2MMIO host helpers use these constants for MMIO access and command interpretation.

State and persistence: no software state; constants describe hardware register/token ABI.

Dependencies and integration: includes `mipi_backend_defs.h` because Stream2MMIO consumes MIPI backend stream output.

Risks and test signals: header guard name contains `MMMIO`, but it is self-consistent. Tests should validate command token generation, acknowledgement parsing, and register bank stride for multiple SIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/hrt/stream2mmio_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/ibuf_ctrl_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/ibuf_ctrl_global.h

Purpose: defines public IBUF controller configuration structures and supplemental FSM/status constants.

Important APIs/types/functions: constants name main-controller FSM masks/states and DMA sync states not present in generated defs. `isp2401_ib_buffer_t` describes an input-buffer address/stride/line count. `ibuf_ctrl_cfg_t` describes online mode, DMA channel/command/reconfiguration packing, input buffer, destination buffer, store counts, and Stream2MMIO sync/store commands. `N_IBUF_CTRL_PROCS` declares per-controller process limits.

Control flow: no direct logic. Configuration code fills `ibuf_ctrl_cfg_t` and writes registers defined in `ibuf_cntrl_defs.h`.

State and persistence: config structures are caller-owned; applied values persist in hardware registers.

Dependencies and integration: includes generated IBUF controller defs and bridges DMA, Stream2MMIO, and IBUF controller configuration.

Risks and test signals: command fields must use exact DMA and Stream2MMIO token values. Tests should cover online/offline configs, buffer end-address calculations, element packing shifts, and FSM status interpretation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/ibuf_ctrl_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/isys_dma_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/isys_dma_global.h

Purpose: defines public ISYS 2401 DMA connection, extension, port, and device configuration types.

Important APIs/types/functions: macros name IBUF-to-DDR/VMEM connections and zero/sign extension values. `isys2401_dma_port_cfg_t` stores stride, elements, cropping, and width. `isys2401_dma_connection`, `isys2401_dma_extension`, and `isys2401_dma_cfg_t` describe channel, connection, extension, and transfer height. `N_ISYS2401_DMA_CHANNEL_PROCS` declares channel limits per DMA ID.

Control flow: no direct flow. DMA setup code consumes these types before writing registers.

State and persistence: caller-owned config only; hardware persistence occurs after register writes in private/public DMA helpers.

Dependencies and integration: depends on CSS type support and generated system DMA channel/ID types.

Risks and test signals: comments note duplicated definitions from CSS DMA until a device library exists, so divergence is possible. Tests should compare with DMA v2 expectations and validate port configuration for DDR and VMEM connections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/isys_dma_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/isys_irq_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/isys_irq_global.h

Purpose: defines ISYS IRQ controller register indices and broad mask/clear/enable values.

Important APIs/types/functions: register indices are edge, mask, status, clear, enable, and level/no-pulse. Values `ISYS_IRQ_MASK_REG_VALUE`, `ISYS_IRQ_CLEAR_REG_VALUE`, and `ISYS_IRQ_ENABLE_REG_VALUE` are all `0xFFFF`.

Control flow: no direct flow. `isys_irqc_status_enable()` and private helpers use these constants for MMIO.

State and persistence: constants only; applied values persist in IRQ controller registers.

Dependencies and integration: included by ISYS IRQ public/private code.

Risks and test signals: using `0xFFFF` assumes all active IRQ bits fit and should be enabled/cleared. Tests should validate hardware bit width, masked/unmasked behavior, and status clear semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/isys_irq_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/isys_stream2mmio_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/isys_stream2mmio_global.h

Purpose: defines the public Stream2MMIO configuration structure and declares per-controller SID limits.

Important APIs/types/functions: `stream2mmio_cfg_t` stores `bits_per_pixel` and `enable_blocking`. `N_STREAM2MMIO_SID_PROCS` provides active SID count per controller.

Control flow: no direct flow. Configuration code uses `stream2mmio_cfg_t`; state/dump helpers use SID counts.

State and persistence: config is caller-owned. Hardware state persists only after register writes.

Dependencies and integration: depends on CSS type support and generated Stream2MMIO ID types. It bridges MIPI backend output into MMIO storage paths.

Risks and test signals: blocking behavior can stall input if no command is queued. Tests should validate bits-per-pixel programming, blocking enable, and controller-specific SID limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/isys_stream2mmio_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/pixelgen_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/pixelgen_global.h

Purpose: defines public configuration types for the CSS 2401 pixel generator, including sync generator, test-pattern generator, and PRBS modes.

Important APIs/types/functions: `isp2401_sync_generator_cfg_t` describes blanking, pixels per clock, frame count, pixels per line, and lines per frame. `pixelgen_tpg_mode_t` enumerates ramp, checkerboard, and mono modes. `pixelgen_tpg_cfg_t` contains color, mask, delta, and sync-generator settings. `pixelgen_prbs_cfg_t` contains PRBS seeds and sync-generator settings.

Control flow: no logic in the header. Pixelgen setup code converts these configs into register writes.

State and persistence: caller-owned config structures; applied hardware configuration persists until reset/reprogramming.

Dependencies and integration: depends on CSS type support and duplicates parts of broader input-system config types.

Risks and test signals: duplication from other headers can drift. Tests should verify PRBS and TPG output dimensions, color/mask/delta behavior, and sync generator frame timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/pixelgen_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_receiver_2400_common_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_receiver_2400_common_defs.h

Purpose: provides legacy/common CSS receiver 2400 MIPI data-format, format-type, repeat-pattern, compression, packet, and custom-decoding definitions.

Important APIs/types/functions: macros define short packet field widths, MIPI data IDs for YUV/RGB/RAW/user-defined/embedded and frame/line events, format type IDs, repeat patterns, compression modes, RAW16/RAW18 configuration fields, packet header/payload bit positions, and custom decoder fields.

Control flow: no executable flow. Receiver and backend code use these constants for packet decoding and register packing.

State and persistence: constants only; hardware state is controlled elsewhere.

Dependencies and integration: this header uses the same guard name as `mipi_backend_common_defs.h` and contains nearly overlapping definitions, which can affect include ordering. It represents the CSS receiver 2400 side of MIPI packet interpretation.

Risks and test signals: duplicate guard/definition overlap is a significant integration risk if both headers are included in one translation unit. Some format comments appear inconsistent with macro values. Tests should verify include-order builds, sensor format mapping, packet decode fields, and custom decoder register packing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_receiver_2400_common_defs.h -->
