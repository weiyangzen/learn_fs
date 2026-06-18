# Research: subset-b-005420

Grouped research for the requested staging media driver sources. Each section title preserves the source path and is wrapped with the exact file markers required by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7.c

Purpose: this is the PCI root driver for Intel IPU7/IPU7.5/IPU8 staging media hardware. It binds supported PCI IDs, maps BARs, loads and validates CPD firmware, configures buttress power/control data, instantiates ISYS and PSYS auxiliary bus devices, and prepares firmware code memory mappings for secure and non-secure boot modes. Most of the file is hardware variant data: static `ipu_isys_internal_pdata` and `ipu_psys_internal_pdata` tables for IPU7, IPU7P5, and IPU8 describe MMU channels, ZLX/UAO stream mappings, CDC FIFO thresholds, and subsystem offsets consumed by lower IPU7 MMU, ISYS, and PSYS drivers.

Important APIs and functions: `ipu_internal_pdata_init()` fills common CSI2 offsets, stream counts, and PSYS SPC offsets; it is exported through the header for sibling code. `ipu7_isys_init()` and `ipu7_psys_init()` allocate per-subsystem platform data, call `ipu7_bus_initialize_device()`, initialize the subsystem MMU with `ipu7_mmu_init()`, set `subsys`, and add the auxiliary device. `ipu7_dump_fw_error_log()` copies firmware error-log words from buttress firmware GP registers into a static per-subsystem buffer and is exported in the `INTEL_IPU7` namespace. Firmware execution memory is handled by `ipu7_map_fw_code_region()`, `ipu7_unmap_fw_code_region()`, `ipu7_init_fw_code_region_by_sys()`, and `ipu7_init_fw_code_region()`.

Control flow: `ipu7_pci_probe()` is the main lifecycle entry. It reads optional firmware node data, enables the PCI device, maps BAR0 and BAR4, selects firmware names and platform data by PCI device ID, sets a 39-bit coherent DMA mask, allocates one IRQ vector, initializes buttress state, requests CPD firmware, validates the CPD file, creates ISYS and PSYS auxiliary devices, requests the shared buttress IRQ, then maps/authenticates firmware differently depending on `secure_mode`. Non-secure mode allocates a 16 MiB vmalloc code region, copies ISYS/PSYS CPD binaries into it, initializes each subsystem MMU, maps the code region through host DMA and IPU DMA, syncs it, and tears down transient MMU hardware state. Secure mode maps the signed CPD image through PSYS, authenticates via buttress, and then cleans up MMU runtime state. On success, runtime PM is allowed and `ipu7_bus_ready_to_probe` is set.

State and persistence: persistent device state lives in `struct ipu7_device` allocated with devm memory and stored as PCI drvdata. The driver owns `cpd_fw`, `fw_code_region`, BAR mappings, `secure_mode`, `ipc_reinit`, `isys`, `psys`, and the device list. Per-subsystem firmware mappings persist in each `ipu7_bus_device` `fw_sgt` until remove or probe failure cleanup. Static hardware tables are mutable structs passed by pointer and normalized once by `ipu_internal_pdata_init()`, so future edits must avoid accidental shared mutation surprises.

Dependencies and integration points: this file depends on Linux PCI, firmware, DMA mapping, runtime PM, fwnode graph, interrupts, and media `ipu-bridge`. Internal integration is heavy: `ipu7-bus`, `ipu7-buttress`, `ipu7-cpd`, `ipu7-dma`, `ipu7-mmu`, and platform register headers define most hardware contracts. ISYS graph probing integrates with ACPI/software-node camera bridge support via `ipu_bridge_init()` when firmware nodes lack graph endpoints.

Risks: error unwinding crosses firmware, MMU, DMA, auxiliary-device, and runtime-PM ownership boundaries; leaks or double puts are plausible if new failure paths are added. `ipu7_map_fw_code_region()` converts vmalloc-backed pages into an SG table and maps them twice, so page walking, DMA attributes, and unmap symmetry are critical. The IPU8 PCI ID is defined in the header but not present in `ipu7_pci_tbl`, while `probe()` has an IPU8 switch case; that is a notable integration mismatch to verify against build configuration and intended hardware enablement. Secure-mode probe error paths after `pm_runtime_get_sync()` can jump to common cleanup without always following the local cleanup sequence that successful secure-mode setup uses, so runtime PM balance deserves targeted review.

Test signals: build with `CONFIG_VIDEO_INTEL_IPU7` staging dependencies and check namespace exports. Probe tests need PCI ID matching, BAR mapping, firmware request/validation failure handling, graph-present and bridge-created camera topology paths, secure and non-secure firmware setup, runtime suspend/resume, FLR reset prepare/done, and remove after partial probe. Useful instrumentation includes DMA mapping failures, CPD binary missing cases for `isys`/`psys`, and verifying `fw_sgt.nents` drives exactly one unmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7.h

Purpose: this header is the central public contract for the Intel IPU7 PCI driver and its internal ISYS/PSYS auxiliary devices. It defines device names, firmware filenames, PCI IDs, hardware-version helpers, DMA/MMU sizing constants, firmware code region layout, and platform-data structures that are populated in `ipu7.c` and consumed by bus, MMU, ISYS, PSYS, buttress, and firmware-loading code.

Important APIs and types: `enum ipu_version` encodes IPU7, IPU7P5, and IPU8 hardware revisions, with inline helpers `is_ipu7()`, `is_ipu7p5()`, and `is_ipu8()`. `struct ipu7_device` is the top-level PCI driver state containing PCI device, auxiliary ISYS/PSYS devices, buttress state, CPD firmware, BAR mappings, hardware revision, firmware boot mode flags, and bus readiness. `struct ipu7_mmu_hw`, `struct ipu7_hw_variants`, `struct ipu_isys_internal_pdata`, and `struct ipu_psys_internal_pdata` express the per-generation MMU, ZLX, UAO, CDC FIFO, DMEM, and SPC configuration tables used at probe time. `struct ipu7_isys_pdata` and `struct ipu7_psys_pdata` are passed to child auxiliary devices.

Control flow and integration: this header does not implement control flow, but it constrains the flow in `ipu7.c`: the probe selects firmware filename constants, fills `struct ipu7_device`, chooses one `struct ipu7_hw_variants` tree, and passes ISYS/PSYS platform data to `ipu7_bus_initialize_device()` and `ipu7_mmu_init()`. Exported declarations include `request_cpd_fw()`, `ipu_internal_pdata_init()`, and `ipu7_dump_fw_error_log()`.

State and persistence behavior: constants such as `IPU_FW_CODE_REGION_START`, `IPU_FW_CODE_REGION_SIZE`, and `IPU_FW_CODE_REGION_END` document the non-secure firmware virtual address window. MMU sizing limits (`IPU_MMU_MAX_NUM`, stream limits, ZLX/UAO maxima, MMUV2 trash ranges) bound arrays embedded in platform data, so changing them affects static table size and hardware programming loops elsewhere. `struct ipu7_device` state persists for the PCI device lifetime, while pdata structures are shared static tables referenced by subsystem devices.

Dependencies: includes Linux list, PCI, and types headers plus `ipu7-buttress.h`. Consumers also depend on register headers for field values placed into these structures. The constants interact with DMA API restrictions and firmware CPD image layout.

Risks: array-bound changes are high risk because the large static tables in `ipu7.c` assume the maxima here. The declared `IPU8_PCI_ID` and `IPU8_FIRMWARE_NAME` need consistency with the actual PCI match table. Because this header exposes mutable internal platform data structs rather than const-only opaque descriptors, consumers can accidentally mutate shared hardware variant data.

Test signals: compile-time coverage should catch most struct/member drift across IPU7 modules. Runtime validation should confirm selected hardware revision helpers, firmware filenames, MMU counts, stream counts, and DMA mask constants match real silicon and firmware expectations. Static analysis should focus on array initializers versus declared maxima.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/max96712/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/media/max96712/Kconfig

Purpose: this Kconfig entry exposes the staging V4L2 subdevice driver for Maxim MAX96712 Quad GMSL2 deserializers as `CONFIG_VIDEO_MAX96712`. It can be built in or as a module and documents that the module name is `max96712`.

Important symbols: `VIDEO_MAX96712` is a tristate option labeled "Maxim MAX96712 Quad GMSL2 Deserializer support". It directly depends on `I2C`, `OF_GPIO`, and `VIDEO_DEV`, and selects `V4L2_FWNODE`, `VIDEO_V4L2_SUBDEV_API`, and `MEDIA_CONTROLLER`.

Control flow and integration: Kconfig selection controls whether `max96712.o` is included by the local Makefile. The dependencies line up with `max96712.c`, which uses I2C regmap access, optional GPIO power control, fwnode endpoint parsing, V4L2 subdev state, controls, and media pads.

State and persistence behavior: no runtime state is defined here. The configuration state determines whether the driver can bind compatible OF nodes and whether V4L2 subdevice/media-controller support is available.

Risks: the driver parses OF graph endpoints and uses `devm_gpiod_get_optional()`, so `OF_GPIO` and fwnode selections are required. If the driver later supports ACPI or non-OF systems, these dependencies may need loosening. Selecting subdev API and media controller can pull additional framework code into builds, which is expected for this driver.

Test signals: `allyesconfig`, `allmodconfig`, and `COMPILE_TEST`-style builds should verify dependency closure. Runtime probe tests need a device tree node with an endpoint on port 4 and an optional `enable` GPIO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/max96712/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/max96712/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/media/max96712/Makefile

Purpose: this Makefile connects `CONFIG_VIDEO_MAX96712` to the single object file implementing the Maxim deserializer V4L2 subdevice driver.

Important build API: `obj-$(CONFIG_VIDEO_MAX96712) += max96712.o` means the object is built into the kernel or as a module according to the Kconfig tristate state. There are no composite objects, generated sources, or local compiler flags.

Control flow and integration: the parent staging media Makefile includes this directory when enabled. The module metadata in `max96712.c` provides the runtime module description, author, license, I2C driver registration, and OF match table.

State and persistence behavior: no runtime state is created here. Build state is entirely determined by the Kconfig symbol.

Risks: because the driver is a single object, future file splits require converting this to a composite object list. The object name must continue to match the documented module name in Kconfig.

Test signals: verify `CONFIG_VIDEO_MAX96712=m` produces `max96712.ko` and `CONFIG_VIDEO_MAX96712=y` links the object into the kernel image without missing media, I2C, GPIO, or regmap dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/max96712/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/max96712/max96712.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/max96712/max96712.c

Purpose: this file implements a staging V4L2 I2C subdevice driver for Maxim MAX96712/MAX96724 GMSL2 deserializers. In its current form it is primarily a CSI-2 pattern generator source, not a full serializer-link capture driver: it configures MIPI D-PHY or C-PHY output, registers one source media pad, exposes pixel-rate and test-pattern controls, and streams an internal 1920x1080 RGB test pattern.

Important APIs and functions: `struct max96712_priv` holds I2C/regmap state, optional enable GPIO, chip-specific info, parsed MIPI endpoint config, V4L2 subdev/control state, media pad, and selected pattern. Low-level register helpers wrap `regmap_write()`, `regmap_update_bits()`, and `regmap_bulk_write()`. `max96712_mipi_configure()` disables output, selects 2x4 mode, configures fixed PHY0/PHY1 lane mapping, lane polarity, DPLL frequency, and PHY enables. `max96712_pattern_enable()` programs the video timing and pattern generator. `max96712_s_stream()` toggles pattern and MIPI output. `max96712_v4l2_register()` initializes the subdev, controls, pad, state lock, and async registration. `max96712_parse_dt()` parses a fwnode endpoint on port 4.

Control flow: `max96712_probe()` allocates state, gets match data, initializes 16-bit-register/8-bit-value regmap, acquires optional `enable` GPIO, powers the chip, sleeps if GPIO was used, issues reset, parses the DT endpoint, configures MIPI output, then registers the V4L2 subdevice. Streaming on enables pattern generation before enabling MIPI; streaming off disables MIPI before disabling the pattern. Remove unregisters the subdev and powers down the optional GPIO.

State and persistence: runtime state is held in devm-managed `priv`, with V4L2 control handler and media entity resources explicitly freed only on registration error; unregister handles the normal subdev lifetime. `pattern` persists as the last `V4L2_CID_TEST_PATTERN` value and is consumed on stream start. Parsed `priv->mipi` lane polarity and lane count are fixed after probe. No runtime PM or dynamic link state is maintained.

Dependencies and integration points: depends on I2C, regmap, GPIO descriptors, OF graph/fwnode parsing, V4L2 subdev APIs, media controller pads, and V4L2 controls. OF compatible data distinguishes MAX96712 at 1000 MHz DPLL with a debug-extra register from MAX96724 at 1200 MHz without that register.

Risks: endpoint parsing is hard-coded to port 4 and only supports exactly 4 D-PHY data lanes or 3 C-PHY trios; 1- or 2-lane configs and lane swapping are TODOs. `max96712_pattern_enable()` ignores most write failures because callers do not aggregate return values, so streaming can report success after partial hardware programming. Pixel-rate calculation is simplified and uses DPLL frequency divided by lane count, not full CSI-2 symbol semantics. Only one pad/source format is exposed, with `.set_fmt` mapped to `get_fmt`, so userspace cannot negotiate meaningful formats.

Test signals: verify probe with `maxim,max96712` and `maxim,max96724`, optional enable GPIO timing, valid/invalid endpoint bus types, lane counts, lane polarities, and async subdev registration. Stream tests should check checkerboard and gradient controls, MIPI enable/disable register ordering, 75 MHz debug PCLK behavior only on MAX96712, and media graph source-pad format reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/max96712/max96712.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/Kconfig

Purpose: this Kconfig entry exposes the Amlogic Meson video decoder staging driver as `CONFIG_VIDEO_MESON_VDEC`. The help text scopes it to video decoder hardware found in GXBB/GXL/GXM chips, while the implementation also contains platform data for later G12A/SM1 revisions.

Important symbols: `VIDEO_MESON_VDEC` is a tristate "Amlogic video decoder driver". It depends on `VIDEO_DEV`, `HAS_DMA`, and either `ARCH_MESON` or `COMPILE_TEST`. It selects `VIDEOBUF2_DMA_CONTIG`, `V4L2_MEM2MEM_DEV`, and `MESON_CANVAS`.

Control flow and integration: enabling this symbol builds the composite `meson-vdec` module/object from the local Makefile. The selected frameworks match the implementation: V4L2 mem2mem queues, contiguous DMA buffers for source/capture/VIFIFO/workspaces, and Meson canvas IDs for legacy hardware framebuffer addressing.

State and persistence behavior: no runtime state is defined in Kconfig. The selected dependencies determine availability of DMA-contiguous vb2 memory ops, m2m scheduling helpers, and canvas allocation APIs used throughout the driver.

Risks: the help text may understate supported revisions relative to the OF match table. Since the driver is staging and uses firmware plus hardware-specific register programming, `COMPILE_TEST` can validate build coverage but not runtime behavior. Missing firmware files remain runtime failures, not Kconfig constraints.

Test signals: build matrix coverage with `ARCH_MESON=y`, `COMPILE_TEST=y`, module and built-in modes. Runtime tests need OF nodes with DOS, ESPARSER, clocks, resets, AO sysctrl, canvas provider, and IRQ resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/Makefile

Purpose: this Makefile defines the composite object list for the Amlogic Meson VDEC driver and connects it to `CONFIG_VIDEO_MESON_VDEC`.

Important build API: `meson-vdec-objs` includes shared infrastructure (`esparser.o`, `vdec.o`, `vdec_helpers.o`, `vdec_platform.o`), hardware-block support (`vdec_1.o`, `vdec_hevc.o`), and codec implementations (`codec_mpeg12.o`, `codec_h264.o`, `codec_hevc_common.o`, `codec_vp9.o`). The final line `obj-$(CONFIG_VIDEO_MESON_VDEC) += meson-vdec.o` builds them as one module or built-in object.

Control flow and integration: composite object ordering ensures common infrastructure and codec ops are linked into one driver that registers a single platform driver/video device. Header-declared extern ops such as `vdec_1_ops`, `codec_mpeg12_ops`, `codec_h264_ops`, and `codec_vp9_ops` are resolved inside this module.

State and persistence behavior: no runtime state is maintained here. Build composition determines which codecs and hardware back ends are present for platform format tables.

Risks: adding or removing a codec requires updating both this object list and platform format tables. Since all codecs link into one module, a build break in one codec disables the entire VDEC driver.

Test signals: verify `meson-vdec.ko` contains all required codec and hardware symbols, and that modpost sees no unresolved references for codec ops, VDEC ops, platform tables, or exported helper functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_h264.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_h264.c

Purpose: this file implements the H.264 codec side of the Meson VDEC_1 pipeline. It provides `codec_h264_ops` for firmware loading, codec startup/shutdown, capture-buffer recycling, resolution-change resume, EOS signaling, and interrupt-driven frame completion.

Important APIs and functions: `struct codec_h264` tracks extended firmware, workspace, reference motion-vector memory, SEI dump memory, macroblock dimensions, and maximum references. `codec_h264_load_extended_firmware()` is called by `vdec_1_load_firmware()` after the base microcode and allocates/copies the 20 KiB H.264 extension. `codec_h264_start()` allocates the main workspace and SEI buffer, programs firmware scratch registers with workspace-relative addresses, enables VLD power bits, enables firmware error correction, and configures DC thresholds. `codec_h264_resume()` maps capture buffers to canvases, allocates reference MV memory based on parsed macroblock dimensions and max refs, and writes reference limits to scratch registers. `codec_h264_threaded_isr()` decodes firmware commands.

Control flow: the VDEC_1 hardware loader first calls `load_extended_firmware`, then `start`. Firmware emits mailbox IRQs; the hard ISR clears `ASSIST_MBOX1_CLR_REG` and wakes the threaded ISR. `CMD_SRC_CHANGE` triggers `codec_h264_src_change()`, which reads parsed SPS/crop/aspect data from scratch registers and calls `amvdec_src_change()` with `max_refs + 5` DPB size. Userspace then reallocates/requeues capture buffers and start-streaming calls `resume()`. `CMD_FRAMES_READY` reads one or more frame status entries, derives buffer index, interlaced field, and VIFIFO offset, then calls `amvdec_dst_buf_done_idx()`.

State and persistence: H.264 private state is stored in `sess->priv` and freed in `codec_h264_stop()`. The driver uses firmware scratch registers as a persistent ABI across IRQs: `AV_SCRATCH_0` carries commands/status, `AV_SCRATCH_1..` carry parsed metadata and frame status, `AV_SCRATCH_7/8` are recycle slots, and `AV_SCRATCH_J` flags SEI data. The EOS sequence is a static 4 KiB encoded picture used to provoke firmware drain.

Dependencies and integration points: depends on V4L2 mem2mem/vb2 DMA, `dos_regs.h`, `vdec_helpers`, and the VDEC_1 firmware loader. It integrates with generic session state for keyframe detection, source-change events, timestamp matching, buffer completion, and abort handling.

Risks: allocation failure in `codec_h264_start()` after workspace allocation but before SEI allocation returns without freeing the workspace until later stop paths, so error unwinding should be checked. Scratch-register ABI assumptions are undocumented outside constants and can break with firmware changes. Reference MV allocation scales with macroblock count and max refs; corrupted parsed values could drive large allocations before abort. The static EOS sequence is a workaround and should be regression-tested with drain/stop paths.

Test signals: decode H.264 streams with SPS changes, crop/aspect-ratio changes, interlaced `PIC_TOP_BOT`/`PIC_BOT_TOP`, multiple frames-ready per IRQ, decode-error flags, bad width/height firmware commands, fatal errors, buffer recycle pressure, and EOS via decoder command.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_h264.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_h264.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_h264.h

Purpose: this header exports the H.264 codec operations object to the Meson VDEC platform/format tables.

Important API: it includes `vdec.h` and declares `extern struct amvdec_codec_ops codec_h264_ops;`. The implementation fills this ops table with `start`, `stop`, `load_extended_firmware`, `isr`, `threaded_isr`, `can_recycle`, `recycle`, `eos_sequence`, and `resume`.

Control flow and integration: platform format descriptors reference `codec_h264_ops` when an OUTPUT pixel format is H.264. Generic `vdec.c` calls these callbacks during stream start, IRQ handling, source-change resume, recycle-thread processing, drain/EOS, and stop.

State and persistence behavior: the header does not define state, but the ops table creates the contract that H.264 private state will be attached to `amvdec_session.priv` by the codec implementation and released through the stop callback.

Dependencies: depends on `struct amvdec_codec_ops` from `vdec.h`; it must be linked with `codec_h264.o` in the same composite module.

Risks: because the exported object is mutable, accidental writes by other code would affect all sessions. Signature drift in `struct amvdec_codec_ops` requires updating both this declaration and the implementation initializer.

Test signals: compile/link tests should catch missing `codec_h264_ops`. Runtime tests should select the H.264 format and verify generic VDEC code reaches all implemented callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_h264.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_hevc_common.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_hevc_common.c

Purpose: this file contains shared helper code for HEVC-family hardware paths used by VP9 and likely HEVC codec implementations. It programs decode-head/FBC modes, allocates framebuffer-compression and MMU header buffers, builds hardware reference tables, and exports helpers for codec-specific setup.

Important APIs and functions: `vdec_hevc_parser_cmd` is a 37-entry parser command program loaded by codecs such as VP9. `codec_hevc_setup_decode_head()` configures decompression/read mode, compressed body/header sizes, and MMU/FBC controls. `codec_hevc_setup_buffers()` coordinates optional FBC buffer allocation, optional MMU header/map allocation, and revision-specific reference table programming through either `codec_hevc_setup_buffers_gxbb()` or `codec_hevc_setup_buffers_gxl()`. `codec_hevc_free_fbc_buffers()`, `codec_hevc_free_mmu_headers()`, and `codec_hevc_fill_mmu_map()` provide cleanup and per-frame MMU page-map setup.

Control flow: codec resume paths call `codec_hevc_setup_buffers()` after userspace has queued capture buffers. For GXBB, the helper writes `HEVCD_MPP_ANC2AXI_TBL_CMD_ADDR` entries and fills unused slots with the last buffer. For GXL and later, it writes packed physical addresses to `HEVCD_MPP_ANC2AXI_TBL_DATA`. For 10-bit/FBC/downsample use cases, it allocates hidden compressed buffers and/or MMU headers before programming the hardware tables. Per-frame code can then call `codec_hevc_fill_mmu_map()` to point the hardware MMU map at the selected output or hidden FBC buffer.

State and persistence: state is held in `struct codec_hevc_common`, which stores arrays of hidden FBC buffers, MMU header buffers, and one MMU map. These allocations persist for the session/resolution until freed by codec stop/error paths. The helper writes persistent hardware reference-table and decompression registers that remain active for subsequent frame decoding.

Dependencies and integration points: depends on V4L2 mem2mem destination buffer iteration, vb2 contiguous DMA addresses, AM21C size helpers from `vdec_helpers`, platform revision values, and HEVC register definitions. It is exported with GPL symbols for use by sibling codec files in the same driver.

Risks: allocation loops index arrays by VB2 buffer index and assume indices are below `MAX_REF_PIC_NUM`; queue limits should maintain that invariant. Error handling must free both FBC and MMU allocations in all partial-failure cases. `codec_hevc_use_fbc()` currently returns true for all 10-bit content and has a TODO for 8-bit compressed buffers, so output-format behavior is intentionally incomplete. Physical-address shifting and table formats differ by revision, making revision tests important.

Test signals: exercise GXBB versus GXL/G12A/SM1 buffer-table programming, 8-bit NV12, 10-bit downsample-to-NV12, MMU-enabled G12A/SM1 paths, allocation failures midway through buffer arrays, source-change reallocation, and cleanup idempotence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_hevc_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_hevc_common.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_hevc_common.h

Purpose: this header defines the shared HEVC-family buffer-management and parser-command contract used by Meson VDEC codec implementations.

Important APIs and types: it defines parser skip configuration constants, `VDEC_HEVC_PARSER_CMD_LEN`, and the external `vdec_hevc_parser_cmd` array. `MAX_REF_PIC_NUM` is 24. `struct codec_hevc_common` stores per-reference FBC buffer virtual/physical addresses, per-reference MMU compressed-header buffers, and one MMU map buffer. Inline policy helpers decide whether a decode uses FBC, downsampling, or MMU based on capture pixel format, bit depth, and platform revision. Function declarations expose decode-head setup, FBC/MMU cleanup, buffer setup, and MMU map fill.

Control flow and integration: VP9 and HEVC implementations embed `struct codec_hevc_common` in their private session state, call setup during resume/source-change, call fill-map for frames on MMU-capable revisions, and call cleanup during stop. The inline helpers centralize format/revision policy so codec files do not duplicate those decisions.

State and persistence behavior: the header-defined struct owns DMA allocations that live across frames and must be released by the codec. `MAX_REF_PIC_NUM` bounds these arrays and must align with capture queue limits and hardware reference table capacity.

Dependencies: includes `vdec.h` for session/platform types and revision constants. The implementation also depends on HEVC register definitions and vb2 DMA helpers.

Risks: the simple inline policies currently treat all 10-bit decode as FBC/downsample and all G12A-or-newer FBC as MMU-backed, which may be too broad for future formats. Changing `MAX_REF_PIC_NUM` affects memory footprint and table programming loops.

Test signals: compile all codec users after any signature or policy change. Runtime tests should verify 8-bit versus 10-bit paths, revision gates, capture buffer counts near 24, and cleanup after setup failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_hevc_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_mpeg12.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_mpeg12.c

Purpose: this file implements MPEG-1/MPEG-2 codec operations for the Meson VDEC_1 firmware path. It programs canvases and firmware scratch registers, owns a small workspace, recycles capture buffers to firmware, handles display-aspect-ratio updates, signals EOS, and completes decoded frames from mailbox IRQs.

Important APIs and functions: `struct codec_mpeg12` stores the 128 KiB DMA workspace. `codec_mpeg12_start()` allocates that workspace, maps capture buffers to `AV_SCRATCH_0..7` canvases through `amvdec_set_canvases()`, writes workspace and command registers, clears error/wait state, and marks `keyframe_found`. `codec_mpeg12_can_recycle()` and `codec_mpeg12_recycle()` use `MREG_BUFFERIN` to return buffers to firmware. `codec_mpeg12_threaded_isr()` handles fatal error detection, frame-ready status, interlace field selection, DAR update, VIFIFO offset reading, and `amvdec_dst_buf_done_idx()` completion. `codec_mpeg12_eos_sequence()` returns a static MPEG sequence end code padded to 1 KiB.

Control flow: generic VDEC startup loads firmware through `vdec_1.c`, then calls `codec_mpeg12_start()`. The recycle thread returns freed capture buffer indices when `MREG_BUFFERIN` is clear. The hard ISR only wakes the thread. The threaded ISR clears mailbox status, checks `MREG_FATAL_ERROR`, reads `MREG_BUFFEROUT`, ignores an unclear all-ones marker, derives progressive/interlaced field from `MREG_PIC_INFO`, maps the low nibble buffer ID to a zero-based index, reads `MREG_FRAME_OFFSET`, and completes the matching capture buffer.

State and persistence: session-private workspace persists until `codec_mpeg12_stop()`. Firmware state persists in DOS scratch registers: sequence info, picture info, buffer-in/out mailboxes, command dimensions, workspace pointer, error counters, and frame offsets. The codec does not track a DPB list in software; firmware and the generic recycle path coordinate buffer ownership.

Dependencies and integration points: depends on `dos_regs.h`, V4L2 mem2mem/vb2 DMA, `vdec_helpers` for canvas setup, PAR setting, buffer completion, and abort. It is selected by platform format tables through `codec_mpeg12_ops`.

Risks: the ISR contains an "unclear what this means" condition for a special `MREG_BUFFEROUT` bit pattern, so behavior around that firmware status is not fully understood. `amvdec_set_canvases()` only maps the currently queued capture buffers, making queue setup/minimum buffer enforcement important. Fatal firmware errors abort both queues.

Test signals: MPEG-1 and MPEG-2 streams with progressive and interlaced pictures, DAR codes 4:3/16:9/2.21:1/default, EOS stop command, recycle pressure, fatal error injection, and capture queue sizes up to the eight scratch-register canvas slots used here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_mpeg12.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_mpeg12.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_mpeg12.h

Purpose: this header exports the MPEG-1/MPEG-2 codec operations object for the Meson VDEC driver.

Important API: it includes `vdec.h` and declares `extern struct amvdec_codec_ops codec_mpeg12_ops;`. The implementation supplies start/stop, ISR/threaded ISR, recycle, and EOS callbacks.

Control flow and integration: platform format tables reference this object for MPEG-1/2 OUTPUT formats. Generic VDEC code invokes the callbacks during VDEC_1 firmware startup, IRQ dispatch, recycle-thread execution, decoder-command stop, and stream shutdown.

State and persistence behavior: no state is declared here. The implementation attaches `struct codec_mpeg12` to `amvdec_session.priv` and releases its DMA workspace through the stop callback.

Dependencies: depends on the `amvdec_codec_ops` definition from `vdec.h` and link inclusion of `codec_mpeg12.o`.

Risks: ops signature drift must be reflected in both declaration and implementation. A mutable global ops object can be corrupted by unintended writes, though normal code treats it as a static callback table.

Test signals: link-time symbol resolution and runtime selection of MPEG formats should demonstrate that `codec_mpeg12_ops` is reachable and all expected callbacks are non-NULL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_mpeg12.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_vp9.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_vp9.c

Purpose: this file implements VP9 codec operations on the Meson HEVC-family decode block. It manages the VP9 workspace layout, HEVC parser programming, loop-filter/probability adaptation, reference-frame tracking, hidden FBC/MMU buffers, SAO/MPRED/MCRCC setup, source-change handling, output draining, and threaded IRQ progression.

Important APIs and types: `struct codec_vp9` is the main per-session state. It contains a mutex, embedded `codec_hevc_common`, workspace DMA memory, parsed RPM parameters, bit-depth/resolution, a list of live VP9 reference frames, reference maps, frame refs, LCU count, loop-filter state, segmentation state, and current/previous frame pointers. `struct vp9_frame` links a VB2 capture buffer to VP9 frame metadata and software lifetime. Key functions include `codec_vp9_start()`, `codec_vp9_resume()`, `codec_vp9_process_frame()`, `codec_vp9_threaded_isr()`, `codec_vp9_flush_output()`, and the probability adaptation helpers `adapt_coef_probs()` and `vp9_tree_merge_probs()`.

Control flow: startup allocates the large workspace, writes all workspace subregion addresses into HEVC/VP9 scratch registers, enables parser/shift/CABAC controls, loads the shared HEVC parser command table, enables mailbox interrupts, initializes loop-filter registers, and initializes reference maps to -1. When firmware parses a frame header it raises `VP9_HEAD_PARSER_DONE`; the threaded ISR validates status, optionally adapts probabilities from count memory, updates reference maps for the previous frame, fetches/reorders RPM data, detects resolution or bit-depth changes, and either raises `amvdec_src_change()` or processes the next frame. Frame processing obtains a new capture buffer, syncs VP9 refs, updates next refs, fills MMU maps if needed, configures MC/MPRED for inter frames, writes picture size, MCRCC, SAO, decode-head/loop-filter state, and finally writes `VP9_10B_DECODE_SLICE` to start firmware decode. Displayable old frames are completed by `codec_vp9_show_frame()`.

State and persistence: software maintains a DPB-like `ref_frames_list`, `ref_frame_map`, `next_ref_frame_map`, and `frame_refs`. Hidden FBC/MMU allocations from `codec_hevc_common` persist after resume until stop. The workspace contains parser/RPM/prob/count/LMEM/MV/DBLK/SAO subregions at fixed offsets. `frames_num` feeds ESPARSER backpressure through `num_pending_bufs`. Drain flushes outstanding frames, completing show frames and requeueing non-show frames.

Dependencies and integration points: depends on `dos_regs.h`, `hevc_regs.h`, `codec_hevc_common`, `vdec_helpers`, V4L2 mem2mem, and vb2 DMA. It uses the generic source-change mechanism and capture-buffer completion helpers. It relies on the HEVC hardware block and the parser command table shared with HEVC-style codecs.

Risks: this is stateful and high risk. Reference saving for resized frames is explicitly incomplete (`FIXME` warning), so streams resizing with active refs may lose correctness. `codec_vp9_stop()` frees the workspace and FBC buffers but does not call `codec_hevc_free_mmu_headers()`, which should be reviewed for MMU-enabled 10-bit paths. Several paths assume VB2 buffer indices fit `MAX_REF_PIC_NUM`. Probability adaptation casts unaligned workspace byte pointers to `unsigned int *`; architecture alignment and endianness assumptions matter. Source-change and drain paths manipulate queued buffers and frame lists under the VP9 lock, so race testing with streamoff/EOS is important.

Test signals: cover VP9 key frames, inter frames, show-existing-frame streams, non-show refs, resolution changes, 8-bit and 10-bit bitstreams, G12A/SM1 MMU paths, downsample/FBC paths, reference scaling, probability adaptation status `0xfd`, capture-buffer starvation, drain/streamoff, and corrupted firmware statuses. Memory leak tests should focus on workspace, FBC buffers, MMU headers/maps, and `struct vp9_frame` list nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_vp9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_vp9.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_vp9.h

Purpose: this header exports the VP9 codec operations object used by the Meson VDEC platform format tables.

Important API: it includes `vdec.h` and declares `extern struct amvdec_codec_ops codec_vp9_ops;`. The implementation provides callbacks for start, stop, ISR, threaded ISR, pending-buffer accounting, drain, and resume.

Control flow and integration: generic VDEC session code invokes `codec_vp9_ops` to start the HEVC-family hardware path, account for VP9-held reference frames during ESPARSER queuing, flush output on drain, resume after source changes, and dispatch decode IRQs.

State and persistence behavior: no state is defined here, but the ops table implies that VP9 private state is stored in `amvdec_session.priv` and remains active across frames and source-change resumes until stop.

Dependencies: depends on `struct amvdec_codec_ops` from `vdec.h` and on linking `codec_vp9.o` into `meson-vdec`.

Risks: a missing or mismatched ops declaration breaks platform format linkage. Since VP9 uses optional callbacks that generic code treats specially (`num_pending_bufs`, `drain`, `resume`), future ops changes must preserve these entries.

Test signals: compile/link tests for `codec_vp9_ops`; runtime VP9 format selection should exercise pending-buffer accounting, drain, resume, and IRQ callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_vp9.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/dos_regs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/dos_regs.h

Purpose: this header defines register offsets and bit fields for the Meson DOS/VDEC_1 block, firmware scratch interface, VIFIFO stream buffer, MPEG/H.264 decoder control, reset, clock, and memory power-down registers.

Important APIs and constants: it defines mailbox registers (`ASSIST_MBOX1_CLR_REG`, `ASSIST_MBOX1_MASK`), firmware control registers (`MPSR`, `CPSR`, `MCPU_INTR_MSK`), IMEM DMA registers, decoder/post-scaler controls, canvas address register base (`ANC0_CANVAS_ADDR`), scratch registers `AV_SCRATCH_0` through `AV_SCRATCH_L`, MPEG and VLD controls, VIFIFO start/current/end/control/write/read/level registers, and top-level DOS reset/clock/memory registers. Bit helpers include VIFIFO fill/empty control bits and manual buffer control.

Control flow and integration: `vdec_1.c` uses these offsets to power/reset VDEC_1, load firmware through IMEM DMA, configure VIFIFO, and enable mailbox IRQs. MPEG-1/2 and H.264 codec files use scratch registers as their firmware ABI. `vdec_helpers.c` wraps read/write access to the DOS base, but this header defines the address contract.

State and persistence behavior: register values represent live hardware state. Scratch registers persist as firmware mailboxes across IRQs. VIFIFO pointer registers track the DMA bitstream ring. Reset and memory power registers control hardware block lifetime around streaming.

Dependencies: depends on Linux `BIT()`/GENMASK availability through including source files. It is paired with `amvdec_read_dos()` and `amvdec_write_dos()` helpers that add these offsets to `core->dos_base`.

Risks: wrong offsets or bit definitions can hang firmware, corrupt DMA, or prevent IRQ delivery. Scratch register reuse is codec-specific and not type-safe. Some registers are shared by multiple codec paths, so changes need cross-codec review.

Test signals: firmware load success, mailbox IRQ delivery, VIFIFO fill-level accounting, stream start/stop reset sequencing, MPEG/H.264 scratch ABI behavior, and register tracing against vendor documentation or known-good downstream trees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/dos_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/esparser.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/esparser.c

Purpose: this file implements the Elementary Stream Parser support for Meson VDEC. ESPARSER consumes queued OUTPUT bitstream buffers, optionally rewrites VP9 frame headers, pads and appends start-code search patterns, DMA-fetches data into the hardware VIFIFO, tracks source timestamps by VIFIFO offset, and provides an EOS write path.

Important APIs and functions: `esparser_init()` requests the parser IRQ and reset control. `esparser_power_up()` resets and configures parser registers, search pattern/mask, VIFIFO start/end pointers, optional decoder-specific parser config, and parser IRQ enable. `esparser_queue_all_src()` is the workqueue handler scheduled by V4L2 m2m paths. `esparser_queue()` handles one source buffer: checks VIFIFO free space, applies VP9-specific backpressure, removes the source buffer from m2m, records timestamp/offset with `amvdec_add_ts()`, rewrites VP9 superframe headers through `vp9_update_header()`, pads with `esparser_pad_start_code()`, writes data through `esparser_write_data()`, and completes the source buffer. `esparser_queue_eos()` writes a codec-provided EOS sequence through a temporary coherent buffer.

Control flow: parser IRQ `esparser_isr()` acknowledges `PARSER_INT_STATUS`, clears PFIFO pointers on start-code found, sets a global `search_done`, and wakes a waitqueue. `esparser_write_data()` programs parser fetch address and command, then waits up to 200 ms for that IRQ. `esparser_queue_all_src()` loops over source buffers until stop is requested or one buffer cannot be queued because VIFIFO/capture capacity is insufficient. VP9 additionally subtracts three buffers from available destination capacity to avoid reference starvation.

State and persistence: global `search_done` and waitqueue serialize parser fetch completion. Per-session state includes `vififo_paddr`, `vififo_size`, `last_offset`, `wrap_count`, and atomic `esparser_queued_bufs`. Timestamp records persist in `sess->timestamps` until a decoded capture buffer matches by FIFO offset or FIFO order.

Dependencies and integration points: depends on parser register offsets local to this file, `dos_regs.h`, `vdec_helpers`, V4L2 mem2mem iteration, vb2 DMA addresses and virtual mappings, and codec ops for `num_pending_bufs` and `conf_esparser`.

Risks: `search_done` is global, so concurrent sessions would race, although `vdec.c` enforces a single active session. VP9 header rewriting modifies source buffers in place and requires spare plane capacity. Padding/start-code append can fail silently by returning only partial pad size, so parser behavior depends on source buffer size margins. Timeout/error paths mark source buffers error and remove timestamps, but parser fetch state must be cleared correctly to avoid later stalls.

Test signals: parser IRQ timing, 200 ms timeout behavior, VIFIFO wrap offset accounting, timestamp matching, VP9 superframes with multiple frame sizes, too-small source buffers, EOS writes, stop while source buffers are queued, and VP9 capture-buffer backpressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/esparser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/esparser.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/esparser.h

Purpose: this header declares the Meson ESPARSER interface used by the core VDEC driver and codec/hardware setup code.

Important APIs: `esparser_init()` binds IRQ/reset resources during platform probe. `esparser_power_up()` configures parser hardware for a session after VDEC power-on. `esparser_queue_eos()` writes a codec-provided EOS byte sequence into the parser. `esparser_queue_all_src()` is the work handler that drains queued OUTPUT buffers into ESPARSER when capacity allows. `ESPARSER_MIN_PACKET_SIZE` defines the 4 KiB minimum packet padding threshold required to trigger VDEC IRQs reliably.

Control flow and integration: `vdec_probe()` calls `esparser_init()`, `vdec_poweron()` calls `esparser_power_up()`, V4L2 m2m scheduling queues `esparser_queue_all_src()` as work, and decoder stop commands use `esparser_queue_eos()` when the codec provides an EOS sequence rather than a custom drain callback.

State and persistence behavior: the header does not declare state. Implementation state is split between hardware parser registers, global parser wait state, and `amvdec_session` VIFIFO/timestamp fields.

Dependencies: includes `linux/platform_device.h` and `vdec.h` for core/session types. Implementation relies on reset, IRQ, parser MMIO, and vb2 DMA APIs.

Risks: callers must ensure the session has allocated and configured VIFIFO memory before calling `esparser_power_up()` or queueing source buffers. EOS data must remain valid for the requested length.

Test signals: platform probe resource acquisition, parser power-up during stream start, workqueue scheduling on source/capture buffer events, and EOS paths for codecs that expose `eos_sequence`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/esparser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/hevc_regs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/hevc_regs.h

Purpose: this header defines register offsets and selected bit fields for the Meson HEVC-family decoder block used by VP9 and HEVC paths. It covers assist scratch/mailbox registers, parser/shift/CABAC controls, MPRED, MPP reference tables, decompression, DBLK, SAO, compressed-body/header, MMU, firmware CPU, IMEM DMA, and scaling controls.

Important constants: assist mailbox and scratch offsets begin around `0xc000`. Parser stream and command registers include `HEVC_STREAM_*`, `HEVC_SHIFT_*`, `HEVC_PARSER_*`, and parser interrupt controls. Motion prediction registers include `HEVC_MPRED_CTRL0` with bits for new picture/tile, TMVP, refs, and MV read/write. Reference table and canvas/decompression registers include `HEVCD_MPP_ANC2AXI_TBL_*`, `HEVCD_MPP_ANC_CANVAS_*`, and `HEVCD_MPP_DECOMP_CTL*`. SAO and compressed memory registers include `HEVC_SAO_*`, `HEVC_CM_BODY_*`, `HEVC_CM_HEADER_*`, and MMU header addresses.

Control flow and integration: `codec_vp9.c` uses these registers to program parser commands, workspace sub-buffer addresses, reference scaling, MCRCC, MPRED motion-vector buffers, SAO output addresses, compressed/FBC output, MMU maps, and decode start/status. `codec_hevc_common.c` uses decompression, MPP, SAO, and compressed-memory registers for shared buffer setup. `vdec_hevc.c` in the same module likely uses the same header for HEVC decode.

State and persistence behavior: values written through these offsets are live decoder hardware state. Assist scratch registers act as a firmware ABI. Reference, SAO, MPRED, and DBLK registers persist across frames until reprogrammed by codec frame setup or reset by hardware stop paths.

Dependencies: source files use `amvdec_read_dos()` and `amvdec_write_dos()` with these offsets against the DOS MMIO base. Bit macros depend on kernel `BIT()`.

Risks: many offsets are densely hardware-specific and shared across codecs; incorrect changes can break VP9 and HEVC simultaneously. Some register aliases overlap intentionally, such as DBLK status/config offsets, and should not be deduplicated without hardware confirmation. Revision-specific behavior is handled in codec code, not this header.

Test signals: VP9 and HEVC stream start, parser command load, mailbox IRQ, reference-table setup, 10-bit FBC/MMU decode, SAO output to NV12, and register traces comparing GXBB/GXL/G12A/SM1 behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/hevc_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec.c

Purpose: this file is the core V4L2 mem2mem platform driver for Amlogic Meson VDEC. It registers the video device, opens per-file decoding sessions, owns VB2 queue setup and streaming lifecycle, schedules ESPARSER work, dispatches IRQs to codec ops, handles formats/events/decoder commands, and powers the selected hardware block through `amvdec_ops`.

Important APIs and functions: `vdec_open()` allocates `amvdec_session`, initializes V4L2 m2m context, controls, default formats, locks, timestamp/recycle lists, and parser work. `vdec_start_streaming()` enforces a single active session, allocates the 16 MiB VIFIFO, resets session counters, powers hardware via `vdec_poweron()`, starts recycle thread if needed, and schedules parser work. `vdec_stop_streaming()` powers off, drains, frees VIFIFO/canvas/timestamps/recycle/private codec state, and marks queued buffers error. Format operations negotiate coded OUTPUT formats and NV12M/YUV420M capture formats. `vdec_decoder_cmd()` implements STOP/START and EOS/drain behavior. `vdec_probe()` maps MMIO resources, gets clocks/reset/canvas/regmap, requests IRQs, initializes ESPARSER, registers V4L2 device and video node.

Control flow: userspace opens the video node, sets OUTPUT/CAPTURE formats, queues buffers, and streams on. When OUTPUT streaming starts and capture buffers are ready, the driver powers DOS/parser/VDEC, initializes codec/hardware, and queues source buffers into ESPARSER. Decode IRQs call `vdec_isr()` to update activity time and run codec hard ISR, then `vdec_threaded_isr()` runs codec threaded logic to complete capture buffers or raise source-change events. Source changes move the session to `STATUS_NEEDS_RESUME`; capture reconfiguration and `changed_format` trigger codec `resume()`.

State and persistence: `amvdec_core` is per platform device and stores MMIO bases, clocks, canvas provider, V4L2 device, current session, and mutex. `amvdec_session` is per open file and stores formats, queues, VIFIFO DMA memory, stream flags, sequence counters, timestamp list, recycle list/thread, status, and codec private data. Only one session may be active in hardware at a time through `core->cur_sess`.

Dependencies and integration points: integrates Linux platform devices, OF match data (`vdec_platform_*`), clocks, resets, AO syscon regmap, Meson canvas, V4L2 mem2mem/ioctls/events/controls, vb2 DMA-contig, ESPARSER, and codec/hardware ops tables.

Risks: state transitions among `STATUS_STOPPED`, `STATUS_INIT`, `STATUS_RUNNING`, and `STATUS_NEEDS_RESUME` are subtle, especially streamoff during source change. `vdec_close()` does not explicitly cancel parser work; correctness relies on VB2/m2m stream shutdown before context release. The hard IRQ assumes `core->cur_sess` is valid. Capture `YUV420M` setup assigns plane 2 size as `output_size / 2` in try_fmt while queue setup expects `/4`, which should be reviewed. Single-session enforcement returns queued buffers to `QUEUED` on busy start, which userspace behavior should be tested.

Test signals: V4L2 compliance for mem2mem ioctls, format negotiation, min buffer controls, streamon/off order permutations, concurrent opens with one active decode, source-change event/reallocation, EOS event, drain, capture buffer recycling, IRQ after streamoff, platform probe defers, and remove after registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec.h

Purpose: this header defines the core data model and callback contracts for the Meson VDEC driver. It is shared by the platform core, ESPARSER, hardware back ends, helpers, and codec implementations.

Important APIs and types: `struct amvdec_core` stores singleton device resources: MMIO bases, AO regmap, clocks, reset, canvas provider, V4L2/video devices, current session, platform data, and lock. `struct amvdec_ops` abstracts hardware block operations: start, stop, parser config, and VIFIFO level. `struct amvdec_codec_ops` abstracts codec operations including start/stop, optional extended firmware, pending buffer accounting, recycle, drain, resume, EOS sequence, and ISR callbacks. `struct amvdec_format` maps a coded OUTPUT pixel format to buffer limits, resolution limits, flags, hardware ops, codec ops, firmware path, and supported capture formats. `struct amvdec_session` is the per-open decode state. `amvdec_get_output_size()` is declared for shared output sizing.

Control flow and integration: platform tables bind formats to a pair of hardware and codec ops. `vdec.c` uses `amvdec_session` for all queue, format, event, and streaming state, while codec files attach private data through `priv` and use helper functions to complete buffers or signal source changes.

State and persistence behavior: the header documents all persistent per-device and per-session fields: stream flags, sequence counters, VIFIFO memory, canvas allocations, timestamp/recycle lists, active status, format fields, pixel aspect, and firmware buffer-index mapping. This makes it the main ownership map for cleanup paths.

Dependencies: includes Linux IRQ, regmap, list, V4L2/vb2, controls, V4L2 device, Meson canvas, and `vdec_platform.h`.

Risks: many fields are accessed across workqueue, IRQ, threaded IRQ, recycle kthread, and ioctl contexts, so locking expectations must stay clear. Optional codec callbacks require null checks in generic code. `fw_idx_to_vb2_idx[32]` bounds firmware buffer indices and should align with format max buffer counts.

Test signals: compile coverage across every implementation file after struct changes; runtime stress around queueing, IRQ completion, recycle thread, source changes, and streamoff validates the documented ownership model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_1.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_1.c

Purpose: this file implements the `amvdec_ops` backend for the legacy VDEC_1 hardware block, used by MPEG-1/2 and H.264 style firmware. It powers/resets the block, loads microcode into IMEM, configures the VIFIFO stream buffer, integrates ESPARSER, and delegates codec-specific setup/stop to `amvdec_codec_ops`.

Important APIs and functions: `vdec_1_load_firmware()` requests the codec firmware, verifies at least 16 KiB microcode, copies it to coherent DMA memory, programs IMEM DMA registers, waits for DMA completion, and passes remaining firmware bytes to optional `load_extended_firmware()`. `vdec_1_stbuf_power_up()` initializes VLD VIFIFO registers from session DMA addresses. `vdec_1_conf_esparser()` writes VDEC_1-specific parser control. `vdec_1_start()` enables clocks, powers and de-isolates VDEC_1 using AO sysctrl and DOS registers, resets hardware, enables memories/clocks, loads firmware, runs codec start, enables mailbox IRQ, selects two-plane output for NV12M, starts firmware CPU, and settles. `vdec_1_stop()` calls an internal stop sequence and disables the clock.

Control flow: generic `vdec_poweron()` enables DOS parser/DOS clocks, then calls `vdec_1_start()`, then powers ESPARSER. Stop sets `should_stop`, waits for inactivity, optional codec drain, then calls `vdec_1_stop()`. If any start step fails, `__vdec_1_stop()` resets firmware state, masks IRQs, powers down memories and hardware, and calls codec stop if private state exists.

State and persistence: VDEC_1 state is almost entirely hardware state plus codec-private session data. Firmware microcode DMA memory is temporary during load. VIFIFO registers persist during streaming. AO power/isolation bits differ for SM1 versus older revisions. Codec private allocations are owned by codec stop.

Dependencies and integration points: depends on firmware API, clocks, AO regmap, DOS registers, VDEC helpers, ESPARSER configuration callback, and codec ops. It exports `vdec_1_ops` for platform format tables.

Risks: firmware DMA wait is a busy loop with a fixed 1000-iteration budget and no sleep, so hardware hangs become immediate errors. `static void *mc_addr` and `static dma_addr_t mc_addr_map` inside firmware load are unnecessary static state and could be confusing if concurrency were ever allowed. Power/isolation sequencing is revision-specific and should not be changed without hardware validation.

Test signals: firmware missing/too-small/DMA-hang cases, H.264 extended firmware load, MPEG startup, NV12M versus YUV420M output bit, SM1 power bits versus older bits, stop after partial start failure, and mailbox IRQ enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_1.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_1.h

Purpose: this header exposes the VDEC_1 hardware backend operations table.

Important API: it includes `vdec.h` and declares `extern struct amvdec_ops vdec_1_ops;`. The implementation supplies start, stop, ESPARSER configuration, and VIFIFO level callbacks.

Control flow and integration: platform format descriptors use `vdec_1_ops` for codecs that run on the VDEC_1 hardware block. Generic `vdec.c` invokes these callbacks during power-on, power-off, parser setup, and VIFIFO free-space accounting.

State and persistence behavior: no state is declared here. Runtime hardware state is stored in registers and per-session VIFIFO fields defined in `vdec.h`.

Dependencies: depends on `struct amvdec_ops` from `vdec.h` and the `vdec_1.o` object being linked into the composite driver.

Risks: adding callbacks to `struct amvdec_ops` requires updating this implementation. The global ops object should be treated as immutable after initialization.

Test signals: compile/link symbol resolution and runtime format selection for MPEG/H.264 should show the generic core calling VDEC_1 start/stop and parser methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_helpers.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_helpers.c

Purpose: this file provides shared Meson VDEC helpers for MMIO access, AM21C compressed-frame sizing, canvas allocation/programming, destination-buffer completion, timestamp tracking, pixel aspect calculation, source-change signaling, and session abort.

Important APIs and functions: `amvdec_read_dos()`, `amvdec_write_dos()`, bit set/clear helpers, `amvdec_read_parser()`, and `amvdec_write_parser()` wrap MMIO. `amvdec_am21c_body_size()`, `amvdec_am21c_head_size()`, and `amvdec_am21c_size()` compute compressed buffer sizes. `amvdec_set_canvases()` maps queued destination VB2 buffers into Meson canvas IDs for NV12M or YUV420M and fills `fw_idx_to_vb2_idx`. Timestamp helpers `amvdec_add_ts()` and `amvdec_remove_ts()` maintain a spinlock-protected list. Completion helpers map firmware indices or VIFIFO offsets to capture buffers and call `v4l2_m2m_buf_done()`. `amvdec_src_change()` updates dimensions/min buffers and emits V4L2 source-change events. `amvdec_abort()` errors both queues.

Control flow: codec start/resume calls `amvdec_set_canvases()`. ESPARSER records timestamps before writing source buffers. Codec IRQs complete destination buffers through `amvdec_dst_buf_done_idx()`, `amvdec_dst_buf_done()`, or `amvdec_dst_buf_done_offset()`, which set payloads, timestamps, sequence, flags, EOS/LAST state, and reschedule parser work. Source-change paths either resume immediately if the current capture queue is already compatible or mark `STATUS_NEEDS_RESUME` and notify userspace.

State and persistence: canvas IDs allocated per session are stored in `canvas_alloc` and freed by `vdec.c`. Timestamps persist until matched or removed. `sequence_cap`, pixel aspect, dimensions, `changed_format`, status, and `ctrl_min_buf_capture` are updated here. `fw_idx_to_vb2_idx` maps firmware buffer slots to VB2 indices for later completions.

Dependencies and integration points: depends on Meson canvas API, V4L2 mem2mem/events, vb2 DMA-contig, gcd helper, and `vdec.h` session/core definitions. Exported GPL symbols are used by all codec and hardware files.

Risks: `amvdec_dst_buf_done_offset()` accepts `allow_drop` but does not use it, so callers may assume unsupported behavior. Timestamp matching by offset can drop records after repeated misses and logs errors when unmatched, so VIFIFO wrap accounting and firmware offsets must be correct. Canvas allocation is monotonic during a stream and can hit `MAX_CANVAS`. Plane payload and bytes-per-plane assumptions must remain consistent with format negotiation.

Test signals: NV12M/YUV420M canvas setup, canvas exhaustion, timestamp FIFO and offset matching, EOS LAST flag behavior, source-change with compatible and incompatible capture queues, abort queue errors, and AM21C size calculations for aligned/unaligned dimensions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_helpers.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_helpers.h

Purpose: this header declares shared helper functions used across the Meson VDEC core, ESPARSER, hardware back ends, and codecs.

Important APIs: declarations cover canvas mapping (`amvdec_set_canvases()`), DOS/PARSER MMIO accessors and bit helpers, AM21C compressed-size helpers, destination-buffer completion by firmware index, direct buffer, or VIFIFO offset, timestamp add/remove, display-aspect-ratio to pixel-aspect conversion, source-change notification, and session abort.

Control flow and integration: codec start/resume uses canvas and AM21C helpers, ESPARSER uses timestamp helpers and parser MMIO accessors, codec IRQ handlers use destination completion helpers, and parsed metadata paths use PAR/source-change helpers. `amvdec_abort()` is the common fatal-error escape hatch for firmware or allocation failures.

State and persistence behavior: the header itself has no state, but its functions mutate central `amvdec_session` fields: canvas allocation arrays, timestamp list, sequence counters, pixel aspect, dimensions, min-buffer control, status, and VB2 queue error state.

Dependencies: includes `vdec.h`, which supplies core/session types and V4L2/vb2 dependencies. Implementation additionally requires Meson canvas, V4L2 events, and DMA-contig helpers.

Risks: helper signatures form a broad internal ABI; changing them requires edits across most driver files. Completion helpers assume caller-provided firmware indices and offsets are valid for current session mappings. Exported helper availability must stay aligned with the composite object list.

Test signals: build all codec files after signature changes; runtime tests should cover every helper family through MPEG/H.264/VP9 decode, source changes, EOS, and abort.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_helpers.h -->
