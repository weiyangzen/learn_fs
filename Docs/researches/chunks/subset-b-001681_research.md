# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h lines 2666-5203

## Purpose

This chunk is generated AMDGPU DCN 3.0.0 register-offset metadata. It contains no executable C logic; its public surface is a large set of preprocessor constants mapping hardware register names to MMIO register offsets and to register-base-index selectors. The paired pattern is:

- `mmREGISTER_NAME` gives the register offset, in this range from `0x077c` through `0x0f7f`.
- `mmREGISTER_NAME_BASE_IDX` gives the register aperture/base selector, consistently `2` for the chunked display-register blocks here.

The path is under a local `ceph-client` source mirror, but this file is AMD display-driver hardware metadata rather than Ceph or distributed-filesystem logic.

The range starts at the tail of `DC_PERFMON7`, covers DCN hub pipe instances 2 through 5, then covers DPP instance 0 and most of DPP instance 1. It ends at `mmCM1_CM_3DLUT_READ_WRITE_CONTROL_BASE_IDX`; later lines in the same file continue other DCN 3.0.0 generated register blocks.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or runtime objects in this chunk. The important API is the generated macro namespace consumed by AMD display register-list helpers such as `SRI(...)`, `SR(...)`, `REG_READ`, `REG_WRITE`, `REG_UPDATE`, and the DCN resource tables that bind offsets together with masks and shifts from the matching `dcn_3_0_0_sh_mask.h`.

Major macro families in this chunk:

- `DC_PERFMON7_*`, `DC_PERFMON8_*`, `DC_PERFMON9_*`, `DC_PERFMON10_*`, `DC_PERFMON11_*`, and `DC_PERFMON12_*`: display performance-counter control, state, counted value, high/low counter value, and interrupt/misc registers associated with hub pipe and DPP blocks. `DC_PERFMON7` is partial at the start of the chunk.
- `HUBP2_*` through `HUBP5_*`: hub pipe surface configuration, address and tiling configuration, primary and secondary luma/chroma viewport start and dimension registers, request-size configuration, hubp control, clock control, virtual-memory page configuration, debug registers, and DCFCLK/DPPCLK measurement-window controls.
- `HUBPREQ2_*` through `HUBPREQ5_*`: hub request programming for surface pitch, VMID, primary/secondary luma and chroma surface addresses, metadata addresses, surface control, flip control, flip interrupts, current and earliest in-use addresses, expansion modes, TTU/QoS watermarks, VM aperture, L1 TLB control, blanking/scaler/prefetch/vblank/flip/nominal timing parameters, per-line delivery, cursor TTU, cursor settings, request limits, DMDATA VM control, and memory power controls/status.
- `HUBPRET2_*` through `HUBPRET5_*`: hub return control, DET buffer plane offsets and crossbar selection, memory power control/status, read-line controls and values, read-line status, interrupt mask/type/status/ack registers, and read-line configuration.
- `CURSOR0_2_*` through `CURSOR0_5_*`: cursor control, surface address high/low, size, position, hot spot, stereo control, destination offset, cursor memory power state, and DMDATA address/control/QoS/status/software-data registers.
- `DPP_TOP0_*` and `DPP_TOP1_*`: DPP control, soft reset, and clock-control registers.
- `CNVC_CFG0_*` / `CNVC_CFG1_*` and `CNVC_CUR0_*` / `CNVC_CUR1_*`: conversion and cursor-blending front-end registers for format control, pixel format, alpha LUTs, floating-point bias/scale, color keying, pre-degamma, pre-dealpha, pre-realalpha, pre-CSC matrices for A/B banks, cursor color/control, and cursor scale/bias.
- `DSCL0_*` and `DSCL1_*`: scaler and line-buffer registers for coefficient RAM, scaler mode, tap control, replicate control, horizontal/vertical ratios and inits, black color, scaler update/autocal, overscan, OTG blanking, recout, MPC size, line-buffer data format, line-buffer memory power state, obuf power control, and DSCL memory power controls.
- `CM0_*` and `CM1_*`: color-management registers for dealpha, bias, gamma correction, gamut remap, post CSC, blend gamma, shaper LUT, HDR multiplier, coefficient format, memory power, 3D LUT access, and test/debug registers. The chunk includes both RAM A/RAM B region programming patterns for gamma correction, blend gamma, and shaper LUTs, with per-channel B/G/R start, slope, base, end, offset, and region-pair registers.

## Control Flow

This header chunk has no branches, loops, calls, or initialization sequence. It is declarative hardware address data.

Runtime control flow is in the consumers:

1. DCN 3.0 resource, IRQ, GPIO, clock-manager, and DMUB code includes `dcn_3_0_0_offset.h`.
2. Resource code expands register-list macros such as `HUBP_REG_LIST_DCN30(id)` and `DPP_REG_LIST_DCN30(id)` for instances 0 through 5. For this chunk, `id` values 2 through 5 select the hub pipe and cursor offsets, while `id` values 0 and 1 select the DPP/CNVC/DSCL/CM offsets present here.
3. Generic hubp and dpp implementations use those register tables plus matching masks/shifts to perform MMIO reads and writes during modesets, plane programming, page flips, cursor updates, color pipeline updates, clock/power transitions, diagnostics, and interrupt handling.
4. Hardware sequencing is entirely outside this header. The macros do not say when a field is writable, double-buffered, sticky, read-only, write-one-to-clear, or dependent on clocks/power being enabled.

## State And Persistence Behavior

The header stores no software state and persists nothing. It describes GPU display hardware registers that hold volatile MMIO state.

The represented hardware state includes:

- Plane fetch state: surface format, alpha plane enable, tiling/swizzle/address-bank configuration, viewport geometry, luma/chroma pitch, primary/secondary surface addresses, metadata addresses, DCC/protection-related surface control, VMID, and current/earliest in-use addresses.
- Flip and timing state: surface flip control, flip interrupt status/ack paths, blanking and scaler destination parameters, prefetch settings, vblank/flip/nominal PTE and meta-row timing parameters, per-line delivery timing, and request expansion limits.
- VM and memory-system state: VM aperture bounds, L1 TLB control, DMDATA VM control, TTU/QoS watermarks, DRQ limits, request-size config, memory power controls/status, DET buffer state, and hub return read-line/underflow interrupts.
- Cursor and metadata state: cursor enable/mode/pitch, address, size, position, hot spot, stereo state, destination offset, cursor memory power, and DMDATA buffer address/control/QoS/status/software fields.
- DPP image-processing state: pixel format conversion, alpha handling, pre-degamma, color keying, pre-CSC, DSCL ratios/taps/line-buffer settings, color-management gamma/gamut/post-CSC/blend-gamma/shaper/3D-LUT state, HDR multiplier, and memory power status.
- Diagnostics and performance state: perfmon counter control/value registers, debug DB registers, test/debug index/data registers, clock measurement-window controls, read-line status, underflow status, and interrupt status/ack registers.

Persistence is determined by hardware behavior and driver sequencing outside the header. Configuration values usually remain until the next plane update, color update, modeset, power-gating transition, suspend/resume, or ASIC reset. Status and interrupt registers may be sticky, self-clearing, snapshot-like, or read-only. Names containing `*_STATUS`, `*_ACK`, `*_CLEAR`, `*_PENDING`, `*_INUSE`, `*_MEM_PWR_STATUS`, `*_READ_LINE_STATUS`, or `*_UNDERFLOW*` should be treated as side-effect-sensitive by consumers.

## Dependencies And Integration Points

This offset header is paired with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h`, which provides the field shifts and masks for these register offsets.

Direct include points found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`

The closest register-table consumers are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`, which instantiates six `hubp_regs` entries with `HUBP_REG_LIST_DCN30(id)` and six `dpp_regs` entries with `DPP_REG_LIST_DCN30(id)`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn30/dcn30_hubp.h`, which layers DCN 3.0 hubp registers over DCN 2.1 hubp lists and adds `HUBPREQ*_DCN_DMDATA_VM_CNTL`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.h`, which uses `SRI(..., id)` to bind the DPP_TOP, CNVC_CFG, CNVC_CUR, DSCL, CURSOR0, and CM register names represented here.

The same generated offsets are also mirrored across nearby DCN 3.0.x offset headers such as `dcn_3_0_1_offset.h`, `dcn_3_0_2_offset.h`, and `dcn_3_0_3_offset.h`, making this chunk part of an ASIC-family hardware contract rather than isolated application logic.

## Risks And Edge Cases

- These macros are a hardware ABI. A wrong offset or base index will compile cleanly but can write the wrong MMIO register, producing blank scanout, corrupt planes, stuck flips, broken cursor state, incorrect color output, clock/power failures, or interrupt storms.
- Repeated instance blocks create drift risk. `HUBP2` through `HUBP5`, `HUBPREQ2` through `HUBPREQ5`, `HUBPRET2` through `HUBPRET5`, and `CURSOR0_2` through `CURSOR0_5` are mostly cloned with fixed instance stride. A single stale macro can fail only when enough displays or planes are active to use the affected pipe.
- DPP blocks are similarly repeated but this chunk ends partway through DPP instance 1. Whole-file research must merge later chunks before making complete claims about `CM1` or later DPP/display blocks.
- Surface and metadata address registers are split across low/high, luma/chroma, primary/secondary, and metadata variants. Mixing these offsets can scan out stale or wrong memory, break multi-plane formats, corrupt compressed surfaces, or trigger VM faults.
- Flip, interrupt, status, and clear/ack registers have side effects not represented in an offset header. Full-register writes or reads in the wrong sequence can lose an event, clear a pending flip, miss an underflow, or leave an interrupt asserted.
- QoS, prefetch, TTU, per-line delivery, DRQ, and timing registers are workload-sensitive. Offset mistakes may appear only under high resolution, high refresh, scaling, multiple planes, low memory clocks, or cursor-heavy workloads.
- Color pipeline registers include indexed LUTs, RAM A/B banks, per-channel start/end/slope/base fields, region pairs, and 3D-LUT data/control registers. Wrong offsets can cause subtle color errors that pass basic modeset testing but fail gamma, gamut, HDR, or color-management validation.
- Memory power and clock-control registers require sequencing with the DC power-management paths. Accesses while a block is gated or memories are powered down can return stale values or drop writes.

## Test Signals

Useful validation is a mix of compile-time table coverage and DCN 3.0 hardware behavior:

- Build AMDGPU/DC with DCN 3.0 support; missing or renamed macros should fail in `dcn30_resource.c`, hubp, dpp, IRQ, GPIO, clock-manager, or DMUB include paths.
- Diff this generated range against the authoritative AMD register database and sibling DCN 3.0.x headers, especially for instance stride consistency across hub pipe instances 2 through 5 and DPP instances 0 through 1.
- Exercise DCN 3.0 hardware with enough active pipes to use HUBP/CURSOR instances 2, 3, 4, and 5. Validate modesets, plane enable/disable, page flips, cursor movement, cursor size/format changes, hotplug, DPMS, suspend/resume, and multi-monitor layouts.
- Test RGB and YUV formats, luma/chroma plane programming, primary and secondary surfaces, metadata/DCC surfaces, protected/TMZ-capable paths where applicable, and VM fault reporting for bad surface addresses.
- Stress flip and timing paths: immediate flips, vblank-synchronized flips, flip interrupts, flip-away handling, triple-buffer-like paths, prefetch timing, low memory clock, high refresh, scaling, and multi-plane composition.
- Validate DSCL and DPP color behavior with scaling ratios, scaler taps, overscan, pre-CSC, pre-degamma, gamma correction, gamut remap, post CSC, blend gamma, shaper LUT, HDR multiplier, and 3D LUT programming.
- Use perfmon/debug tooling to start/stop the affected `DC_PERFMON*` counters, read high/low values, and check interrupt/status/ack behavior.
- Watch kernel logs and display diagnostics for hubp underflow, VM faults, DCC errors, missed flips, IRQ storms, cursor corruption, color regressions, power-gating resume failures, and pipe-specific failures.

## Cross-Chunk Notes

The first lines of this chunk are only the tail of the `DC_PERFMON7` offset block. The chunk also stops immediately after `CM1_CM_3DLUT_READ_WRITE_CONTROL_BASE_IDX`, so DPP instance 1 and the rest of the generated DCN 3.0.0 offset namespace continue in later chunks. The final per-file research document should reconcile adjacent chunks before presenting complete file-level coverage.
