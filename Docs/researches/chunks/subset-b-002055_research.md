# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h lines 13006-15279

## Purpose

This chunk is generated AMD DCN 3.5.0 register-offset metadata. It contains C preprocessor constants only: each visible hardware register has a `reg...` address macro and a paired `reg..._BASE_IDX` macro. There are no executable functions, structs, enums, branches, allocations, locks, or direct MMIO accesses in this range.

The range covers the late display-pipe output and stream-encoder portion of `dcn_3_5_0_offset.h`. It starts inside the MPC configuration block, continues through MPC output color-space conversion, display performance counters, HPO HDMI/DP stream/link encoder blocks, ABM instances, MPCC MCM color-management blocks, DLPC, DPIA microcontroller registers, HDA aliases, DIO DPIA muxes, and DIG stream mapper offsets, then ends at the header guard `#endif`. Although the path is under a local `ceph-client` source mirror, this is AMDGPU display hardware metadata, not Ceph or distributed filesystem logic.

The requested range has 2,274 source lines and 2,150 `#define` lines: 1,075 register-offset definitions and 1,075 matching `BASE_IDX` definitions. It is boundary-partial at the beginning: line 13006 starts after the `dce_dc_mpc_mpc_cfg_dispdec` address-block comment and after the first MPC config registers, so the complete MPC config block must be reconciled with the previous chunk.

## Important APIs, Types, And Macros

The public interface is the generated macro namespace:

- `reg<REGISTER>`: numeric register offset used by AMDGPU display register helpers.
- `reg<REGISTER>_BASE_IDX`: base-index selector used with DC register-base tables.
- `// addressBlock:` and `// base address:` comments: generator metadata grouping registers by hardware block and block base.

Major register families in this chunk include:

- MPC configuration tail: CRC selection/result registers, perfmon event control, bypass background, host read, DPP/pending status, vertical-update lock sets 0-3, and `MPC_DWB0_MUX`.
- MPC output CSC/denorm: `MPC_OUT0` through `MPC_OUT3` mux, denormalization, clamp, CSC mode, and A/B coefficient registers.
- DC performance monitor: `DC_PERFMON15_*` and HPO perfmon counter/control/value registers.
- HPO HDMI stream support: AFMT5 audio packet/60958/CRC registers, VPG5 generic/secondary data packet registers, DME5 metadata packet registers, HDMI stream encoder clock/input/FIFO controls, HDMI transport/bypass encoder packet, ACR, CRC, encryption, mode, buffer, and metadata controls, plus HDMI link and FRL encoder control/status/memory registers.
- HPO top and DP stream mapping: top-level HPO clock and hardware control plus `DP_STREAM_MAPPER_CONTROL0..3`.
- ABM instances 0-3: backlight PWM levels and duty-cycle controls, ABM control, ACE offset/slope/threshold controls, histogram/luma statistics, sample rates, histogram result bins, and backlight master locks.
- MPCC MCM instances 0-3: shaper LUT controls, RAM A/B shaper regions, 3D LUT mode/index/data/read-write/out-normalization/out-offset registers, 1D LUT control/index/data/RAM A/B piecewise region programming, and memory power control.
- DLPC: enable, current count, OPTC snapshot, power-up, OTG resync, ZSC/LONO power-up, spare, and counter-init registers.
- DPIA MU: per-port clock/reset controls for ports 0-3, TPI status, credit count, interrupt control/status/ack, RBBMIF timeout/status, microsecond reference, port adapter status, glue control, and perf-count registers.
- HDA/Azalia aliases: controller CORB/RIRB, immediate command/response, DMA position, wall-clock alias, endpoint immediate command, and input-endpoint immediate command registers.
- DIO and stream mapping: DPIA mux controls for muxes 0-3 and `DIG0` through `DIG4_STREAM_MAPPER_CONTROL`.

The macro names are consumed through token-pasting register-table definitions rather than as traditional APIs. Callers usually write `REG(...)`, `SR(...)`, `SRII(...)`, `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, or related helper calls that expand into these generated offsets plus field definitions from `dcn_3_5_0_sh_mask.h`.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU Display Core:

1. DCN 3.5 code includes `dcn_3_5_0_offset.h` and `dcn_3_5_0_sh_mask.h`.
2. Resource and block-construction macros paste symbolic register names into `reg...` offset constants and matching mask/shift constants.
3. Display block objects store the resolved offsets in register tables for MPC, ABM, HPO, DMUB, IRQ, and resource code.
4. Modeset, link-training, color-management, audio, backlight, power, interrupt, and diagnostics code use DC register helpers to read or write the underlying MMIO registers in hardware-defined order.

The offsets do not encode sequencing. Correct behavior still depends on external code ordering clocks, resets, stream encoder setup, packet programming, ABM locks, LUT bank selection, memory power transitions, DPIA routing, HDA command-ring setup, and status polling.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes MMIO-backed hardware state. The represented state includes:

- MPC output routing, denormalization/clamp/CSC programming, CRC results, pending-update state, and vupdate lock configuration.
- HPO HDMI/DP stream routing, audio/video info packets, ACR values, generic packets, metadata packets, encryption/mode state, FRL encoder state, FIFO/status values, and HPO clock/hardware enable state.
- ABM backlight/PWM configuration, target/current/final duty levels, adaptive brightness controls, histogram/luma statistics, and lock state.
- MPCC MCM color pipeline state for shaper LUTs, 3D LUTs, 1D LUTs, RAM A/RAM B bank selection and region data, output offsets, and LUT memory power control.
- DLPC counter/snapshot/resync/power state.
- DPIA microcontroller clock/reset, interrupt, timeout, TPI credit/status, perf counter, and mux/routing state.
- HDA/Azalia command/response ring aliases and immediate command/response state.

Persistence is hardware-defined. Configuration registers normally retain values until overwritten, reset, power-gated, or restored during resume. Status, counter, CRC, histogram, FIFO, interrupt, timeout, and command-ring registers can be volatile, sticky, self-clearing, read-only, write-one-to-clear, or firmware-owned depending on the block. This offset header does not state access type, reset value, side effects, or required polling delays.

## Dependencies And Integration Points

This chunk must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h`, which supplies the matching field shifts and masks.
- Other DCN 3.5 generated headers and register-base tables used by AMDGPU Display Core.
- The DCN 3.5 hardware register database that defines block base addresses, instance layout, and per-register access semantics.

Direct include sites for the DCN 3.5 offset and mask headers in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn35/irq_service_dcn35.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.c`

Functional integration points include:

- DCN35 resource construction, including HPO DP stream/link encoder setup, ABM instance registration, audio/stream encoder resources, and comments noting DCN3.5 DPIA topology.
- DMUB DCN35 support, where generated offsets contribute to firmware-facing display register access.
- DCN35 IRQ service setup, which depends on generated register constants for interrupt-source register tables.
- MPC/MPCC color-management code inherited from DCN3.x paths, especially 1D LUT, shaper LUT, 3D LUT, memory-power, and RAM A/RAM B programming paths.
- Backlight and ABM code that programs PWM levels, ACE controls, histogram/luma collection, and lock registers.
- HPO HDMI/DP and DPIA routing code that controls stream mapping, FRL/link/transport encoders, packet generation, audio metadata, and DPIA muxing.

## Risks And Edge Cases

- Generated-offset drift is the main risk. A wrong offset or `BASE_IDX` compiles cleanly but sends a valid register-helper call to the wrong MMIO address.
- The chunk starts mid-address-block. Complete claims about `dce_dc_mpc_mpc_cfg_dispdec` require the previous chunk for `MPC_CLOCK_CONTROL`, soft reset, and CRC control context.
- Repeated instances are copy-sensitive. ABM0-3, MPCC_MCM0-3, DPIA ports 0-3, DIO DPIA muxes 0-3, and DIG stream mappers use structurally similar names; one instance index error can affect only a subset of pipes or connectors.
- `BASE_IDX` values vary by address domain. Most display-register entries here use base index 3, but DLPC/DIO/DIG entries use base index 2 and HDA alias entries use base index 0 or 1. A base-index mismatch can target a wrong register aperture even if the register offset looks plausible.
- LUT programming is banked and stateful. MPCC MCM shaper/1D LUT RAM A/RAM B registers require correct host selection, index setup, write masks, and mode updates; stale bank selection can produce valid-looking but wrong color output.
- ABM and histogram registers mix configuration, locks, live statistics, and PWM output state. Updating them without respecting lock/update sequencing can cause visible brightness jumps or stale histogram feedback.
- HDMI/HPO packet, ACR, CRC, FIFO, encryption, FRL, and metadata registers are timing-sensitive. Programming them while a stream is active or clocks are gated can cause audio/video packet errors, black screens, or link retraining.
- DPIA MU and DIO mux registers are routing and interrupt sensitive. Incorrect clock/reset or mux programming can break USB-C/DP Alt Mode paths or produce hard-to-diagnose hotplug/link failures.
- HDA aliases use overlapping offsets for different CORB/RIRB/immediate-command views. Consumers need the field-level mask header and HDA access semantics to avoid treating aliases as independent storage.

## Test Signals

Useful validation for changes touching this chunk includes:

- Build AMDGPU Display Core with DCN35 enabled; malformed, missing, or renamed macros should fail in `dmub_dcn35.c`, `irq_service_dcn35.c`, `dcn35_resource.c`, and register-table users.
- Mechanically compare this range against AMD's authoritative DCN 3.5.0 register database or a regenerated `dcn_3_5_0_offset.h`; every visible `reg...` should have exactly one matching `reg..._BASE_IDX`.
- Cross-check every register family against `dcn_3_5_0_sh_mask.h` so offset names and field-mask names remain aligned.
- Exercise DCN35 display modes across HDMI FRL, HPO DP, and DPIA/USB-C paths: hotplug, modeset, link-rate changes, blank/unblank, suspend/resume, and runtime power transitions.
- Validate HDMI/HPO audio and packet behavior with audio playback, infoframe/metadata changes, HDR or variable metadata paths, CRC/status reads, and high-bandwidth FRL modes.
- Validate ABM/backlight behavior by changing brightness, enabling/disabling adaptive brightness, checking PWM duty-cycle registers, and watching histogram/luma statistics update without jumps or stalls.
- Validate color-management paths by loading 1D LUT, shaper LUT, and 3D LUT state on all MPCC instances, switching RAM banks, and checking output visually or through CRC/reference captures.
- Monitor kernel logs and debug dumps for HPO FIFO underflow, FRL/link encoder faults, DPIA MU interrupts/timeouts, HDA command-ring failures, ABM lock/update stalls, MPCC MCM memory-power timeout, and unexpected stream mapper routing.

## Cross-Chunk Notes

The previous chunk owns the beginning of the MPC configuration address block and the immediately preceding MPCC OGAM/gamut remap offsets. This chunk owns the remainder of the file through `#endif`, including all visible MPCC MCM instance blocks and late HPO/DPIA/HDA/DIO stream mapping offsets. The final per-file report should merge this document with adjacent chunks before making complete claims about the full `dcn_3_5_0_offset.h` register map.
