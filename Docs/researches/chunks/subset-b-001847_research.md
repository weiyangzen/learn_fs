# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 34608-36980

## Purpose

This chunk is generated AMD DCN 3.1.4 register field metadata. It contains C preprocessor constants for hardware register field shifts and masks; it has no executable C logic, no declarations with storage, and no local data structures.

The requested range covers 2,373 lines with 2,179 `#define` entries: 1,089 `__SHIFT` macros and 1,090 `_MASK` macros. It starts inside the `DC_PERFMON15_PERFMON_CNTL` field block, completes the tail of perfmon15, covers the DIO display-output I2C/DDC block, DIO misc/link/power/clock registers, HPD0 through HPD4 hot-plug-detect blocks, a complete `DC_PERFMON16` block, complete DP AUX0 through DP AUX2 blocks, and ends partway through DP AUX3 at `DP_AUX3_AUX_LS_DATA`.

Although the source tree path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU display-driver hardware metadata copied into the tree. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, typedefs, includes, variables, locks, or allocation paths in this range. The interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for the named hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field.

These constants are consumed with the matching DCN 3.1.4 offset header and AMD display register helpers such as `FD_SHIFT`, `FD_MASK`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and DMUB register-table macros. A shift/mask macro is only meaningful when paired with the correct MMIO register address from `dcn_3_1_4_offset.h`.

Major register families in this slice:

- `DC_PERFMON15_*` tail and `DC_PERFMON16_*`: display-controller performance monitor control, counter selection/state, report counts, clock enable, counter-off interrupt controls, counter-value low/high fields, and per-counter interrupt status/ack bits.
- `DC_I2C_*`: software I2C control, arbitration between software/hardware/DMCU access, interrupt status/ack/mask for SW and DDC hardware engines, SW transfer status/error bits, DDC1 through DDC5 hardware status, DDC speed/setup timing, transaction descriptors 0 through 3, data FIFO access, EDID detect control, and read-request interrupt controls.
- `DIO_SCRATCH0` through `DIO_SCRATCH7`: 32-bit scratch registers with full-width payload masks.
- `DIO_*` misc controls: DP ALPM wakeup interrupt status, memory power status/control, DIO clock enables and gating/disconnect bits, power-management idle status, HDMI RX status timer, generic interrupt message/clear fields, and per-link `DIO_LINKA_CNTL` through `DIO_LINKF_CNTL`.
- `DIG_SOFT_RESET`: per-DIG soft reset bits for DIGA through DIGF plus AUX, HPD, and I2C reset controls.
- `HPD0_*` through `HPD4_*`: hot-plug interrupt status, interrupt enable/ack/mask/polarity/timer, HPD line state/enable/connection timer, fast-train delay/select, and toggle-filter timing fields.
- `DP_AUX0_*`, `DP_AUX1_*`, and `DP_AUX2_*`: AUX enable/reset/control, SW transaction control, arbitration, SW/LS/GTC-sync interrupts, detailed SW and link-service status/error fields, SW/LS data windows, DPHY TX/RX controls and status, GTC sync control/error/status, and AUX PHY wake controls.
- `DP_AUX3_*` partial block: AUX3 control, SW control, arbitration, interrupt control, SW status, LS status, and SW/LS data fields. Its DPHY/GTC/PHY-wake registers continue after this chunk.

Representative field names show the semantics exposed by the generated constants: `DC_I2C_GO`, `DC_I2C_TRANSACTION_COUNT`, `DC_I2C_SW_USE_I2C_REG_REQ`, `DC_I2C_DMCU_DONE_USING_I2C_REG`, `DC_I2C_SW_TIMEOUT`, `DC_I2C_SW_STOPPED_ON_NACK`, `DC_I2C_DDC<n>_EDID_DETECT_STATE`, `DIO_MEM_PWR_DIS`, `DIO_MEM_PWR_STATE`, `DISPCLK_G_R_DIO_GATE_DIS`, `DIG<n>_RESET`, `DC_HPD_INT_ACK`, `DC_HPD_SENSE`, `AUX_SW_GO`, `AUX_REG_RW_CNTL_STATUS`, `AUX_SW_RX_TIMEOUT`, `AUX_LS_CP_IRQ`, `AUX_GTC_SYNC_LOCK_DONE_INT`, and `DP_AUX_PHY_WAKE_ACK`.

## Control Flow

This header does not contain runtime control flow. Runtime sequencing is supplied by AMDGPU display and DMUB code:

1. DCN 3.1.4 code includes the offset header and this shift/mask header.
2. Register helper macros paste register and field names into generated tokens such as `DP_AUX1_AUX_SW_STATUS__AUX_SW_RX_TIMEOUT_MASK`.
3. Drivers or firmware-service setup code use the offset and field metadata to compose read/modify/write operations, poll hardware status, acknowledge interrupts, and build firmware-visible register tables.
4. Display link, hotplug, AUX, DDC/I2C, clock/power, reset, and perfmon code provide the real ordering around those MMIO accesses.

The macros do not encode any sequencing constraints. Consumers must still perform protocol-specific ordering, such as requesting I2C/AUX register ownership before starting a software transaction, clearing or acknowledging sticky interrupt bits in the hardware-defined way, waiting for AUX reset completion, respecting HPD debounce/filter timing, and restoring DIO clocks/power before touching blocks that may be gated.

## State And Persistence Behavior

The chunk stores no software state and persists nothing. It describes fields in hardware registers whose persistence and side effects are defined by DCN 3.1.4 hardware.

The represented hardware state includes:

- Performance monitor state: counter mode, selected event/state sources, current counter values, report-count thresholds, interrupt status and acks, clock enable, and run-enable start/stop selectors.
- I2C/DDC state: active transaction count, selected DDC line, arbitration ownership, abort signals, software transfer status and errors, DDC hardware request/done/urgent status, EDID-detect state, speed/setup timing, transaction opcodes/stop/start flags, FIFO data/indexing, and read-request interrupts.
- DIO misc state: scratch payloads, link-power and memory-power status, DIO clock-gating controls, soft-reset bits, generic interrupt payload/clear values, HDMI timer programming, and link training override/disable bits for links A through F.
- HPD state: sensed connector level, interrupt routing and acknowledgement, connect/disconnect timer values, HPD enablement, and fast-training/toggle-filter controls.
- DP AUX state: software and link-service transfer control, request/done status, protocol error reporting, reply byte count, arbitration state, DPHY calibration/status, GTC sync status, CP IRQ indication, and AUX PHY wake handshakes.

Many of these fields are likely volatile or side-effect-sensitive: interrupt ack bits may be write-one-to-clear or self-clearing, status bits may be sticky until acknowledged, reset/go/abort bits may trigger hardware state machines, and data-window index fields may auto-increment. This generated mask header does not identify access permissions or side effects, so consumers must rely on the hardware specification and surrounding driver patterns.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.1.4 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h`, which supplies the corresponding register offsets and base-index selectors.
- DCN 3.1.4 display register-access helpers in AMDGPU display code, including field helper macros that map symbolic register/field names to `_MASK` and `__SHIFT` constants.
- DMUB service code for DCN 3.1.4. The neighboring offset research identifies `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c` as an include/integration point for the offset and shift/mask headers.
- Display connector management code paths that program DDC/I2C and DP AUX engines for EDID/DPCD access, HPD interrupt handling, link training, DisplayPort sideband activity, power management, and diagnostics.

The line range is source-tree-aligned to `dcn_3_1_4_sh_mask.h` but is not a semantic file boundary. It begins after the first `DC_PERFMON15_PERFMON_CNTL` field and ends before the DP AUX3 DPHY/GTC/PHY-wake field families, so final per-file analysis must reconcile neighboring chunks before presenting complete per-block coverage.

## Risks And Edge Cases

- Shift/mask drift is the main correctness risk. These macros are untyped constants, so an incorrect generated value can compile cleanly while corrupting unrelated MMIO bits.
- Protocol engines are side-effect-heavy. Blind read/modify/write on I2C, AUX, HPD, reset, or interrupt registers can lose status, retrigger interrupts, abort in-flight transfers, or start hardware transactions unexpectedly.
- I2C and AUX arbitration fields represent shared ownership among software, hardware engines, and DMCU/DMUB paths. Incorrect ownership sequencing can deadlock register access or race firmware/hardware transfers.
- DDC/EDID and DP AUX errors are user-visible as missing displays, failed EDID reads, broken DPCD access, bad link training, MST instability, or intermittent hotplug behavior.
- HPD timing and polarity fields are connector-sensitive. Wrong masks can produce interrupt storms, missed plug/unplug events, or fast-training behavior on the wrong HPD instance.
- Clock, memory-power, and reset fields can make otherwise valid register programming fail if a block is gated or held in reset. The mask header does not state which blocks require ungating first.
- Repeated DP AUX0/1/2 layouts invite copy/paste or generator skew. A per-instance mismatch might affect only one connector path, making failures hardware-port-specific.
- The chunk contains partial boundaries for perfmon15 and AUX3. Any automated check that expects complete register families in this file slice must account for the preceding and following chunks.

## Test Signals

Useful validation combines generated-header checks with hardware and driver behavior:

- Build AMDGPU display and DMUB code paths that include `dcn_3_1_4_sh_mask.h`; renamed, missing, or malformed macros should fail where register tables or field helpers reference them.
- Mechanically verify that complete field groups in lines 34608-36980 have consistent `__SHIFT`/`_MASK` pairs, with explicit exceptions for the chunk boundaries at `DC_PERFMON15_PERFMON_CNTL` and `DP_AUX3_AUX_LS_DATA`.
- Diff this range against AMD's authoritative DCN 3.1.4 register database and nearby generated DCN headers where DIO, HPD, I2C, AUX, and perfmon layouts should match.
- Exercise DDC/I2C EDID reads across all exposed connectors, including NACK, timeout, unplug, suspend/resume, and repeated hotplug cases.
- Exercise DP AUX and link-training flows on AUX0 through AUX3-capable hardware: DPCD reads/writes, HPD disconnect during AUX, CP IRQ/link-service status, MST sideband access, and AUX timeout/overflow paths.
- Validate HPD0 through HPD4 interrupt behavior by plugging/unplugging displays and checking that the expected connector reports events without interrupt storms or missed disconnects.
- Test power-management and reset paths through display suspend/resume, runtime power transitions, and modesets while watching for stuck DIO memory power state, gated-clock access failures, or blocks left in reset.
- Use perfmon/debug paths, where available, to confirm counter reads, counter-off interrupts, and current-value high/low fields behave consistently.

## Cross-Chunk Notes

The previous chunk owns the start of the `DC_PERFMON15` field family, including earlier `DC_PERFMON15_PERFCOUNTER_*` definitions and the first `DC_PERFMON15_PERFMON_CNTL__PERFMON_STATE__SHIFT` line. The next chunk should continue from `DP_AUX3_AUX_DPHY_TX_REF_CONTROL` and cover the remainder of AUX3 plus later register blocks. The merge lane should combine these chunks before making complete claims about all DIO, HPD, perfmon, or AUX instances in `dcn_3_1_4_sh_mask.h`.
