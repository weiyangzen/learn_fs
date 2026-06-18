# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 24836-27328

## Scope And Purpose

This chunk is a generated AMD DCE 12.0 register field shift/mask header section. It contains C preprocessor constants only: no functions, structs, enums, storage, or executable logic. Each register field is represented by a `__SHIFT` macro and a matching `_MASK` macro that callers use to pack or extract bitfields for DCE 12.0 display-engine MMIO registers.

The range begins mid-register at the final mask for `DCP4_COMM_MATRIXB_TRANS_C13_C14`, then covers the rest of the DCP4 color/cursor/LUT/CRC/update-control fields, complete address blocks for `dce_dc_lb4_dispdec`, `dce_dc_dcfe4_dispdec`, `dce_dc_dc_perfmon7_dispdec`, `dce_dc_dmif_pg4_dispdec`, `dce_dc_scl4_dispdec`, `dce_dc_blnd4_dispdec`, `dce_dc_crtc4_dispdec`, and `dce_dc_fmt4_dispdec`, and then starts `dce_dc_dcp5_dispdec` through `DCP5_GRPH_UPDATE`.

The purpose is hardware-description support for AMDGPU/DC, not Ceph filesystem behavior. The source tree is a Ceph-client mirror that includes Linux GPU driver code; this file belongs to the AMD display stack and gives register programming code stable symbolic bit positions for pipe 4 and the beginning of pipe 5 on DCE 12.0 hardware.

## Important APIs, Types, And Macro Families

There are no callable APIs or C types in this chunk. The exported interface is the macro namespace. Macro names follow the generated form `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`, with field positions encoded as hexadecimal shifts and masks encoded as 32-bit literals ending in `L`.

The DCP4 section covers display controller pipe 4 plane and color-pipeline fields. It includes matrix coefficients for `COMM_MATRIXB_TRANS_*`, denorm and output rounding/clamp controls, color key ranges, degamma and gamut remap controls, spatial dithering and random seeds, cursor enable/mode/address/size/position/hotspot/color/update/stereo fields, DC LUT read/write/autofill/control/offset fields, DCP CRC control/mask/current/last fields, DVMM PTE control and arbitration, flip-rate/GSL controls, line-buffer data-gap fields, stereo flip control, hardware rotation, XDMA cache-underflow detection/status, regamma LUT and piecewise-region fields for CNTLA/CNTLB, alpha control, XDMA recovery surface addresses, flip timeout/delay, and surface counter controls.

The LB4 line-buffer block defines input data format, interleave and alpha enable, pixel-depth and dynamic expansion/reduction controls, memory size/status, desktop height, vline/vline2/vblank interrupt status and masks, sync reset selection, black/keyer color fields, buffer level/urgency/status/no-outstanding-request fields, and MVP AFR flip/FIFO/line insert controls.

The DCFE4 block defines display front-end clock gating, software reset bits for DCP/SCL/BLND/FMT/CRTC, memory power controls for DCP/LB/SCL/BLND/CRTC/FMT memories, power-status mirrors, miscellaneous DCP global-alpha polarity, and flush controls. These fields are power-management and block-reset sensitive.

The DC_PERFMON7 block defines perf counter selection, count modes, run/stop behavior, interrupt controls, per-counter state fields for counters 0 through 7, perfmon state/control fields, current-value interrupt/mask/status fields, and high/low counter readback fields. It is a display-engine performance-monitor register bank, not Linux perf infrastructure.

The DMIF_PG4 block defines pipe arbitration, watermark mask, urgent/stutter/low-power controls, repeat programming, checksum pre-process control, and DVMM status fields for display memory-interface pipe group 4. These fields directly affect display memory fetch timing, latency tolerance, stutter entry/exit, and virtual-memory fault/status reporting.

The SCL4 scaler block defines coefficient RAM selection and tap data fields, scaler mode/tap/bypass/manual-replicate/automatic-mode controls, horizontal and vertical filter ratios/initial phases, round offsets, update lock/pending/taken controls, sharpness and ALU controls, coefficient conflict status, primary/secondary viewport start and size, external overscan, and mode-change detection/masking fields.

The BLND4 block defines blender enable/mode/alpha/stereo/current-eye controls, SM control, feeding-pixel and clamp controls, update lock/pending/taken controls, underflow interrupt/mask/clear/status fields, V-update lock behavior, and register-update status fields. This is the composition stage between DCP/SCL/FMT/CRTC.

The CRTC4 timing-generator block is the largest complete block in this chunk. It covers horizontal and vertical totals, blanking, sync A/B timing and polarity, variable vertical total control, total/nominal-vsync/vupdate/range timing interrupt status, trigger A/B controls, force-count and flow controls, stereo/interlace controls and status, CRTC enable/master/update locks, blanking/test-pattern/readback/status/counter/snapshot fields, vertical interrupt 0/1/2 controls, CRTC CRC windows and data, external timing sync controls and interrupt state, static-screen control, 3D structure, GSL, DRR, overscan/blank/black color registers, and MVP status/insert fields.

The FMT4 formatter block defines clamp bounds, dynamic expansion, pixel encoding, subsampling, 4:2:0 phase state, truncation/spatial/temporal dithering, random seeds and offsets, clamp format, formatter CRC control/signature/masks, side-by-side stereo active width, and 4:2:0 hblank early start fields.

The DCP5 opening section begins the next pipe's graphics-plane state. It includes enable/keyer alpha, surface format/depth/tiling geometry, address-translation and privileged-access controls, shader-engine/pipe layout fields, 10-bit LUT bypass, endian and color-channel crossbar controls, primary/secondary surface addresses and high address bits, pitch, viewport offsets, X/Y start/end, input gamma mode, and the start of graphics update status/lock fields.

## Control Flow And Data Flow

This header has no internal runtime control flow. Data flow is compile-time macro substitution: a C source file includes `dce_12_0_sh_mask.h`, combines these field descriptions with a companion register address from `dce_12_0_offset.h`, and reads or writes the target hardware register through AMDGPU/DC helpers.

The DCE 12.0 timing-generator code shows the typical pattern. `display/dc/dce120/dce120_timing_generator.c` includes this header and uses helper macros such as `CRTC_REG_UPDATE`, `CRTC_REG_SET`, and `FD(reg__field)` to pass field descriptors into `generic_reg_update_soc15()` or `generic_reg_set_soc15()`. Those helpers use the `__SHIFT` and `_MASK` values to update one or more fields without manually spelling bit arithmetic at each call site.

Interrupt registration follows a similar compile-time composition path. `display/dc/irq/dce120/irq_service_dce120.c` builds `irq_source_info` entries with macros such as `IRQ_REG_ENTRY`, `vblank_int_entry`, `vupdate_int_entry`, and `pflip_int_entry`; those entries pair DCE 12.0 register offsets with field masks such as vertical interrupt enable/clear, v-update clear, and graphics page-flip interrupt mask/clear fields.

Hardware sequencing, resource setup, GPIO translation/factory code, and `amdgpu/gmc_v9_0.c` also include the DCE 12.0 offset and shift/mask headers. Some of this chunk's fields may be used indirectly through shared DCE macros that target pipe instance 0 with a runtime pipe offset, while the generated pipe-4 and pipe-5 names document the replicated hardware layout.

## State And Persistence Behavior

The file stores no state and performs no I/O. The mutable state represented by these constants lives in DCE 12.0 display hardware registers. Driver writes using these macros can persist until another modeset, page flip, cursor update, color update, interrupt acknowledgement, power-management transition, suspend/resume sequence, or hardware reset rewrites the block.

Important state categories represented here include color pipeline state, LUT and regamma programming, cursor surface and position state, graphics primary/secondary surface address state, scaler ratios and viewport state, line-buffer memory and urgency state, DMIF watermark/stutter/urgent state, timing-generator totals/sync/blanking/counter state, interrupt masks and sticky status bits, CRC capture windows and signatures, formatter dithering and pixel encoding, and display-front-end reset or memory power state.

Several fields are double-buffered, latched, or synchronization-sensitive. Examples include `*_UPDATE_LOCK`, `*_UPDATE_PENDING`, `*_UPDATE_TAKEN`, `CRTC_MASTER_UPDATE_LOCK`, `CRTC_MASTER_UPDATE_MODE`, `SCL_UPDATE`, `BLND_UPDATE`, cursor update locks, graphics surface update locks, vertical update locks, GSL controls, DRR controls, and trigger controls. The macro definitions do not enforce sequencing; callers must program them in the order required by the display hardware.

Status and interrupt fields are also stateful. Many masks describe bits that enable, mask, acknowledge, clear, or report sticky events. Misidentifying a status bit as an enable bit, or writing a clear mask at the wrong time, can lose diagnostic information or leave interrupt sources active.

## Dependencies And Integration Points

This chunk depends on the rest of `dce_12_0_sh_mask.h` for a complete include-guarded header and on `dce_12_0_offset.h`/`dce_12_0_d.h` for matching register addresses. It is meaningful only when paired with DCE 12.0 register offsets and the SOC15 base-index model used by the AMDGPU display code.

Direct includes in this tree include `display/dc/dce120/dce120_timing_generator.c`, `display/dc/hwss/dce120/dce120_hwseq.c`, `display/dc/irq/dce120/irq_service_dce120.c`, `display/dc/gpio/dce120/hw_translate_dce120.c`, `display/dc/gpio/dce120/hw_factory_dce120.c`, `display/dc/resource/dce120/dce120_resource.c`, and `amdgpu/gmc_v9_0.c`.

The main integration surfaces are DRM/KMS modesetting, vblank/vupdate/page-flip interrupt handling, display hardware sequencing, display pipe resource construction, cursor programming, surface flips, color management, scaling, formatter output programming, display memory fetch control, power gating/reset, display performance counters, CRC capture, and GPU memory-controller diagnostics involving DCE clients.

The generated names are ASIC-generation specific. Nearby headers for DCE 6.0, 8.0, 10.0, 11.0, 11.2, and DCE 12.0 offsets contain overlapping block and field names with generation-specific addresses or field coverage. Mixing DCE versions can compile in some macro contexts but program the wrong hardware field.

## Risks And Edge Cases

The highest risk is numeric drift from the authoritative ASIC register database. These constants are opaque to the compiler: a wrong shift or mask still builds but can silently program unrelated bits in display hardware.

This chunk starts and ends inside larger logical blocks. It begins with only the final mask for `DCP4_COMM_MATRIXB_TRANS_C13_C14`, whose shift definitions and first mask are in the previous chunk, and ends in `DCP5_GRPH_UPDATE`, before DCP5 graphics flip/address-in-use/interrupt and later DCP5 fields. The final merged file report should avoid treating this range as a complete DCP4 or DCP5 description.

Repeated pipe-instance names are easy to confuse. Pipe 4 macros such as `CRTC4_*`, `DCP4_*`, `SCL4_*`, `BLND4_*`, `LB4_*`, `FMT4_*`, and `DMIF_PG4_*` mirror other pipe instances. Copying a field from the wrong instance or combining a pipe-4 field with the wrong offset/base can affect another display pipe or no useful register at all.

Wide masks and packed 16-bit fields appear throughout matrix, color, clamp, CRC, position, and seed registers. Off-by-one shifts or sign/width assumptions can corrupt adjacent channels, coordinates, coefficients, or control bits. Surface address fields split low and high address bits; programming only one side or applying the wrong alignment mask can point scanout or cursor fetches at the wrong memory.

Timing and memory-fetch fields can cause visible failures. Wrong CRTC totals, blanking, sync polarity, DRR, GSL, or trigger fields can blank a monitor or destabilize vblank accounting. Wrong DMIF urgency/stutter/watermark fields can cause underflow. Wrong SCL/FMT/DCP color and dithering fields can produce subtle image quality regressions that compile and modeset successfully.

Power/reset fields in DCFE4 are sensitive because they affect multiple sub-block memories and clocks. Incorrect use can leave a sub-block reset, powered down, or reporting stale status while later programming assumes it is live.

## Test Signals

There are no unit tests for this header chunk alone. Useful validation starts with build coverage for AMDGPU/DC configurations that include `dce_12_0_sh_mask.h`, especially DCE 12.0 timing generator, IRQ service, hardware sequencing, GPIO, resource, and GMC code.

Generated-header integrity should be checked against the authoritative DCE 12.0 register database or a known-good upstream generated header. The comparison should focus on this chunk's repeated pipe-4 blocks, the DCP4-to-LB4 and FMT4-to-DCP5 boundaries, packed coefficient/color fields, interrupt clear/mask fields, and address high/low masks.

Runtime signals include successful modeset across all available DCE 12.0 pipes, stable vblank and vupdate events, correct page flips and cursor updates, no display underflow interrupts, correct suspend/resume reprogramming, and no hangs during display power-gating transitions.

Pipeline validation should exercise framebuffer formats, tiling/swizzle settings, primary and secondary surface addresses, cursor formats and positions, color keying, degamma/gamut/regamma/LUT updates, scaling ratios and viewport changes, formatter pixel encodings including 4:2:0 and stereo modes, spatial/temporal dithering, and clamp behavior.

Interrupt and diagnostic validation should cover CRTC vertical interrupts, vupdate and range timing status, DCP page-flip and underflow status, BLND underflow status, DC_PERFMON7 counter programming/readback, DCP/CRTC/FMT CRC capture paths, DMIF DVMM status, and surface counter outputs. These tests catch polarity, clear-mask, latch, and field-width mistakes that compile-time checks cannot see.
