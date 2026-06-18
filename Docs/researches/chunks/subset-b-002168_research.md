# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 42396-44858

## Purpose

This chunk is a generated AMD DCN 4.1.0 shift/mask header slice for display hardware register fields. It contains no executable C code; its public surface is a set of `#define` constants that give bit positions (`__SHIFT`) and bit masks (`_MASK`) for fields in DCN display registers.

The requested range contains 2,144 generated definitions. It starts in the tail of the `DSCC0` debug field group, covers the `DSCCIF0` and `DSC_TOP0` field groups, covers complete DSC compressor/interface/top field layouts for DSC instances 1 through 3, then covers DCOH top, PHY mux instances 0 through 3, DP AUX instances 0 through 3, and ends at the beginning of HPD0 hot-plug-detect fields. The boundaries are artificial chunk boundaries: `DSCC0` begins in the previous chunk, and HPD0 continues in the next chunk.

Although this file lives under a local `ceph-client` source mirror, this chunk is AMDGPU display-controller metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct MMIO operations in this range. The API contract is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position inside the register.
- `<REGISTER>__<FIELD>_MASK`: the field's bit mask inside the register.

The main register-field families in this chunk are:

- `DSCC0` tail: debug data fields and display-clock debug index/data fields for DSC compressor instance 0.
- `DSCCIF0` through `DSCCIF3`: input pixel format, bits per component, and double-buffer update-pending fields for the DSC compressor interface.
- `DSC_TOP0` through `DSC_TOP3`: DSC clock enable, display-clock and DSCCLK gate-disable bits, fine-grain clock-gating repeat disable, dynamic DSCCLK gating, debug enable, test clock mux, spare debug, and test debug index/data fields.
- `DSCC1` through `DSCC3`: DSC compressor configuration, status, interrupts, picture parameter set registers, memory-power controls, error counters, buffer fullness counters, and diagnostic readback fields.
- `DCOH_TOP`: DCOH clock control and spare fields.
- `PHY_MUX0` through `PHY_MUX3`: PHY mux enable, output-to-PHY selection, and port-type fields.
- `DP_AUX0` through `DP_AUX3`: DisplayPort AUX channel control, software transaction control/status/data, low-speed status/data, arbitration, interrupt control, DPHY TX/RX timing/status, and AUX PHY wake control/status fields.
- `HPD0` beginning: hot-plug interrupt status/control, HPD enable/timer fields, fast-train delay/enable fields, and toggle-filter timing fields.

The DSC PPS groups are dense and user-visible. `DSCCx_DSCC_PPS_CONFIG0` through `DSCCx_DSCC_PPS_CONFIG22` encode DSC version, line-buffer depth, component precision, bits per pixel, RGB/4:2:2/4:2:0 flags, block prediction, chunk size, picture and slice dimensions, initial transmit/decode delays, scale values and intervals, first/second-line BPG offsets, initial/final offsets, flatness QP limits, RC model size, RC edge and quantization limits, target offsets, RC buffer thresholds 0 through 13, and range parameter triples 0 through 14.

The AUX groups are also structurally repeated. Each `DP_AUXn` instance exposes enable/reset/reset-done, manual AUX transaction start and byte count, reply/status/error bits, read/write data window and index, arbitration state, software-done interrupt acknowledge/enable bits, low-speed sideband status, physical layer TX reference/timing controls, RX threshold/window/timeout controls, TX/RX state readback, and a wake handshake/status surface.

## Control Flow

This header has no runtime control flow. It participates in compile-time register-table construction:

1. DCN401 code includes `dcn_4_1_0_offset.h` and this matching `dcn_4_1_0_sh_mask.h`.
2. Resource and block headers use token-pasting macros such as `DSC_SF`, `AUX_SF`, `SRI_ARR`, `SR`, and `REG_FIELD_LIST` variants to bind generic field names to the generated instance-0 or per-instance field macros.
3. Runtime display objects receive register, shift, and mask tables during construction.
4. Shared AMD display helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` use those tables to read, write, and update bitfields in MMIO registers.

The macros in this chunk do not define programming order. DSC setup, AUX transaction sequencing, HPD interrupt handling, PHY mux selection, power management, and clock gating are controlled by driver code and hardware rules outside this generated header.

## State And Persistence Behavior

The header stores no software state and persists nothing itself. It names hardware-visible state fields:

- DSC compressor configuration and status, including slice topology, initial-code-history behavior, rate-control model size, double-buffer update pending, PPS payload, memory-power state, error counters, buffer fullness readback, and debug bus selectors/data.
- DSC top/interface state, including clock enable/gating, debug muxing, input pixel format, component precision, and double-buffered interface update status.
- DCOH and PHY mux state, including display-output-to-PHY routing and port type.
- DP AUX state, including software transaction state, reply byte count, completion/error flags, arbitration ownership, interrupt enable/acknowledge bits, DPHY timing/status, and AUX PHY wake handshakes.
- HPD0 state at the end of the range, including HPD sense/interrupt/RX interrupt status, interrupt polarity/enable/acknowledge, HPD enable, connection/RX timers, fast-train delays, and connect/disconnect filter delays.

Persistence and side effects are hardware-defined. Configuration fields generally remain until modeset, link reset, suspend/resume, power gating, GPU reset, or ASIC reset rewrites them. Status and interrupt fields can be latched, write-one-to-clear, self-clearing, or valid only while the relevant display block is powered and clocked. This file only provides bit positions and masks; it does not encode those access semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DCN 4.1.0 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h` supplies the matching register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c` includes both generated headers and initializes AUX, HPD, link encoder, HPO, and DSC register/shift/mask tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.h` defines `DSC_REG_LIST_DCN401_RI(id)`, which expects the `DSCC`, `DSCCIF`, and `DSC_TOP` names covered here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn401/dcn401_dsc.h` defines `DSC_REG_LIST_SH_MASK_DCN401(mask_sh)` using instance-0 field names such as `DSCC0_DSCC_PPS_CONFIG*`, `DSCC0_DSCC_INTERRUPT_STATUS*`, and `DSC_TOP0_DSC_TOP_CONTROL`; this chunk contains the tail of the instance-0 metadata and the full instance-1 through instance-3 generated copies.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn401/dcn401_dsc.c` programs DSC configuration, interrupt enables, PPS fields, and readback/status fields through the shift/mask tables derived from this header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_aux.h` provides the AUX field-list macros that consume `DP_AUX0_*` shift/mask names for all AUX engine instances.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn401/irq_service_dcn401.c` includes this header for HPD and HPD RX interrupt source setup. This chunk starts HPD0; HPD1 and later HPD fields continue after this chunk.

Behaviorally, this range is an endpoint for three important display paths: DSC stream compression, connector AUX/DDC/DPCD transactions, and hotplug/link-detection plumbing. It also describes the lower-level DCOH/PHY mux fields that connect display output logic to physical ports.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while corrupting only one register field at runtime.
- The file is generated. Manual edits risk divergence from the authoritative register database, the offset header, firmware assumptions, and silicon documentation.
- Chunk boundaries are not semantic. The first lines are only the tail of `DSCC0`, and the final lines stop inside the HPD0 block. Adjacent chunk reports must be merged before making whole-file claims about all DSC or HPD fields.
- Repeated instances are copy-sensitive. `DSCC1`, `DSCC2`, and `DSCC3` are structurally similar; a per-instance generator error can break only one DSC pipe or only modes routed through that instance.
- DCN401 DSC uses a split interrupt layout (`DSCC_INTERRUPT_CONTROL0/1` plus `DSCC_INTERRUPT_STATUS0/1`) rather than the older single combined interrupt-control/status register. Consumers that assume older field names or clear semantics can miss overflow/underflow events or leave status bits stuck.
- DSC PPS fields must be programmed coherently. Bad masks for dimensions, chunk size, rate-control thresholds, or range QP/BPG offsets can produce blank displays, decoder mismatch, visible corruption, bandwidth instability, or failures only under high-resolution/high-refresh modes.
- `DSCCIF*_DOUBLE_BUFFER_REG_UPDATE_PENDING` and `DSCC*_DSCC_DOUBLE_BUFFER_REG_UPDATE_PENDING` are synchronization/status fields. Polling the wrong bit can cause modeset code to proceed before hardware has latched compressed-stream parameters.
- Memory-power fields are sequencing-sensitive. Forcing or reporting the wrong DSCC memory power state can interact badly with DSC enable/disable, power gating, suspend/resume, or fine-grain clock gating.
- AUX status fields include many physical and protocol error conditions: timeout, overflow, HPD disconnect, non-AUX mode, partial byte, minimum-count violation, invalid stop/start, sync invalid, no detect, invalid high/low receive, CP IRQ, update, and wake-ack errors. Wrong masks can misclassify sink absence, link issues, or HDCP/CP IRQ events.
- AUX software data windows use index, data, read/write, and autoincrement-disable fields. Incorrect masks can corrupt EDID/DPCD transactions or produce off-by-one data-window behavior.
- HPD fields can be edge/level and acknowledge sensitive. Bad HPD status, polarity, enable, or acknowledge masks can cause missed hotplug events, repeated interrupts, or connector state flapping.
- DCOH/PHY mux fields control physical routing. Incorrect mux selection or port-type masks can make an otherwise valid encoder/AUX/HPD setup target the wrong connector.

## Test Signals

Useful validation combines generated-header consistency checks with runtime display behavior:

- Build DCN401 AMDGPU display support. Missing or renamed macros should surface in `dcn401_resource.c`, `dcn401_resource.h`, `dcn401_dsc.h`, `dcn401_dsc.c`, `dce_aux.h`, and HPD IRQ setup.
- Mechanically compare this range against the authoritative DCN 4.1.0 register-field database and ensure every `_MASK` has the expected paired `__SHIFT` definition.
- Cross-check this shift/mask range against `dcn_4_1_0_offset.h` so every field register has a corresponding register offset and base-index entry.
- Run or add static checks for repeated instance consistency across `DSCC1-3`, `DSCCIF0-3`, `DSC_TOP0-3`, `PHY_MUX0-3`, and `DP_AUX0-3`, while allowing intentional per-instance prefixes.
- Exercise DSC modes across all available DSC instances, especially high-bandwidth modes that require compression. Expected signals are successful modesets, no stuck double-buffer update-pending bits, no unexpected DSCC output/rate-control overflow or underflow status, and sane PPS readbacks through `dcn401_dsc.c`.
- Validate DSC PPS programming with register dumps or CRC/visual checks across RGB, 4:2:2, 4:2:0/native modes, different bits-per-component settings, slice counts, and picture/slice dimensions.
- Exercise suspend/resume, stream disable/enable, and rapid modeset transitions with DSC enabled to catch memory-power and clock-gating field mistakes.
- Exercise AUX transactions on all four AUX engines: EDID reads, DP DPCD reads/writes, link training sideband traffic, timeout paths on disconnected sinks, CP IRQ handling, and absent-sink behavior. Watch for wrong reply byte counts, stuck `AUX_SW_DONE`, false timeout/error bits, or cross-connector aliasing.
- Exercise HPD0 hotplug and HPD RX behavior at the chunk boundary, then rely on adjacent chunks for HPD1-3 validation. Expected signals are correct sense/status reporting, interrupt enable/acknowledge behavior, and stable connect/disconnect filtering.
- Validate PHY mux routing by testing each physical connector and ensuring AUX, HPD, and link encoder activity are aligned to the same port.

## Cross-Chunk Notes

The previous chunk owns most of `DSCC0`, including its early configuration, PPS, memory-power, error, fullness, and debug selector fields. This chunk starts at the `DSCC0` debug-data tail. The next chunk continues HPD after `HPD0_DC_HPD_TOGGLE_FILT_CNTL` and should cover the remaining HPD instances. The final per-file research document should reconcile these boundaries before describing all of `dcn_4_1_0_sh_mask.h` or all DCN 4.1.0 DSC/AUX/HPD metadata.
