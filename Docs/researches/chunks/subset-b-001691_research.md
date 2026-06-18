# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 9805-12287

## Scope

This chunk is generated AMD DCN 3.0.0 register field metadata. It contains 2,112 `#define` entries in the visible range: 1,054 `__SHIFT` constants and 1,058 `_MASK` constants. There are no C functions, structs, enums, variables, or executable branches in this file slice; its API is the generated preprocessor namespace that maps display-controller register fields to bit positions and already-shifted bit masks.

The path is under a local `ceph-client` source mirror, but this source is AMDGPU display hardware metadata, not Ceph or distributed filesystem logic.

The chunk starts inside the `DC_PERFMON6_PERFCOUNTER_CNTL` register definition, after earlier fields from that register have already appeared in the previous chunk. It then covers:

- The remainder of `DC_PERFMON6_*` perfmon control/state/value fields.
- HUBP/HUBPREQ/HUBPRET/CURSOR instance 1 field masks and shifts.
- Complete `DC_PERFMON7_*` definitions.
- HUBP/HUBPREQ/HUBPRET/CURSOR instance 2 field masks and shifts.
- Complete `DC_PERFMON8_*` definitions.
- HUBP instance 3 and the first part of HUBPREQ instance 3, ending at `HUBPREQ3_BLANK_OFFSET_0__REFCYC_H_BLANK_END_MASK`.

Because the first and last register families are partial, whole-file conclusions for `DC_PERFMON6_PERFCOUNTER_CNTL` and `HUBPREQ3` must be reconciled with adjacent chunks.

## Purpose

The purpose of this header range is to let AMD display code program DCN 3.0.0 hardware registers symbolically. Each field is represented by a pair:

- `REGISTER__FIELD__SHIFT`: the field's least-significant bit position.
- `REGISTER__FIELD_MASK`: the field's already-positioned register mask.

Runtime code combines these constants with the matching generated address header, `dcn_3_0_0_offset.h`, and AMD display register helpers such as `REG_SET`, `REG_SET_2`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, `SRI(...)`, and `HUBP_SF(...)`. The constants in this chunk are therefore part of the DCN 3.0.0 register ABI used by plane programming, page flips, cursor programming, VM/TLB setup, memory power control, interrupt handling, and display performance monitoring.

## Important API Surface

The major macro groups are:

- `DC_PERFMON6_*`, `DC_PERFMON7_*`, and `DC_PERFMON8_*`: display performance counter control and status fields. These include event selection, counted-value selection, increment mode, hardware control selection, run enable mode, count-off and restart controls, interrupt enable/status/ack fields, counter active/state fields for counters 0-7, global perfmon state/report count, clock/run-enable controls, counter value low/high fields, and read selector fields.
- `HUBP1_*`, `HUBP2_*`, and `HUBP3_*`: hub pipe surface metadata. These define surface pixel format, rotation, horizontal mirror, alpha plane enable, address configuration, tiling/swizzle mode, primary and secondary viewport start/dimensions for luma and chroma planes, request size programming, HUBP blank/disable/underflow state, clock control, virtual memory page config, and DCFCLK/DPPCLK measurement-window fields.
- `HUBPREQ1_*`, `HUBPREQ2_*`, and visible `HUBPREQ3_*`: hub request path fields for scanout memory fetches. These include luma/chroma pitch, VMID, primary and secondary surface addresses, metadata addresses, DCC and TMZ controls, flip control, flip interrupts, in-use and earliest-in-use address reporting, expansion mode, TTU/QoS programming, VM aperture and L1 TLB controls, blanking/scaler/prefetch timing, vblank and flip timing, nominal PTE/meta-row timing, per-line delivery, cursor request settings, reference-frequency conversion, destination-Y request limits, and request-side memory power control/status.
- `HUBPRET1_*` and `HUBPRET2_*`: hub return path fields for DET buffer plane base addresses, component crossbar selection, pack control, return memory power control/status, read-line control/value/status, and HUBPRET interrupt mask/type/status/ack fields.
- `CURSOR0_1_*` and `CURSOR0_2_*`: cursor and display metadata fields for cursor enable/mode/pitch, magnification, line chunking, alpha and color controls, cursor surface address, size, position, hot spot, stereo control, destination offset, cursor memory power state, DMDATA address, DMDATA mode/update/repeat/size, QoS control, completion/error status, and software DMDATA writes.

Important examples include:

- `HUBP1_DCSURF_SURFACE_CONFIG__SURFACE_PIXEL_FORMAT__SHIFT` / `_MASK`, `HUBP2_DCSURF_TILING_CONFIG__SW_MODE__SHIFT` / `_MASK`, and `HUBP3_DCSURF_ADDR_CONFIG__NUM_PKRS__SHIFT` / `_MASK` for plane format, tiling, and address layout.
- `HUBPREQ1_DCSURF_PRIMARY_SURFACE_ADDRESS*`, `HUBPREQ2_DCSURF_PRIMARY_META_SURFACE_ADDRESS*`, and matching `_C` chroma macros for split low/high luma, chroma, and metadata addresses.
- `HUBPREQ*_DCSURF_SURFACE_CONTROL__PRIMARY_SURFACE_DCC_EN`, `*_SECONDARY_SURFACE_DCC_EN`, `*_TMZ`, and metadata TMZ fields for compressed and trusted-memory scanout behavior.
- `HUBPREQ*_DCSURF_FLIP_CONTROL`, `HUBPREQ*_DCSURF_FLIP_CONTROL2`, and `HUBPREQ*_DCSURF_SURFACE_FLIP_INTERRUPT` for update locking, flip type, stereo sync, pending status, GSL, triple buffering, interrupt mask/type/status, and clear fields.
- `HUBPREQ*_DCN_DMDATA_VM_CNTL`, `HUBPREQ*_DCN_VM_SYSTEM_APERTURE_*`, and `HUBPREQ*_DCN_VM_MX_L1_TLB_CNTL` for DMDATA VM timing/status and display VM/TLB setup.
- `CURSOR0_*_DMDATA_*` for metadata packet programming attached to a cursor/plane pipe.

## Control Flow

There is no local control flow. The chunk is declarative register-layout data used by external driver code.

The runtime flow that consumes these constants is:

1. DCN 3.0 resource and block constructors include `dcn_3_0_0_offset.h` and `dcn_3_0_0_sh_mask.h`.
2. Register-list macros such as `HUBP_REG_LIST_DCN30(id)` bind per-instance MMIO addresses with generated symbols like `HUBP1_*`, `HUBPREQ1_*`, `HUBPRET1_*`, and `CURSOR0_1_*`.
3. Mask/shift table macros such as `HUBP_MASK_SH_LIST_DCN30(__SHIFT)` and `HUBP_MASK_SH_LIST_DCN30(_MASK)` paste register and field names through `HUBP_SF(...)` into `struct dcn_hubp2_shift` and `struct dcn_hubp2_mask`.
4. HUBP runtime code programs VM apertures, TLB controls, surface addresses, metadata addresses, DCC/TMZ bits, flip type, stereo flip state, cursor state, and timing/QoS controls with `REG_SET*` and `REG_UPDATE*` helpers.
5. IRQ service code builds page-flip interrupt entries with `SRI(HUBPREQ, id, DCSURF_SURFACE_FLIP_INTERRUPT)` and generated `SURFACE_FLIP_INT_MASK` / `SURFACE_FLIP_CLEAR` fields.
6. DMUB, resource, GPIO, clock manager, and IRQ paths include the same generated mask/offset pair so firmware-facing and display-manager paths use one register contract.

The generated masks do not encode sequencing. Consumers must still enforce hardware ordering, for example writing address high words before low words for latching, using surface update locks correctly, enabling clocks before MMIO access, and acknowledging sticky interrupt/status bits in the required manner.

## State And Persistence Behavior

The header itself stores no software state and persists nothing. It describes MMIO-backed GPU display state.

Hardware state represented by this chunk includes:

- Plane interpretation state: pixel format, alpha plane enable, rotation, mirror, tiling mode, address configuration, viewport coordinates, viewport dimensions, request size, and swath/PTE/meta chunk sizing.
- Scanout memory state: luma and chroma primary/secondary surface addresses, metadata surface addresses, address high words, VMID, VM system aperture, L1 TLB enable and access mode, and in-use/earliest-in-use address snapshots.
- Compression and protection state: DCC enable, independent block sizing, TMZ bits for primary/secondary and metadata surfaces, including chroma variants.
- Flip and update state: surface update lock, flip type, pending status, stereo sync mode, GSL enable, triple buffering, pending delay/min-time, and flip/flip-away interrupt mask/type/status/clear bits.
- Request timing and QoS state: TTU watermarks, fixed QoS levels, QoS ramp disable, vblank timing, flip timing, nominal PTE/meta timing, prefetch settings, per-line delivery values, reference-frequency-to-pixel-frequency conversion, blank offsets, scaler output timing, and destination-Y DRQ limits.
- Power and clock state: HUBP clock enable/disable fields, HUBPREQ/HUBPRET/CURSOR memory power force/disable/status fields, virtual memory page config, and measurement-window clock counters.
- Cursor and DMDATA state: cursor control, surface address, size, position, hot spot, stereo control, destination offset, DMDATA address/control/QoS/status/software-update fields.
- Diagnostics and profiling state: underflow/status bits, read-line values, HUBPRET interrupts, perfmon counter values and counter state, perfmon interrupt status and ack bits, and clock measurement-window counters.

Persistence is hardware-defined. Configuration fields usually remain programmed until a plane update, modeset, suspend/resume, power-gating transition, or GPU reset. Status and interrupt fields may be read-only, sticky, write-one-to-clear, self-clearing, or side-effect-sensitive. Names such as `*_STATUS`, `*_ACK`, `*_CLEAR`, `*_PENDING`, `*_INUSE`, `*_UNDERFLOW_CLEAR`, `*_MEM_PWR_STATUS`, and `*_CLOCK_ENABLE` should be treated as side-effect-sensitive unless the consuming code or hardware specification proves otherwise.

## Dependencies And Integration Points

This chunk depends on the matching generated address header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`

Observed include points for the DCN 3.0.0 offset/mask pair include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c`

The closest structural integration is `display/dc/hubp/dcn30/dcn30_hubp.h`, where `HUBP_MASK_SH_LIST_DCN30(mask_sh)` references fields in this chunk through `HUBP_SF(...)`: surface config, tiling, pitch, flip control, viewport, surface and metadata addresses, DCC/TMZ, flip interrupt, HUBPRET control, expansion mode, request sizing, blanking, prefetch, vblank/flip/nominal timing, TTU/QoS, cursor, DMDATA, VM aperture, and L1 TLB fields.

`display/dc/resource/dcn30/dcn30_resource.c` instantiates `hubp_shift` and `hubp_mask` from `HUBP_MASK_SH_LIST_DCN30(__SHIFT)` and `HUBP_MASK_SH_LIST_DCN30(_MASK)`, then passes them to `hubp3_construct(...)`. `display/dc/hubp/dcn30/dcn30_hubp.c` uses the resulting register tables in functions such as `hubp3_set_vm_system_aperture_settings(...)` and `hubp3_program_surface_flip_and_addr(...)`. `display/dc/irq/dcn30/irq_service_dcn30.c` maps page-flip IRQ sources to `HUBPREQ` `DCSURF_SURFACE_FLIP_INTERRUPT` fields.

## Risks And Edge Cases

- These constants are hardware ABI, not ordinary compile-time conveniences. A wrong mask or shift can compile cleanly while programming the wrong bits, causing blank planes, corrupted scanout, bad cursor placement, missed flips, VM faults, underflow, or pipe-specific failures.
- Repeated instance blocks are high drift risk. `HUBP1`, `HUBP2`, and `HUBP3`, `HUBPREQ1`, `HUBPREQ2`, and partial `HUBPREQ3`, `HUBPRET1/2`, `CURSOR0_1/2`, and `DC_PERFMON7/8` are highly similar. Copying one field width or mask from the wrong instance can affect only one active pipe.
- The chunk starts and ends mid-family. The leading `DC_PERFMON6_PERFCOUNTER_CNTL` fields are incomplete here, and `HUBPREQ3` stops after the first `BLANK_OFFSET_0` mask. Adjacent chunks must be consulted before claiming full coverage for those families.
- Packed control/status registers require read-modify-write discipline. Surface control, flip control, interrupt, memory power, VM/TLB, cursor control, and DMDATA control registers contain unrelated fields in one word; full-register writes can corrupt neighboring state.
- Address programming is order-sensitive. DCN HUBP code documents that high address registers must be programmed before low address registers because the low write can latch the address set. Bad masks for low/high, chroma, metadata, or primary/secondary fields can scan out stale or unintended memory.
- Interrupt and sticky status bits can have write-one-to-clear or self-clearing behavior. Misusing `SURFACE_FLIP_CLEAR`, `SURFACE_FLIP_AWAY_CLEAR`, perfmon ack bits, HUBPRET interrupt ack bits, or underflow clear bits can miss events or create interrupt storms.
- DCC and TMZ fields interact with compression and memory protection. A stale or misplaced `*_DCC_EN`, `*_DCC_IND_BLK`, or `*_TMZ` mask can cause decompression artifacts, memory-security policy violations, or failures limited to protected/compressed surfaces.
- TTU, prefetch, vblank, flip, nominal, and per-line delivery fields are workload-sensitive. Bad masks may only fail at high resolution, high refresh, low memory clock, multi-plane, scaling, cursor-heavy, or DCC-enabled workloads.
- Power and clock fields have sequencing dependencies outside this header. Accessing HUBP/HUBPREQ/HUBPRET/CURSOR registers while clock or memory domains are disabled can produce stale reads or dropped writes.
- Perfmon fields are diagnostic but still side-effect-sensitive. Wrong counter select, interrupt, restart, active, or read selector masks can make profiling misleading or leave perfmon interrupts uncleared.

## Test Signals

Useful validation signals for this range include:

- Build AMDGPU/DC with DCN 3.0.0 support enabled. Missing or renamed macros should fail at `dcn30_resource.c`, `dcn30_hubp.h`, IRQ, GPIO, clock manager, and DMUB include sites.
- Statically compare this generated header chunk against AMD's DCN 3.0.0 register database and the matching `dcn_3_0_0_offset.h` to verify every visible `__SHIFT` and `_MASK` pair matches the intended register field.
- Diff repeated instance families across `HUBP1/2/3`, `HUBPREQ1/2/3`, `HUBPRET1/2`, `CURSOR0_1/2`, and `DC_PERFMON7/8` to catch accidental instance drift where the hardware layout should be identical.
- Exercise display hardware with enough active pipes to use instances 1, 2, and 3. Cover modeset, page flip, plane enable/disable, cursor movement, cursor format changes, scaling, rotation, mirroring, multi-monitor, hotplug, DPMS, suspend/resume, and GPU reset recovery.
- Test RGB and YUV/chroma paths with primary and secondary surfaces, metadata addresses, DCC-enabled surfaces, and TMZ/protected surfaces where supported.
- Stress page-flip behavior: immediate flips, vblank-synchronized flips, update locks, stereo sync modes, GSL, triple buffering, flip pending status, flip-away status, and IRQ clear/mask behavior.
- Validate VM/TLB and DMDATA paths by exercising VM aperture setup, DMDATA VM fault/underflow/late/done status, cursor/metadata address programming, and software DMDATA update paths.
- Run bandwidth-sensitive display workloads at high resolution/refresh and low memory clock. Watch for underflow, flicker, corruption, missed vblank, page faults, flip timeouts, or failures isolated to one pipe.
- Use display perfmon/debug tooling, where available, to configure `DC_PERFMON7` and `DC_PERFMON8`, start/stop counters, read low/high values, and verify interrupt/status/ack behavior.

## Cross-Chunk Notes

The previous chunk is needed for the beginning of `DC_PERFMON6_PERFCOUNTER_CNTL`. The next chunk is needed for the rest of `HUBPREQ3`, including later blanking, destination, prefetch, vblank, flip, nominal, delivery, cursor, reference-frequency, DRQ-limit, and memory-power fields. The final per-file research document should merge those adjacent reports before making complete statements about the DCN 3.0.0 generated register map.
