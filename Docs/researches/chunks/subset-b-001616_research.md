# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 14827-17349

## Purpose

This chunk is part of AMDGPU's generated DCN 2.0 register field mask header. It contains no executable C code; it publishes preprocessor constants that describe bit shifts and already-positioned bit masks for hardware registers in one late HUBP5 pipe and the beginning of DPP0/color-management register space.

The range starts at the tail of the `HUBP5_DCHUBP_CNTL` field definitions, then covers address blocks for the fifth hub pipe request path and its companion cursor/performance/XFC logic:

- `HUBP5` clock, blanking, disable, timeout, underflow, virtual-memory page, request-debug, and DCFCLK/DPPCLK measurement-window controls.
- `HUBPREQ5` surface pitch, VMID, primary/secondary luma/chroma surface addresses, primary/secondary metadata addresses, DCC/TMZ surface control, flip control, flip interrupts, current/earliest in-use addresses, TTU/QoS controls, VM aperture and context0 page-table fields, prefetch/vblank/flip/nominal timing parameters, cursor request settings, and HUBPREQ memory power controls.
- `HUBPRET5` return-path controls, memory power state, read-line configuration/readback, and interrupt fields.
- `CURSOR0_5` cursor surface, size, position, hot spot, stereo, memory power, and display metadata (`DMDATA`) fields.
- `DC_PERFMON12` perf-counter and perf-monitor control, state, interrupt/misc status, and counter value fields for the HUBP performance monitor slice.
- `HUBPXFC5` crossbar/frame-cache style control, XBUF read-base addresses, delay, underflow, slave VTG/scaler, and MPC configuration fields.

The second half switches to `DPP0` and related display pixel processor blocks:

- `DPP_TOP0` top-level DPP control, soft reset, CRC value/control, and host-read control.
- `CNVC_CFG0` and `CNVC_CUR0` input format conversion, alpha expansion, color keying, 2-bit alpha LUT, and cursor conversion fields.
- `DSCL0` scaler coefficient RAM, mode/tap controls, ratios, initial phases, recout/MPC dimensions, line-buffer configuration, autocalculation, overscan, memory power, output-buffer control, and OTG blanking pass-through fields.
- `CM0` color-management control, input CSC and gamut-remap matrices, biases, degamma LUT/RAM A/RAM B, blend-gamma LUT/RAM A/RAM B, HDR multiplier, CM memory power, de-alpha, coefficient format, and the start of shaper LUT/RAM A/RAM B region programming.

Each field is represented by `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros. Driver code pairs these values with register addresses from `dcn_2_0_0_offset.h` and uses generated register-helper tables to pack, update, and extract individual fields.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or persistent software objects in this chunk. The API surface is the generated macro namespace consumed by DCN component register tables.

The `HUBP5_DCHUBP_CNTL` fields expose blank enable, outstanding-request and disable status, VTG selection, TTU disable/mode, XRQ outstanding request status, timeout status/threshold/clear/interrupt enable, and underflow status/clear. `HUBP5_HUBP_CLK_CNTL` adds clock enable, clock-gating disable bits, live clock-on bits, and test clock selection. `HUBP5_HUBP_MEASURE_WIN_CTRL_DCFCLK` and `HUBP5_HUBP_MEASURE_WIN_CTRL_DPPCLK` define measurement-window enable, period, event start/stop selectors, mode/source selection, and perfmon integration fields.

The `HUBPREQ5_DCSURF_*` families define the plane fetch contract for a surface attached to HUBP5. They include luma/chroma pitch and metadata pitch, VMID selection, low/high 48-bit-style surface addresses for primary/secondary luma/chroma planes, low/high metadata addresses, DCC enable and 64-byte block indication bits, Trusted Memory Zone bits for surface and metadata, surface update locking, flip type, stereo flip mode, pending status, pending delay, minimum pending time, GSL enable/mask, triple buffering, queue control, frame pacing, and flip interrupt enable/status/clear fields.

The `HUBPREQ5_DCN_*`, `DC_VM_*`, and timing-parameter families cover memory request scheduling and translation. They describe TTU QoS watermarking, global TTU enable/disable, per-surface and per-cursor TTU min/max QoS and deadline values, VM system aperture low/high/default addresses, context0 protection-fault default and fault address fields, context0 page-table base/start/end fields, VM context enable/depth/range/protection-fault behavior, L1 TLB controls, blank offsets, destination dimensions, prefetch values, vblank delivery parameters, flip delivery parameters, nominal delivery parameters, per-line delivery parameters, reference-frequency-to-pixel-frequency conversion, and DRQ limit fields.

`HUBPREQ5_HUBPREQ_MEM_PWR_CTRL` and `HUBPREQ5_HUBPREQ_MEM_PWR_STATUS` expose request-side SRAM/LUT memory power-down, light-sleep, force, and state reporting bits. `HUBPRET5_HUBPRET_MEM_PWR_CTRL` and `HUBPRET5_HUBPRET_MEM_PWR_STATUS` do the same for the return path, while `HUBPRET5_HUBPRET_INTERRUPT` covers read-line/zero-delta interrupt enable, status, clear, and current-read-line event bits.

The `CURSOR0_5_*` fields define cursor mode, expansion mode, pitch, line chunking, enable, 2x magnification, address, size, position, hot spot, stereo force/shift/invert, cursor destination offset, cursor memory power, and DMData address, mode, repeat, size, QoS, done, software update, and software data fields.

`DC_PERFMON12_*` fields expose a DC performance counter/monitor programming surface: counter enable/reset, counter source select, clear, end-of-period behavior, state selection, test debug fields, stop/restart manual control, mode, auto start/stop, watermark selectors, event/occurrence/status/clear bits, and high/low counter value registers.

The `HUBPXFC5_*` fields describe XFC enable/format/swap controls, XBUF base addresses and pitch, refcycle/pipeline/slave-delay settings, underflow status/clear/force/interrupt bits, slave VTG totals/blanking, slave scaler recout dimensions, and MPC line timing.

`DPP_TOP0_*`, `CNVC_*`, and `DSCL0_*` fields are the front end of the DPP processing pipe. They include DPP enable/clock/reset/CRC controls; input surface pixel format, clamping, alpha, output floating-point selection, expansion mode, and color key ranges; scaler RAM tap selection/data, mode, tap counts, 2-tap controls, manual replication, horizontal/vertical ratios and init phases for luma/chroma/bottom fields, black offset, update/autocal controls, recout and MPC sizes, line-buffer format/memory, memory power state, and output-buffer bypass/clock-gate controls.

The `CM0_CM_*` fields define color pipeline programming. Matrix registers provide A/B banks for input CSC and gamut remap. LUT families include degamma, blend gamma, and shaper index/data/write-enable controls plus RAM A/RAM B piecewise-linear regions, start/end bases, slopes, per-channel B/G/R values, LUT offsets, and segment counts. The chunk ends in the middle of `CM0_CM_SHAPER_RAMB_REGION_10_11`: it includes the region comment and three shift macros, while the fourth shift and the corresponding masks continue at line 17350 in the next chunk.

## Control Flow

This chunk has no runtime control flow. It is preprocessor metadata used by DCN register helper code.

A typical runtime path is:

1. DCN 2.0 resource construction includes `dcn_2_0_0_offset.h` and `dcn_2_0_0_sh_mask.h`.
2. Resource tables populate per-component register, shift, and mask structures, such as `dcn_hubp2_registers`, `dcn_hubp2_shift`, `dcn_hubp2_mask`, `dcn2_dpp_shift`, and `dcn2_dpp_mask`.
3. Component code references logical field names through helper macros such as `HUBP_SF`, `TF_SF`, `IPP_SF`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and multi-field variants.
4. Those helpers use the shift/mask constants from this header to modify hardware registers for plane programming, flips, VM/TLB setup, cursor metadata, scaling, color conversion, gamma/shaper LUTs, CRC/perfmon diagnostics, interrupts, and power management.

The control-sensitive operations represented here include arming and observing page flips, locking surface updates, enabling or clearing flip and underflow interrupts, programming VM page-table/aperture behavior, controlling HUBP blanking/disable and TTU request scheduling, setting scaler coefficients and dimensions, choosing input conversion/color-management modes, writing gamma and shaper LUT entries, collecting DPP CRC/perf counters, and forcing or observing memory power states. The macros themselves do not encode ordering, access type, double-buffer timing, or legal value ranges.

## State And Persistence Behavior

The header stores no software state. It describes state held in DCN hardware registers.

The represented hardware state includes:

- Latched plane-fetch state: surface addresses, metadata addresses, pitch, VMID, DCC/TMZ attributes, surface queue configuration, current and earliest in-use addresses, flip lock/pending/delay state, triple-buffer and GSL state, and frame pacing.
- Request scheduling and VM state: TTU/QoS watermarks, per-surface and per-cursor QoS/deadline values, aperture/default/protection-fault addresses, page-table base/start/end, context0 control, L1 TLB configuration, prefetch/vblank/flip/nominal delivery budgets, and DRQ limits.
- Cursor and metadata state: cursor image address, dimensions, position, hot spot, stereo behavior, enable/mode bits, cursor memory power state, and DMData transport/software override state.
- Diagnostic and event state: HUBP underflow/timeout bits, flip interrupt status, HUBPRET read-line interrupt state, XFC underflow bits, perf counter state/value/status, DPP CRC controls and results, live clock-on bits, read-line values, and debug registers.
- Pixel-processing state: DPP reset/enable, input format and color keying, scaler coefficients and ratios, recout/MPC/line-buffer configuration, color matrices, degamma/blend/shaper LUTs and RAM regions, HDR multiplier, de-alpha, coefficient format, and CM/DSCL memory power state.

Persistence is hardware-defined. Programming fields generally persist while the display engine remains powered and configured; many values are reloaded during modeset, plane update, power-gating exit, suspend/resume, or ASIC reset. Status, interrupt, pending, underflow, timeout, done, and clear fields may be live read-only, sticky write-one-to-clear, self-clearing, or latched on a double-buffer boundary. This generated header does not distinguish those access classes, so consumers must rely on hardware sequencing code and register documentation.

## Dependencies And Integration Points

This chunk depends on the generated DCN 2.0 register-header set. `dcn_2_0_0_sh_mask.h` supplies bit layouts; `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h` supplies the matching register addresses.

Direct include points for the DCN 2.0 offset and mask headers include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`

The HUBP fields integrate most directly with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`, where six `hubp_regs` instances are built and shared `hubp_shift`/`hubp_mask` tables are initialized. The functional users are under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/`, especially the DCN10/DCN20-style HUBP code that programs surfaces, flips, VM, cursors, blanking, and underflow handling through `dcn_hubp2` register tables.

The DPP, CNVC, DSCL, and CM fields integrate with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp.h` and `dcn20_dpp.c`, where `TF_SF` maps these field constants into `dcn2_dpp_shift` and `dcn2_dpp_mask`. Shared DPP code uses them for scaling, input CSC, gamut remap, degamma, blend gamma, shaper LUTs, DPP CRC, and memory power control. `CNVC_CFG0`/`CNVC_CUR0` fields are also part of the input pixel processor naming used from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_ipp.h`.

IRQ integration includes the HUBP5 flip interrupt source in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c` and later-generation IRQ services that retain the `HUBP5_FLIP_INTERRUPT` source ID naming. Diagnostic integration includes DPP CRC register tables in HW sequencer/resource code and DC perfmon fields consumed by debug/performance tooling.

Although the repository path is under a local `ceph-client` tree, this file is AMDGPU display-controller hardware metadata. It has no Ceph protocol, filesystem, or distributed-storage behavior.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A wrong shift or mask can compile cleanly while updating the wrong bits, failing to update intended bits, or corrupting adjacent fields during read/modify/write operations.

High-risk HUBP/HUBPREQ fields include surface address high/low words, metadata address high/low words, pitch and metadata pitch, VMID, DCC/TMZ controls, flip pending/lock/mode/status, triple-buffer and GSL bits, TTU/QoS deadlines, VM aperture/page-table/protection-fault controls, L1 TLB configuration, vblank/flip/prefetch delivery timing, and underflow/timeout clear bits. Mistakes here can cause memory faults, secure-surface exposure, wrong frame fetches, stale page flips, missed flip interrupts, underflows, display corruption, hangs during modeset, or page-table faults isolated to one pipe.

High-risk DPP/DSCL/CM fields include scaler tap/phase/ratio values, coefficient RAM indexing/data enable bits, line-buffer memory config, recout/MPC dimensions, CNVC format/alpha expansion, CSC and gamut matrices, gamma/shaper LUT index/data/write-enable bits, RAM region offsets/segment counts, memory power force/state fields, DPP reset/enable, and CRC controls. Errors here can cause incorrect colors, broken HDR/gamma output, bad scaling, clipped or shifted images, CRC mismatches, blank output, or power-management failures.

Generated instance suffixes are a copy-generation risk. This chunk is specific to HUBP instance 5 and DPP instance 0; most register layouts are structurally similar to other instances, but a wrong `5`, `12`, or `0` suffix can affect only systems using the affected pipe or diagnostic counter.

Several fields represent status, interrupt clear, event force, memory power state, or self-clearing trigger bits. The header does not encode read-only/write-one-to-clear semantics. Consumers must avoid treating status bits as ordinary writable state or clearing sticky events while enabling interrupts.

The line range begins after the `HUBP5_DCHUBP_CNTL__HUBP_TIMEOUT_STATUS_MASK` macro was already emitted in the previous chunk, so this chunk contains the remaining `HUBP5_DCHUBP_CNTL` masks before `HUBP5_HUBP_CLK_CNTL`. It also ends mid-register in `CM0_CM_SHAPER_RAMB_REGION_10_11`, before the `REGION11_NUM_SEGMENTS` shift and all masks for that register. The final merged per-file report should treat both as chunk boundaries, not missing definitions.

## Test Signals

Useful validation signals are compile-time generated-header checks plus display hardware behavior:

- AMDGPU/DCN 2.0 builds should compile all users of `dcn_2_0_0_sh_mask.h`, especially DCN20 resource, IRQ, GPIO, clock-manager, DMUB, GMC, HUBP, IPP, and DPP code.
- Register-generation validation should compare every `*_MASK` and `*__SHIFT` pair in this chunk against AMD's source register database and the corresponding addresses in `dcn_2_0_0_offset.h`.
- Multi-pipe modeset and plane-update tests should exercise HUBP5 specifically, including primary/secondary planes, DCC-enabled surfaces, metadata surfaces, TMZ surfaces, cursor planes, page flips, triple buffering, and GSL-enabled flips.
- VM/IOMMU tests should validate VMID, aperture, page-table, protection-fault, L1 TLB, and default-address behavior under valid mappings, invalid mappings, suspend/resume, and repeated modesets.
- Flip IRQ and event tests should check `HUBP5` flip pending/status/clear, underflow clear/status, timeout status/clear, HUBPRET read-line interrupts, and XFC underflow interrupt behavior.
- Bandwidth and timing tests should observe stable TTU/QoS, prefetch, vblank, flip, nominal, per-line, DRQ, and frame-pacing behavior across high-resolution, high-refresh, chroma, DCC, and cursor-heavy workloads.
- DPP tests should verify input format conversion, alpha/keying, scaler ratios/coefs, recout/MPC dimensions, line-buffer configuration, DPP CRC output, and DSCL/CM memory power state transitions.
- Color-management tests should exercise input CSC, gamut remap, degamma, blend gamma, HDR multiplier, de-alpha, coefficient formats, shaper LUT programming, RAM A/B bank selection, and region offset/segment programming.
- Runtime power-management, suspend/resume, hotplug, and repeated atomic update stress should not leave HUBP/DPP memory power forced incorrectly, clocks gated unexpectedly, update locks stuck, interrupts uncleared, or LUT banks partially programmed.

Regression symptoms from bad constants include blank or unstable display output, page flips that never complete, missed vblank/flip interrupts, GPU VM faults during scanout, HUBP underflows or timeouts, incorrect cursor position or metadata transport, XFC underflows, wrong scaling, bad colors/HDR/gamma, CRC mismatches, and failures isolated to HUBP5 or DPP0.

## Cross-Chunk Notes

Earlier chunks define preceding DCN 2.0 register families and the beginning of the HUBP5/HUBPREQ5 sequence, including the first part of `HUBP5_DCHUBP_CNTL`. This chunk continues through the remaining HUBP5/HUBPREQ5/HUBPRET5/CURSOR0_5/perfmon/XFC fields and then covers DPP0/CNVC/DSCL/CM0 through the start of `CM0_CM_SHAPER_RAMB_REGION_10_11`. The next chunk continues that shaper RAMB register and the remaining color-management/output-pixel-processing register mask definitions. The final per-file merge should describe the whole header as a generated DCN 2.0 hardware register layout contract, not as algorithmic code.
