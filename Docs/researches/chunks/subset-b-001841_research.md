# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 19539-22071

## Purpose

This chunk is generated AMD DCN 3.1.4 register field metadata. It contains no executable C logic; it publishes `#define` constants for register-field bit shifts and bit masks in `dcn_3_1_4_sh_mask.h`. Consumers use the constants with the matching DCN 3.1.4 offset header to build typed register tables for AMDGPU display hardware.

The range starts inside the `HUBPREQ2_DCN_DMDATA_VM_CNTL` field set, then covers the rest of HUBP/HUBPREQ/HUBPRET/cursor/perfmon metadata for pipe instance 2, full HUBP/HUBPREQ/HUBPRET/cursor/perfmon metadata for pipe instance 3, and the beginning of DPP0 color-pipeline metadata through `CM0_CM_GAMCOR_RAMB_REGION_24_25`. It is a chunk of one large generated header, so the first and last register groups are partial.

Although the source tree path is under a local `ceph-client` mirror, this file is AMDGPU display-driver hardware metadata and is unrelated to Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this range. The public interface is the macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT`: the field lsb position within a hardware register.
- `<REGISTER>__<FIELD>_MASK`: the register bit mask for that field.
- `// addressBlock: ...` comments: generated register-database block boundaries, useful for mapping repeated display-pipe instances.

Major macro families in this chunk:

- `HUBPREQ2_*`: tail of pipe-2 HUBP request metadata. It includes display metadata VM status/clear/done fields, system aperture limits, L1 TLB control, blanking and destination timing fields, prefetch ratios, vblank/flip/nominal PTE and metadata request timing, per-line delivery, cursor request offsets, reference-to-pixel frequency conversion, DRQ limit, request-cache memory power control/status, and additional VM/PTE/meta timing fields for flip and vblank.
- `HUBPRET2_*`: pipe-2 return-side HUBP metadata. Fields describe DET buffer plane base, 3-to-2 packing disable, component crossbar routing, DMROB/PIXCDC memory power control and status, read-line control and status, and HUBPRET interrupt status/clear/mask behavior.
- `CURSOR0_2_*`: pipe-2 cursor and display metadata registers. Fields cover cursor enable/mode, request mode, magnification, pitch, chunking, address high/low, size, position, hot spot, stereo enable/mode, destination offset, cursor memory power, DMDATA address/control/QoS/status, and software DMDATA write path.
- `DC_PERFMON8_*`: pipe-2 HUBP perfmon counter control/state/value fields, including counter enable, clear, freeze, field-selection muxes, counter mode, elapsed counter, histogram mode, and low/high counter values.
- `HUBP3_*` and `HUBPREQ3_*`: full pipe-3 HUBP and request metadata for surface config, tiling, viewport, request sizing, blank/underflow/soft reset/status controls, VM page configuration, debug windows, surface pitch, VMID, primary/secondary surface and metadata addresses, DCC/TMZ surface control, flip control and interrupts, in-use/earliest-in-use addresses, expansion mode, QoS/TTU controls, DMDATA VM control, system aperture, L1 TLB, timing/prefetch/vblank/flip/nominal delivery fields, cursor request settings, and memory power control/status.
- `HUBPRET3_*`, `CURSOR0_3_*`, and `DC_PERFMON9_*`: pipe-3 equivalents of the pipe-2 return, cursor, DMDATA, and perfmon fields.
- `DPP_TOP0_*`, `CNVC_CFG0_*`, `CNVC_CUR0_*`, and `DSCL0_*`: start of DPP0 display-pipe processor metadata for DPP clock/reset/CRC/host-read control, pixel format conversion, FP bias/scale, color keying, alpha LUT, pre-dealpha/pre-CSC/pre-degamma/pre-realpha, cursor colors/scale bias, scaler coefficient RAM, scaler mode/tap/init/ratio controls, black color, update/autocal, overscan, recout/MPC size, line-buffer format/memory, DSCL memory power, and output buffer controls.
- `CM0_CM_*`: DPP0 color-management metadata. This chunk includes CM bypass/current-state controls, post-CSC and gamut-remap matrices, bias, gamcor LUT control/data/index, and large RAMA/RAMB piecewise-linear gamma-correction region tables up to `CM0_CM_GAMCOR_RAMB_REGION_24_25`.

## Control Flow

This header has no runtime control flow. Runtime code supplies the sequencing:

1. DCN 3.1.4 resource and IRQ code includes this header with `dcn_3_1_4_offset.h`.
2. Resource constructors in `display/dc/resource/dcn314/dcn314_resource.c` build register address tables from the offset header and build shift/mask tables from this header.
3. For HUBP, `hubp_shift` and `hubp_mask` are initialized with `HUBP_MASK_SH_LIST_DCN31(__SHIFT)` and `HUBP_MASK_SH_LIST_DCN31(_MASK)`. Those macro lists paste register and field names, so fields from `HUBPREQ2_*`, `HUBP3_*`, `HUBPREQ3_*`, `HUBPRET3_*`, and `CURSOR0_3_*` must match the expected instance-0 field names after token substitution.
4. For DPP, `tf_shift` and `tf_mask` are initialized with `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)` and `DPP_REG_LIST_SH_MASK_DCN30(_MASK)`, which ultimately depend on `TF_SF`/`TF2_SF` field macro expansion against `DPP_TOP0_*`, `CNVC_CFG0_*`, `DSCL0_*`, and `CM0_CM_*`.
5. Constructed objects such as `dcn20_hubp` and `dcn3_dpp` receive pointers to these tables. Runtime paths then use register helpers like `REG_UPDATE`, `REG_GET`, `REG_SET`, `REG_READ`, and `REG_WRITE` to program fields indirectly by symbolic field names.

The chunk itself does not encode modeset ordering. Correct sequencing is owned by HUBP, DPP, DML, resource, IRQ, and HW sequencing code that programs clocks, power gates, surface addresses, VM/TLB setup, prefetch timing, cursor/DMDATA updates, scaling, color transforms, LUTs, and interrupt/status handling.

## State And Persistence Behavior

This chunk stores no software state and persists nothing. It describes fields in MMIO-backed display hardware state:

- HUBP request state includes active/in-use surface addresses, flip/update-lock status, VMID/TLB/aperture programming, DCC/TMZ controls, underflow and blanking status, request sizing, VM/PTE/meta delivery timing, QoS/TTU ramping, cursor fetch settings, and memory power state.
- HUBPRET state includes buffer allocation, return-data component routing, read-line capture/status, interrupt bits, and local memory power state.
- Cursor and DMDATA state includes cursor image address/size/position/hot spot/mode, stereo controls, destination offsets, DMDATA memory address, update/repeat/size/mode, QoS, status done, and software data injection fields.
- Perfmon state includes selectable counters, counter mode, enable/clear/freeze control, histogram mode, and low/high counter values.
- DPP state includes DPP clock/reset/CRC controls, color conversion format and coefficients, scaler coefficients and ratios, line buffer format, recout/MPC dimensions, memory power state, cursor colors, and color-management LUT/control/region tables.

Persistence is hardware-defined. Many configuration fields retain values until a modeset, plane disable, power gating, suspend/resume, or ASIC reset. Status, interrupt, clear, read-line, CRC, perfmon, memory-power status, and current-state fields may be read-only, sticky, write-one-to-clear, self-clearing, or double-buffered. This generated header does not distinguish those semantics; consuming driver code must know them.

## Dependencies And Integration Points

Primary dependencies:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h` supplies matching register offsets and base-index macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c` includes this header and constructs DCN314 register/shift/mask tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn31/dcn31_hubp.h` defines `HUBP_MASK_SH_LIST_DCN31`, which consumes HUBP/HUBPREQ/HUBPRET/CURSOR field masks and shifts.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn31/dcn31_hubp.c` uses the constructed HUBP tables in functions such as `hubp31_set_unbounded_requesting`, `hubp31_soft_reset`, `hubp31_program_extended_blank_value`, and `hubp31_get_det_config_error`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp.h` and later DPP headers define `TF_SF`/`TF2_SF` and DPP mask-list macros that consume DPP0, DSCL0, CNVC0, and CM0 fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c` and `display/dc/irq/dcn314/irq_service_dcn314.c` also include the DCN 3.1.4 register headers for DMUB and interrupt mapping, though this chunk is mostly HUBP/DPP field data.

The central integration pattern is preprocessor token pasting. A field such as `HUBPREQ3_PREFETCH_SETTINGS__VRATIO_PREFETCH_MASK` is not referenced manually in most code; instead, macro lists instantiate a `struct dcn_hubp2_mask` member used by `REG_UPDATE(PREFETCH_SETTINGS, VRATIO_PREFETCH, value)` after the HUBP instance's register table maps `PREFETCH_SETTINGS` to the concrete instance-3 register.

## Risks And Edge Cases

- Shift/mask drift is the main risk. These macros are untyped constants; a bad bit position or mask can compile cleanly while writing the wrong field or silently truncating values.
- Repeated pipe instances are copy-sensitive. Instance 2 and 3 HUBP/HUBPREQ/HUBPRET/CURSOR/PERFMON blocks are structurally similar, so a single wrong suffix, field width, or cross-instance paste error may only appear when using the affected display pipe.
- Chunk boundaries are partial. The first line starts after the `DMDATA_VM_DONE__SHIFT` group has already begun, and the last line stops inside the `CM0_CM_GAMCOR_RAMB_REGION_*` table. Adjacent chunks are required for whole-file conclusions.
- VM, TLB, aperture, DCC, and TMZ fields affect memory translation and protected/display-compression surfaces. Incorrect masks can cause faults, underflow, wrong addresses, or security-sensitive surface access behavior.
- Timing and QoS fields are tightly coupled to DML calculations. Bad `REFCYC`, `DST_Y`, PTE/meta, TTU, or prefetch masks can cause underruns, late requests, flip glitches, or failures limited to high-bandwidth formats.
- Cursor and DMDATA fields are update-sensitive. Wrong address, size, status, or software-update masks can cause cursor corruption, stale DMDATA, repeated metadata, or stuck done/status polling.
- Power-control and status fields can be sequencing-sensitive around clock gating and power gating. Incorrect force/disable/status masks can leave memories powered unexpectedly or inaccessible when the display code assumes they are available.
- DPP scaler and color-management fields have visual output risk. Bad coefficient, CSC, gamut, gamma, LUT, or region masks can produce incorrect color, broken scaling, CRC mismatches, or hard-to-diagnose pipe-specific visual defects.

## Test Signals

Useful validation is mostly build-time generated-header consistency plus hardware display coverage:

- Build AMDGPU/DC with DCN314 enabled. Missing or renamed macros should fail in `dcn314_resource.c`, HUBP/DPP headers, IRQ, or DMUB code during shift/mask table initialization.
- Mechanically verify that every `__SHIFT` macro in lines 19539-22071 has a matching `_MASK` macro for the same register and field, accounting for the partial first field and partial final register group.
- Diff this chunk against AMD's authoritative DCN 3.1.4 register database and nearby DCN 3.1/3.1.5 generated headers where compatibility is expected.
- Exercise systems or emulation with four display pipes so HUBP instance 3 is actually allocated: multi-monitor modesets, plane enable/disable, flips, stereo/secondary viewport paths, cursor movement, and pipe reassignment.
- Test memory-backed display paths: DCC on/off, TMZ/protected surfaces if supported, VM faults/clears, system aperture setup, suspend/resume, page flips, and high-bandwidth modes that stress PTE/meta prefetch.
- Validate visual pipeline behavior through DPP0: scaling, color keying, pre/post CSC, gamut remap, gamma correction LUT programming, CRC capture, and format conversion for RGB and chroma surfaces.
- Watch kernel logs and display diagnostics for HUBP underflow, DMDATA VM fault/late/underflow status, stuck flip pending, stale cursor/DMDATA done bits, perfmon counter anomalies, read-line interrupt issues, color CRC mismatches, and resume failures.

## Cross-Chunk Notes

Earlier chunks own the start of the pipe-2 HUBPREQ register groups. Later chunks continue `CM0_CM_GAMCOR_RAMB_REGION_*` and then the remaining DPP color-management/register-mask namespace. The final per-file research document should merge adjacent chunks before making complete claims about all DCN 3.1.4 register fields or the full `dcn_3_1_4_sh_mask.h` generated interface.
