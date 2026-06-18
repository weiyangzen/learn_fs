# subset-b-004174 OMAP3 ISP Research

This grouped report covers the OMAP3 ISP CCP2, CSI-2, CSI PHY, H3A stats, histogram, preview, and register-definition files requested for `subset-b-004174`. Each section is delimited for deterministic split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispccp2.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispccp2.c

## Purpose
`ispccp2.c` implements the TI OMAP3 ISP CCP2/CSI1 receiver media subdevice. It supports sensor input through the CCP2 interface and memory input through the logical channel memory engine, exposes a V4L2 subdevice with sink/source pads, owns a video-output node for memory input, and bridges incoming RAW Bayer data to the CCDC video port.

## Important APIs, Types, And Functions
- Public entry points: `omap3isp_ccp2_init()`, `omap3isp_ccp2_cleanup()`, `omap3isp_ccp2_register_entities()`, `omap3isp_ccp2_unregister_entities()`, and `omap3isp_ccp2_isr()`.
- Stream lifecycle: `ccp2_s_stream()` handles `ISP_PIPELINE_STREAM_CONTINUOUS`, `ISP_PIPELINE_STREAM_SINGLESHOT`, and stopped states, including CSI PHY acquisition/release, SBL read enable, and hardware enable/disable.
- Hardware configuration: `ccp2_reset()`, `ccp2_pwr_cfg()`, `ccp2_phyif_config()`, `ccp2_vp_config()`, `ccp2_lcx_config()`, and `ccp2_mem_configure()` program CCP2 control, logical channel, video port, and memory-channel registers.
- Format operations: `ccp2_try_format()`, `ccp2_enum_mbus_code()`, `ccp2_enum_frame_size()`, `ccp2_get_format()`, and `ccp2_set_format()` constrain supported sink formats to `SGRBG10` and `SGRBG10_DPCM8`, force the source to uncompressed `SGRBG10`, and propagate sink-to-source dimensions.
- Media/video hooks: `ccp2_link_setup()` records whether the sink is fed from memory or a sensor and whether the source feeds CCDC; `ccp2_video_queue()` writes the DMA input address for memory input.

## Control Flow
Initialization sets up wait queues, revision-specific regulator/PHY references, media pads, the V4L2 subdev, a video-output queue, default formats, and then resets the module. Continuous streaming acquires the CSI PHY when present, configures sensor-facing physical/logical-channel registers from `isp_bus_cfg`, prints register status, and enables all logical channels plus interface mode. Single-shot streaming configures memory read parameters from the sink format, enables the CSI1 read SBL path, and enables the memory channel. Stopping synchronizes with in-flight hardware through `omap3isp_module_sync_idle()`, disables the appropriate interface, disables SBL for memory input, and releases the PHY for sensor input.

## State And Persistence
Persistent runtime state lives in `struct isp_ccp2_device`: active pad formats, input/output selection, cached logical-channel and memory-channel configuration, `video_in`, optional `phy`, optional `vdds_csib` regulator, stream state, stop wait queue, and stopping atomic. Register state is volatile hardware state restored on stream configure rather than saved across power loss. DMA addresses are per-buffer state written on queue and EOF interrupts.

## Dependencies And Integration Points
This file depends on the ISP core register helpers, pipeline state helpers, V4L2/media entity APIs, `ispvideo` queues, CSI PHY management, SBL enable/disable, sensor bus configuration via `v4l2_subdev_to_bus_cfg()`, and sensor callbacks such as `g_skip_top_lines`. It integrates with CCDC through the media graph and video port, with memory input through the local video-output node, and with platform power through `vdds_csib` on older revisions.

## Risks And Edge Cases
- `ccp2_s_stream()` calls `ccp2_if_configure()` without checking its return value in the continuous path, so a failed bus/PHY configuration can be followed by interface enable.
- Link setup uses a documented hack that encodes remote entity type into the local pad index; graph changes could break input/output classification.
- Memory read alignment is special: line length and padded line length need 32-byte handling despite underlying 128-bit constraints.
- Revision-specific video-port divisor encoding differs substantially between OMAP3430-style and revision 15.0 hardware.
- Error IRQ handling marks the pipeline error but otherwise leaves recovery to the broader pipeline.

## Test Signals
Useful signals include media graph link validation for memory versus sensor input exclusivity, V4L2 format enumeration/clamping tests, stream start/stop tests for both continuous and single-shot paths, regulator and PHY acquire/release failure injection, EOF buffer-rotation tests, and IRQ error tests verifying `pipe->error` is set for LCx and OCP errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispccp2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispccp2.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispccp2.h

## Purpose
`ispccp2.h` declares the CCP2 media subdevice contract used by the OMAP3 ISP core and `ispccp2.c`. It defines pad indexes, media-graph input/output state enums, cached hardware configuration structures, and the public CCP2 lifecycle/ISR functions.

## Important APIs, Types, And Functions
- Pad constants: `CCP2_PAD_SINK`, `CCP2_PAD_SOURCE`, and `CCP2_PADS_NUM`.
- Routing enums: `enum ccp2_input_entity` distinguishes no input, sensor input, and memory input; `enum ccp2_output_entity` distinguishes no output, CCDC output, and memory output placeholder.
- Cached register config: `struct isp_interface_lcx_config` stores CRC, data start/size, and format for logical channel configuration; `struct isp_interface_mem_config` stores memory-channel destination, dimensions, and offsets.
- Device state: `struct isp_ccp2_device` embeds the V4L2 subdev, media pads, active formats, routing state, video queue, PHY/regulator handles, stream state, wait queue, and stop atomic.
- Public functions expose initialization, cleanup, entity registration, entity unregistration, and interrupt handling.

## Control Flow
The header itself has no executable control flow. Its declarations enable the ISP core to initialize CCP2 during driver probe, register/unregister the CCP2 subdev during media-device setup/teardown, and dispatch CCP2 interrupts to `omap3isp_ccp2_isr()`.

## State And Persistence
The struct fields define all persistent in-kernel CCP2 state. There is no userspace ABI here beyond the V4L2/media behavior implemented by the C file. The header deliberately caches format and link state outside registers so stream configuration can be regenerated when links or formats change.

## Dependencies And Integration Points
It depends on V4L2 media-bus types and forward-declares `struct isp_device` and `struct isp_csiphy`. It is included by `ispccp2.c` and by ISP core code that owns `struct isp_device`.

## Risks And Edge Cases
The output enum contains `CCP2_OUTPUT_MEMORY`, but the implementation comments state CCP2 write-to-memory is not currently supported. Consumers must treat that enum as future-facing rather than implemented functionality. The `formats` array size is tied to `CCP2_PADS_NUM`; pad constants must remain consistent with media entity setup.

## Test Signals
Build coverage should catch mismatched function declarations and struct layout users. Runtime tests should verify that media links set `input` and `output` consistently with the enum values stored in this struct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispccp2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispcsi2.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispcsi2.c

## Purpose
`ispcsi2.c` implements the OMAP3 ISP CSI-2 receiver subdevice. It configures CSI-2 receiver registers, D-PHY timing through the associated PHY, context 0 packet handling, format mapping, IRQ handling, media links to CCDC or memory, and a video-capture node for CSI-2 memory output.

## Important APIs, Types, And Functions
- Public entry points: `omap3isp_csi2_init()`, `omap3isp_csi2_cleanup()`, `omap3isp_csi2_register_entities()`, `omap3isp_csi2_unregister_entities()`, `omap3isp_csi2_reset()`, and `omap3isp_csi2_isr()`.
- Receiver configuration: `csi2_if_enable()`, `csi2_recv_config()`, `csi2_ctx_config()`, `csi2_timing_config()`, and `csi2_configure()` program interface, context, timing, frame skipping, ECC, DPCM, and output mode.
- Format mapping: `csi2_ctx_map_format()` uses `__csi2_fmt_map` to map V4L2 media bus formats, DPCM decompression, output destination, and revision 15.0 differences to CSI-2 context format IDs.
- Streaming: `csi2_set_stream()` acquires/releases the PHY, enables SBL writes for memory output, configures hardware, starts context/interface when buffers are available, and handles stop synchronization.
- IRQ/buffer path: `csi2_isr_ctx()` handles frame-end context interrupts and initial frame skipping; `csi2_isr_buffer()` rotates capture buffers; `csi2_queue()` arms the first buffer or restarts from underrun.

## Control Flow
Probe initializes CSI2A for all supported hardware and prepares CSI2C only on revision 15.0, though entity initialization is only performed for CSI2A in this file. Link setup records memory and CCDC output bits and updates video-port-only/clock-enable control flags. On stream start, the PHY is acquired, SBL write is enabled if memory output is active, receiver/context/timing registers are programmed from pipeline bus data, and hardware starts immediately unless memory output has no queued buffer. IRQs clear top-level and context status, mark the pipeline errored on OCP, FIFO, uncorrectable ECC, short packet, or complex IO errors, skip configured initial frames, and rotate memory buffers on frame-end interrupts.

## State And Persistence
Persistent state is held in `struct isp_csi2_device`: active formats, output bitmask, DPCM flag, frame-skip count, PHY pointer, context array, timing array, control config, stream state, stop synchronization, and video queue. Context 0 carries virtual channel, format ID, DPCM predictor, data offsets, ping/pong addresses, and enable state. Hardware register state is volatile and reconstructed on each stream start.

## Dependencies And Integration Points
The file integrates with the V4L2 subdev/media graph, `ispvideo` capture queues, CSI PHY acquire/release/reset paths, ISP SBL write enablement, pipeline clock/rate metadata, sensor bus config and `g_skip_frames`, and format metadata from `omap3isp_video_format_info()`. It uses register definitions from `ispreg.h` and CSI-2 device/types from `ispcsi2.h`.

## Risks And Edge Cases
- Only context 0 is actively configured and handled despite hardware support for multiple contexts.
- `csi2_configure()` can return `-EBUSY` or `-EPIPE`, but `csi2_set_stream()` does not check that return before continuing.
- Frame skip behavior disables the video port by selecting memory-only format mapping until skipped frames are drained; this is hardware-workaround sensitive.
- The memory output path defers hardware start until a buffer is queued, so underrun flag handling is critical.
- CSI2C setup lacks corresponding entity/video cleanup in this file, reflecting partial availability or core-managed use; revision-specific users need care.

## Test Signals
Exercise format mapping for RAW10, RAW10 DPCM8, YUYV, memory-only, CCDC-only, combined output, and revision 15.0 user-defined IDs. Test media link exclusivity, no-buffer start and underrun restart, frame skip countdown, error IRQ propagation to `pipe->error`, PHY reset busy paths, and stop synchronization under active context interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispcsi2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispcsi2.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispcsi2.h

## Purpose
`ispcsi2.h` defines the CSI-2 receiver data model, format/event constants, pad constants, output flags, and public functions used by the OMAP3 ISP core and CSI-2 implementation.

## Important APIs, Types, And Functions
- Format IDs: `enum isp_csi2_pix_formats` lists hardware context format encodings for YUV422, RAW10, RAW8, DPCM decompression, video-port output, and user-defined data.
- IRQ enums: `enum isp_csi2_irqevents` and `enum isp_csi2_ctx_irqevents` describe top-level and context-specific interrupt bits.
- Config structs: `struct isp_csi2_ctx_cfg`, `struct isp_csi2_timing_cfg`, and `struct isp_csi2_ctrl_cfg` mirror context, timing, and receiver-control registers.
- `struct isp_csi2_device` embeds subdev/pads/formats/video node, hardware resource IDs, output bitmask, DPCM/frame-skip state, PHY pointer, context/timing/control config, stream state, and stop wait primitives.
- Public functions cover ISR, reset, init/cleanup, and entity registration.

## Control Flow
The header has no executable flow but defines the state consumed by `ispcsi2.c`. The ISP core can allocate two instances, CSI2A and CSI2C, assign register resources, and hand each to lifecycle or IRQ functions.

## State And Persistence
The header defines persistent CSI-2 state that survives between stream operations: active media-bus formats, context configuration, output mode, frame skipping, and video-node state. Hardware registers are treated as derived state and are reprogrammed from these fields.

## Dependencies And Integration Points
It depends on Linux integer/V4L2 types and forward-declares `struct isp_csiphy`. It is coupled to `ispreg.h` bit definitions through shared register-field meanings and to `ispvideo`/media entity infrastructure through embedded fields.

## Risks And Edge Cases
`ISP_CSI2_MAX_CTX_NUM` is set to 7 and the array allocates eight contexts, but the implementation currently uses context 0 only. Output flags are bitmasks and must be updated atomically enough under media graph setup assumptions. Hardware format IDs are non-obvious constants, so adding formats requires matching the implementation mapping table.

## Test Signals
Compile-time users should catch struct and prototype mismatches. Runtime tests should verify context 0 register programming matches the cached `struct isp_csi2_ctx_cfg`, and that output bitmasks drive `vp_only_enable` and `vp_clk_enable` correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispcsi2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispcsiphy.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispcsiphy.c

## Purpose
`ispcsiphy.c` manages the OMAP3 CSI/CCP2 physical-layer frontend. It routes ISP interfaces to PHY instances, validates lane configuration, programs D-PHY timing and lane polarity/position, powers PHYs through regulators and CSI2 PHY power commands, and serializes ownership between CSI2/CCP2 users.

## Important APIs, Types, And Functions
- Public lifecycle: `omap3isp_csiphy_init()` initializes PHY1/PHY2 metadata and mutexes; `omap3isp_csiphy_cleanup()` destroys mutexes.
- Ownership: `omap3isp_csiphy_acquire()` enables the regulator, resets the associated CSI2 block, assigns `phy->entity`, configures routing/timing/lanes, powers revision 15.0 PHYs on, and enables autoswitch; `omap3isp_csiphy_release()` reverses routing, disables autoswitch/power, disables the regulator, and clears ownership.
- Routing helpers: `csiphy_routing_cfg_3630()` and `csiphy_routing_cfg_3430()` write syscon/control registers for OMAP3630 and OMAP3430-specific routing.
- Power helpers: `csiphy_power_autoswitch_enable()` and `csiphy_set_power()` manipulate `ISPCSI2_PHY_CFG`.
- Configuration: `omap3isp_csiphy_config()` validates clock/data lane positions and polarity, selects CCP2 versus CSI-2 lane config, computes DDR clock, and writes `ISPCSIPHY_REG0/REG1` timing.

## Control Flow
Acquire is the central path. It fails early if no regulator is available, locks the PHY mutex, enables power, resets the CSI2 block, records the owning media entity, validates and programs bus routing and D-PHY settings from the active pipeline external bus config, then powers the PHY on for revision 15.0. Release locks the same mutex, derives the bus config from the owner entity, turns routing off where supported, powers down revision 15.0 PHYs, disables the regulator, and drops ownership.

## State And Persistence
Persistent state resides in `struct isp_csiphy`: ISP pointer, mutex, associated CSI2 device, regulator, current owning media entity, register resource IDs, and supported lane count. Syscon routing and PHY timing registers are volatile and reprogrammed on acquisition; comments note control register contents are lost in off-mode but acceptable while the ISP is active.

## Dependencies And Integration Points
The file depends on regmap/syscon for SoC control routing, Linux regulators for PHY power, ISP register helpers, the active ISP pipeline and `isp_bus_cfg`, CSI2 reset, and interface enums from OMAP3 ISP platform data. It is used by CSI2 and CCP2 stream-start paths.

## Risks And Edge Cases
- `omap3isp_csiphy_acquire()` does not disable the regulator for all failure paths after regulator enable; only the revision 15.0 power-command failure path explicitly disables it.
- Lane validation rejects duplicate data lanes and clock lane conflicts, but depends on platform bus config correctness.
- DDR clock calculation divides by `hweight32(used_lanes)`; a malformed zero-lane CSI2 config would be hazardous if not prevented upstream.
- `csiphy_routing_cfg_3430()` only supports CCP2B on PHY1; other interface requests silently do nothing.

## Test Signals
Test regulator-missing and regulator-enable failure paths, duplicate/invalid lane rejection, PHY ownership serialization, revision-specific routing writes, power command timeout handling, and CSI2/CCP2 stream start/stop sequences that acquire and release the same PHY.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispcsiphy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispcsiphy.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispcsiphy.h

## Purpose
`ispcsiphy.h` declares the CSI PHY state object and public acquire/release/init/cleanup API for OMAP3 ISP physical-layer users.

## Important APIs, Types, And Functions
- `struct isp_csiphy` stores the parent ISP, configuration mutex, associated CSI2 device, regulator, current owning media entity, register-resource IDs, and supported data-lane count.
- Public functions: `omap3isp_csiphy_acquire()`, `omap3isp_csiphy_release()`, `omap3isp_csiphy_init()`, and `omap3isp_csiphy_cleanup()`.

## Control Flow
The header establishes the ownership contract used by CCP2 and CSI2 stream paths: a media entity acquires the PHY before streaming and releases it when stopped. Initialization populates static hardware metadata before those paths run.

## State And Persistence
The key persistent field is `entity`, which records exclusive ownership and lets release derive the correct active pipeline/bus configuration. The mutex serializes configuration and power transitions.

## Dependencies And Integration Points
It includes `omap3isp.h` and forward-declares CSI2 and regulator types. The API connects ISP core device setup with CSI2/CCP2 receiver modules.

## Risks And Edge Cases
Consumers must pair acquire/release and must not access PHY registers outside the serialized ownership model. `num_data_lanes` is hardware-description state; incorrect initialization can allow invalid platform lane configs or reject valid ones.

## Test Signals
Build tests should cover API visibility. Runtime tests should verify acquire/release pairing, ownership tracking, and proper behavior when two media entities attempt to use the same PHY.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispcsiphy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isph3a.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isph3a.h

## Purpose
`isph3a.h` provides shared H3A Auto Exposure/White Balance and Auto Focus register constants and lifecycle declarations for the OMAP3 ISP statistics engines.

## Important APIs, Types, And Functions
- AEWB constants define packet size, saturation limits, change-flag bits, PCR enable/busy masks, and AEW mask composition.
- AF constants define register offsets, PCR masks, paxel field masks, coefficient masks, and bit shifts used by the AF programming code.
- Public lifecycle functions are `omap3isp_h3a_aewb_init()`, `omap3isp_h3a_aewb_cleanup()`, `omap3isp_h3a_af_init()`, and `omap3isp_h3a_af_cleanup()`.

## Control Flow
No executable control flow is present. The constants are used by the AEWB and AF implementations when validating userspace configs, converting them to register values, enabling hardware, and checking busy state.

## State And Persistence
The header has no persistent state. It defines the bit-level contract that lets `isph3a_aewb.c` and `isph3a_af.c` keep their cached `ispstat` private configs consistent with hardware registers.

## Dependencies And Integration Points
It includes the OMAP3 ISP userspace ABI header `linux/omap3isp.h`, so the limits and struct definitions used by ioctls are shared with driver code. It also references `struct isp_device` through function prototypes.

## Risks And Edge Cases
Incorrect mask/shift updates would corrupt H3A hardware programming and stats buffer sizing. AEWB and AF share the H3A PCR register, so constants must remain non-overlapping where the implementations use `isp_reg_clr_set()`.

## Test Signals
Compile coverage of AEWB/AF files exercises these constants. Functional tests should verify PCR programming for AF and AEWB can be enabled independently without clobbering unrelated bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isph3a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isph3a_aewb.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isph3a_aewb.c

## Purpose
`isph3a_aewb.c` implements the H3A Auto Exposure/Auto White Balance statistics subdevice using the generic `ispstat` framework. It validates userspace AEWB window configuration, computes buffer sizes, stages updates, programs H3A AEW registers, enables/disables the AEWB engine, and handles private ioctls for configuration, enable, and statistics retrieval.

## Important APIs, Types, And Functions
- `h3a_aewb_validate_params()` checks saturation, window sizes/counts/starts, black-window height, subsampling increments, and adjusts `buf_size`.
- `h3a_aewb_get_buf_size()` computes the stats buffer from window count plus unsaturated-block counters.
- `h3a_aewb_set_params()` copies changed fields into the current private config and sets `ispstat` update/config counters.
- `h3a_aewb_setup_regs()` writes active DMA buffer address and, when an update is pending, programs `AEWWIN1`, `AEWINSTART`, `AEWINBLK`, `AEWSUBWIN`, and AEWB PCR fields.
- `h3a_aewb_ioctl()` handles `VIDIOC_OMAP3ISP_AEWB_CFG`, stats request ioctls, and enable ioctl.
- Public lifecycle: `omap3isp_h3a_aewb_init()` and `omap3isp_h3a_aewb_cleanup()`.

## Control Flow
Initialization allocates current and recovery configs, fills a conservative valid recovery config, validates it, computes its buffer size, stores ops/event metadata in `isp->isp_aewb`, and calls `omap3isp_stat_init()`. Userspace config enters through the ioctl and the generic stat layer invokes validate/set callbacks. During stream/stat operation, `setup_regs` writes the current buffer address and applies pending register updates only when not disabled. Enable toggles `ISPH3A_PCR_AEW_EN` and the AEWB subclock. Cleanup delegates to `omap3isp_stat_cleanup()`.

## State And Persistence
AEWB state is persisted in `struct ispstat` plus its `priv` `struct omap3isp_h3a_aewb_config`. `update`, `inc_config`, `config_counter`, `configured`, `buf_size`, `active_buf`, and `recover_priv` are owned by the stat framework. Hardware register state is derived from the cached config at safe update points.

## Dependencies And Integration Points
This file depends on `ispstat` for buffer management, event delivery, stream control, and ioctl support. It uses H3A register offsets and bitfields from `ispreg.h`/`isph3a.h`, OMAP3 ISP ABI limits from `linux/omap3isp.h`, and ISP subclock helpers.

## Risks And Edge Cases
- Several fields must be even and inside hardware ranges; validation is the primary guard against invalid register encodings.
- `h3a_aewb_setup_regs()` returns early when disabled, so pending updates are deferred until the engine is active.
- The current config is updated field-by-field; partial updates are intentional but make future struct changes error-prone.
- Buffer size can be increased or capped based on validation, so userspace must observe the returned configuration size.

## Test Signals
Validate boundary tests for every AEWB window/count/subsample field, buffer-size computation for window counts not divisible by eight, ioctl config/enable/stat request behavior, register-value programming from a known config, recovery-config validity, and subclock enable/disable pairing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isph3a_aewb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isph3a_af.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isph3a_af.c

## Purpose
`isph3a_af.c` implements the H3A Auto Focus statistics subdevice through the generic `ispstat` framework. It validates AF paxel, IIR, HMF, RGB-position, and focus-value mode settings; stages config changes; programs AF registers and coefficient tables; toggles the AF engine; and exposes private ioctls for configuration and statistics.

## Important APIs, Types, And Functions
- `h3a_af_validate_params()` validates horizontal/vertical paxel count, paxel size and increment, start positions, IIR coefficient bounds, IIR start, the known 12-pixel corruption case, and buffer size.
- `h3a_af_setup_regs()` writes the stats buffer address, paxel geometry, IIR start, two coefficient sets, and PCR bits for RGB position, focus-value mode, A-law, and median filter.
- `h3a_af_set_params()` compares all relevant fields, copies the user config when changed or not yet configured, updates config counters, and computes exact buffer size.
- `h3a_af_ioctl()` handles AF config, stat request, time32 stat request, and enable ioctls.
- Public lifecycle: `omap3isp_h3a_af_init()` and `omap3isp_h3a_af_cleanup()`.

## Control Flow
Initialization allocates current and recovery configs, populates minimum valid paxel defaults, validates and sizes the recovery config, stores ops/event metadata, and initializes the stat subdevice. Userspace ioctls flow through generic stat helpers into validation and set callbacks. On hardware setup, the active buffer address is always refreshed when enabled, while full register programming occurs only if `af->update` is set. Enable toggles `ISPH3A_PCR_AF_EN` and the AF subclock.

## State And Persistence
AF persistent state is in `isp->isp_af` and the private `omap3isp_h3a_af_config`. The generic stat framework tracks buffer state, update flags, configuration counters, recovery config, and enabled/disabled state. Hardware AF registers are treated as derived volatile state.

## Dependencies And Integration Points
It depends on the OMAP3 ISP ABI AF config structs/limits, H3A register macros, ISP register helpers, ISP subclock helpers, V4L2 subdev ioctl/event operations, and `ispstat` for common stats behavior.

## Risks And Edge Cases
- AF coefficient programming assumes `OMAP3ISP_AF_NUM_COEF` includes index 10 and writes paired coefficients up to index 9 plus standalone index 10.
- The hardware corruption workaround rejects more than nine windows when paxel area is exactly 12; regression tests should preserve this behavior.
- `h3a_af_set_params()` jumps out at the first changed field and then copies the full struct, which is correct but makes diff-based reasoning less direct.
- Shared H3A PCR bits must be modified using masks to avoid clobbering AEWB fields.

## Test Signals
Boundary tests for paxel count/size/start/increment, IIR coefficient maximums, invalid 12-area/many-window case, known config-to-register encodings, ioctl dispatch, recovery-config validation, stat buffer sizing, and AF enable/busy behavior are the strongest signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isph3a_af.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isphist.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isphist.c

## Purpose
`isphist.c` implements the OMAP3 ISP histogram statistics subdevice. It validates histogram region/bin/white-balance configuration, programs histogram registers, clears and reads hardware histogram memory, uses DMA when possible with PIO fallback, and exposes stats configuration/request/enable ioctls through `ispstat`.

## Important APIs, Types, And Functions
- `hist_validate_params()` checks CFA mode, region count, region bounds/order, legal bin counts per region count, and buffer size.
- `hist_setup_regs()` computes control, white-balance gain, and region registers, clears histogram memory, writes all hardware registers, and updates stat framework config counters.
- `hist_reset_mem()` clears internal histogram memory and resets frame accumulation wait count.
- `hist_buf_process()` gates capture on error/enabled state and accumulated-frame count, then chooses DMA or PIO readout.
- `hist_buf_dma()` configures a DMA slave transfer from histogram data register to the active stats buffer; `hist_buf_pio()` reads the same data by repeated register reads.
- Public lifecycle: `omap3isp_hist_init()` requests an optional DMA channel and initializes the stat subdevice; `omap3isp_hist_cleanup()` releases DMA and cleans up stats.

## Control Flow
Initialization allocates config storage, attempts to obtain any slave-capable DMA channel, falls back to PIO on non-deferral failure, assigns stat ops/event type, and initializes the stat subdevice. Config ioctls validate and stage settings through generic stat callbacks. When setup is requested, memory is cleared before registers are programmed. At interrupt/stat processing time, the module waits for `num_acc_frames`, reads stats through DMA or PIO, resets the wait counter, and returns stat-buffer status to the framework. DMA completion clears the hardware clear bit, notifies the stat framework, and signals histogram DMA completion to the ISP core.

## State And Persistence
State persists in `struct ispstat` and private `struct omap3isp_hist_config`, including current region/bin/CFA/gain settings, wait-accumulation count, active buffer, DMA channel, and update/config counters. Hardware histogram memory is explicitly cleared during setup and error handling to avoid stale accumulation.

## Dependencies And Integration Points
This file depends on Linux DMAEngine, ISP register helpers, histogram register definitions, `ispstat`, V4L2 subdev ioctls/events, and ISP helpers such as `omap3isp_flush()` and `omap3isp_hist_dma_done()`. It uses `isp->mmio_hist_base_phys` as the DMA source base.

## Risks And Edge Cases
- DMAEngine cannot report transfer errors in the callback, so failed hardware reads may only surface indirectly.
- `cfg.src_maxburst = hist->buf_size / 4` depends on valid, bounded buffer sizing.
- `hist_set_params()` copies `user_cfg` before normalizing `num_acc_frames == 0` on `user_cfg`, leaving a possible inconsistency where `cur_cfg->num_acc_frames` remains zero while later logic expects reset behavior.
- Histogram memory must be cleared after invalid buffers/errors to avoid stale stats.

## Test Signals
Test histogram bin limits by region count, invalid region coordinates, DMA request deferral versus fallback, PIO readout with valid/invalid buffers, accumulation count behavior, clear-bit handling, ioctl dispatch, and config-to-register values for CFA, gains, and regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isphist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isphist.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isphist.h

## Purpose
`isphist.h` declares the OMAP3 ISP histogram module lifecycle functions and a small hardware constant used by the histogram implementation.

## Important APIs, Types, And Functions
- `ISPHIST_IN_BIT_WIDTH_CCDC` defines the 10-bit CCDC input width used to compute histogram bin right-shift values.
- Public functions: `omap3isp_hist_init()` and `omap3isp_hist_cleanup()`.

## Control Flow
The header has no executable control flow. It lets the ISP core initialize and clean up histogram statistics support, and lets `isphist.c` derive bin shifts from the CCDC input width.

## State And Persistence
No state is declared in this header. Persistent histogram state is held in `struct ispstat` and private config allocated by `isphist.c`.

## Dependencies And Integration Points
It includes the OMAP3 ISP userspace ABI header for histogram config definitions and forward-declares `struct isp_device`. It is coupled to `isphist.c` and ISP core probe/remove code.

## Risks And Edge Cases
The include guard comment omits `_H`, but the guard macro itself is valid. If the CCDC input bit width changes, histogram bin shift calculations must be revisited with this constant.

## Test Signals
Build tests cover lifecycle prototype use. Histogram functional tests indirectly verify `ISPHIST_IN_BIT_WIDTH_CCDC` through expected bin shift register values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isphist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isppreview.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isppreview.c

## Purpose
`isppreview.c` implements the OMAP3 ISP preview engine subdevice. The preview engine performs Bayer/greyscale to YUV processing with configurable CFA interpolation, gamma, noise filtering, defect correction, white balance, color conversion, luma/chroma processing, brightness/contrast, crop handling, memory input/output, and resizer forwarding.

## Important APIs, Types, And Functions
- Public entry points: `omap3isp_preview_init()`, `omap3isp_preview_cleanup()`, `omap3isp_preview_register_entities()`, `omap3isp_preview_unregister_entities()`, `omap3isp_preview_isr()`, `omap3isp_preview_isr_frame_sync()`, `omap3isp_preview_busy()`, and `omap3isp_preview_restore_context()`.
- Parameter programming: numerous `preview_config_*()` and `preview_enable_*()` helpers write tables and registers for luma, inverse A-law, median filter, CFA, chroma suppression, white balance, black adjustment, RGB blending, CSC, YC limits, defect correction, dark frame, noise filter, gamma, contrast, and brightness.
- Shadow state: `preview_params_lock()`, `preview_params_unlock()`, `preview_params_switch()`, `preview_config()`, and `preview_setup_hw()` implement double-buffered parameter updates protected by a spinlock.
- Format/crop: `preview_try_format()`, `preview_try_crop()`, enum/get/set format operations, and selection operations constrain input formats, output YUV formats, and hidden hardware margins.
- Streaming/buffers: `preview_configure()`, `preview_enable_oneshot()`, `preview_set_stream()`, `preview_isr_buffer()`, `preview_video_queue()`, and address/offset helpers coordinate one-shot hardware runs with memory queues and SBL paths.
- Media integration: `preview_link_setup()` enforces either CCDC or memory input and either resizer or memory output.

## Control Flow
Initialization sets default image-processing tables and parameters, creates controls for brightness/contrast, initializes media pads, default formats/crop, and video input/output nodes. Userspace private preview config copies enabled feature structs from userspace into inactive shadow parameter sets, marks updates, and switches them when neither active nor shadow copies are busy. Stream start enables the preview subclock, configures input/output format, crop margins, SBL bandwidth, active parameter registers, output port bits, offsets, YUV byte order, and then starts one-shot execution as required. Interrupt handling applies pending shadow updates, recomputes input-size margins, rotates memory buffers, marks pipeline idle input/output, and restarts one-shot operation for continuous pipelines.

## State And Persistence
Persistent state lives in `struct isp_prev_device`: media subdev/pads, active formats, crop rectangle, V4L2 controls, input/output routing, video queues, stream state, wait/stop primitives, and the nested double-buffered `params` object. The hardware register context is restored through `omap3isp_preview_restore_context()` by marking all features for update and reprogramming them from cached state.

## Dependencies And Integration Points
This file depends on V4L2 subdev, controls, and media entity APIs; ISP register helpers and SBL controls; pipeline timing/rate state; `ispvideo` buffer queues; format metadata from `omap3isp_video_format_info()`; table headers (`cfa_coef_table.h`, `gamma_table.h`, `noise_filter_table.h`, `luma_enhance_table.h`); and register macros from `ispreg.h`. It connects upstream to CCDC or memory and downstream to resizer or memory capture.

## Risks And Edge Cases
- The preview engine is used in one-shot mode even for continuous operation; correct restart on ISR/frame-sync and underrun flags is critical.
- Hidden crop margins depend on enabled features and Bayer/non-Bayer format; bugs can cause line/frame overflow or Bayer pattern shifts.
- Userspace config copying uses pointers inside `omap3isp_prev_update_config`; each feature needs correct offset/size metadata in `update_attrs`.
- Double-buffered parameter bit logic is subtle and concurrency-sensitive because config ioctls and ISR updates share state.
- Memory input has a documented 64-byte alignment hardware bug despite a nominal 32-byte TRM requirement.

## Test Signals
Strong tests include format/crop clamping for all input/output formats, hidden margin calculations with feature combinations, brightness/contrast V4L2 control updates, private config copy fault injection, shadow-parameter switch races, stream start/stop for memory and CCDC input, memory and resizer output link exclusivity, buffer underrun restart, context restore, and register-programming snapshots for default parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isppreview.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isppreview.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isppreview.h

## Purpose
`isppreview.h` defines the preview engine's public device structure, feature flags, pad constants, routing enums, image-processing parameter cache, and lifecycle/ISR APIs.

## Important APIs, Types, And Functions
- Control constants define brightness and contrast ranges, defaults, steps, and units.
- Feature bits extend the OMAP3 ISP preview ABI with `OMAP3ISP_PREV_CONTRAST`, `OMAP3ISP_PREV_BRIGHTNESS`, and `OMAP3ISP_PREV_FEATURES_END`.
- Routing constants define `enum preview_input_entity`, `PREVIEW_OUTPUT_RESIZER`, and `PREVIEW_OUTPUT_MEMORY`.
- `struct prev_params` stores all configurable preview processing blocks, feature/update/busy masks, and brightness/contrast values.
- `struct isp_prev_device` embeds V4L2 subdev, pads, formats, crop, control handler, routing state, video input/output nodes, double-buffered parameter state with spinlock, stream state, and stop synchronization.
- Public functions expose init/cleanup, entity registration, frame-sync ISR, main ISR, busy check, and context restore.

## Control Flow
This header defines the state consumed by `isppreview.c` and by ISP core IRQ/probe code. The core calls init/register during setup, dispatches preview interrupts and frame-sync interrupts at runtime, and calls cleanup/unregister during teardown.

## State And Persistence
The nested `params` object is the most important persistent state: two copies of `struct prev_params`, an active-bit mask selecting which copy owns each feature, and a spinlock. Formats, crop, input/output routing, and stream state persist between operations and drive register programming.

## Dependencies And Integration Points
It includes the OMAP3 ISP ABI, V4L2 controls, and `ispvideo.h`. It links the preview engine to media graph nodes, video queues, V4L2 control handling, and ISP core interrupt/context-management paths.

## Risks And Edge Cases
Feature bits must remain aligned with the `update_attrs` array in `isppreview.c`; adding a feature requires updating both. Output flags are bitmasks, and the implementation currently rejects multiple simultaneous output paths. `PREV_PADS_NUM` must match the formats/pads arrays and media entity setup.

## Test Signals
Build tests catch layout/prototype mismatches. Runtime tests should verify active/shadow parameter transitions, brightness/contrast control limits, media link state transitions, and that public ISR/context functions operate on the state fields declared here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isppreview.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispreg.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispreg.h

## Purpose
`ispreg.h` is the central register offset and bitfield map for the OMAP3 ISP driver. For this subset it supplies all CCP2, CCDC/SBL, histogram, H3A, preview, resizer, CSI-2, CSI PHY, and SoC control-register constants used by the implementation files.

## Important APIs, Types, And Functions
- No functions or types are defined; the file is a macro contract.
- Top-level ISP macros cover revision, sysconfig/status, IRQ enables/status, ISP control, and timing-control registers.
- CCP2 macros define sysconfig/reset, LCx IRQ/status/control/data registers, memory-channel registers, and control-bit shifts/masks.
- SBL macros define overflow flags, read/write path registers, and SDR request-expansion fields used for bandwidth throttling.
- Histogram/H3A macros define stats engine register offsets, PCR bits, window/paxel fields, histogram bin/gain/region fields, and busy bits.
- Preview/resizer macros define processing register offsets, table addresses, enable bits, format/YC position fields, matrix/offset shifts, crop size fields, and resizer filter coefficient fields.
- CSI-2/CSI PHY macros define receiver sysconfig, IRQ, control, PHY config, context registers, timing fields, PHY timing registers, and OMAP3430/3630 syscon routing bits.

## Control Flow
There is no runtime control flow. Driver C files compose these offsets and masks with `isp_reg_readl()`, `isp_reg_writel()`, `isp_reg_set()`, `isp_reg_clr()`, and `isp_reg_clr_set()` to program hardware.

## State And Persistence
The header has no state; it describes volatile hardware state. Correctness depends on these constants matching the SoC TRM and silicon revision behavior. Many modules cache desired state elsewhere and use this header to restore registers after reset or stream start.

## Dependencies And Integration Points
Every OMAP3 ISP block implementation depends on this file. It integrates with `isp.h` register access abstractions and with platform-specific syscon routing in `ispcsiphy.c`. It also encodes hardware revision differences referenced by CCP2, CSI2, and preview code.

## Risks And Edge Cases
- A typo in a shift or mask silently corrupts hardware programming; examples worth scrutiny include macros where mask definitions reuse a count shift for skip fields or where a sync-pattern mask references a non-shift macro name.
- Some macros are revision-specific, especially CSI2C and OMAP3630 PHY/control fields; using them on the wrong silicon can be invalid.
- Large groups of coefficient macros are repetitive and easy to update inconsistently.
- Because this file is included broadly, macro name collisions or semantic changes have wide blast radius.

## Test Signals
Most validation is integration-level: stream start register traces, IRQ decoding, format/crop hardware programming, histogram/H3A stats operation, PHY route/power tests, and suspend/resume context restore. Static checks comparing macros to TRM tables and targeted unit-style tests for register value composition would catch many regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispreg.h -->
