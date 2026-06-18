# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 39827-42175

## Scope

This chunk is a generated DCN 3.1.5 register-field mask/shift slice. It contains only C preprocessor constants and address-block/register comments: `_SHIFT` macros encode field bit positions, and `_MASK` macros encode raw 32-bit register masks. There are no C functions, structs, enums, allocations, branches, loops, or direct MMIO operations in this range.

The range starts in the tail of `VPG3_VPG_MPEG_INFO0`, covers `VPG3_VPG_MPEG_INFO1`, then fully defines the DIG4 DME/VPG4 blocks, DP AUX instances 0 through 4, the shared DOUT I2C/DDC controller block, and DIO scratch registers 0 through 6. The next source lines continue with `DIO_SCRATCH7` and DIO memory-power registers, so DIO scratch coverage is intentionally partial at this chunk boundary.

## Purpose And Hardware Surface

This header section supplies the bit-layout ABI used by AMDGPU Display Core for DCN 3.1.5 display-I/O hardware. Companion generated headers provide register offsets; this file provides the field masks and shifts consumed by register-helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT`.

Major hardware areas represented here:

- VPG packet generation: `VPG3_VPG_MPEG_INFO*` tail fields and full `VPG4_*` generic packet, frame-update, immediate-update, status, memory-power, ISRC, and MPEG-info fields used for HDMI/DP info packets and metadata injection.
- DIG4 DME metadata engine: `DME4_DME_CONTROL` and `DME4_DME_MEMORY_CONTROL` fields for enabling dynamic metadata, selecting metadata stream/requestor behavior, observing double-buffer handshakes, clearing missed transmissions, and controlling DME SRAM power.
- DP AUX channels 0-4: repeated `DP_AUXn_*` field groups for AUX enable/reset, software and link-service transfers, AUX arbitration, interrupt status/ack/masking, software/link-service data windows, AUX DPHY TX/RX timing, GTC sync control/status, and AUX PHY wake handshakes.
- DC I2C/DDC controller: `DC_I2C_*` fields for software I2C transactions, register arbitration with firmware/hardware users, DDC1-5 hardware/EDID detection status, per-DDC speed/setup timing, transaction descriptors 0-3, indexed data buffer access, EDID-detect control, and read-request interrupt handling for DDC1-6 plus DDCVGA.
- DIO scratch registers: full-width scratch masks for `DIO_SCRATCH0` through `DIO_SCRATCH6`.

## Important Definitions

The exported interface is the generated naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted bitmask for that field in the register value.
- `// addressBlock: ...` comments group register instances by hardware block.
- `//<REGISTER>` comments group the fields belonging to each register.

Important macro families in this chunk:

- `DME4_DME_CONTROL` defines metadata requestor ID, engine enable, stream type, double-buffer pending/taken status, clear bits, DB disable, transmission-missed status, and missed clear fields. `DME4_DME_MEMORY_CONTROL` defines force/disable/state/default-low-power fields for DME memory.
- `VPG4_VPG_GENERIC_PACKET_ACCESS_CTRL` and `VPG4_VPG_GENERIC_PACKET_DATA` expose the indexed generic packet RAM window, with four packed data bytes per write. `VPG4_VPG_GSP_FRAME_UPDATE_CTRL` and `VPG4_VPG_GSP_IMMEDIATE_UPDATE_CTRL` provide update and pending bits for generic packets 0-14. `VPG4_VPG_GENERIC_STATUS` exposes lock/conflict state and conflict clear. `VPG4_VPG_MEM_PWR` controls and reports VPG GSP memory light-sleep state. ISRC and MPEG registers expose packed metadata bytes and MPEG update controls.
- Each `DP_AUXn_AUX_CONTROL` block has channel enable/reset, reset-done, link-service read enable, HPD disconnect handling, AUX mode detection, HPD select, impedance calibration request enable, test mode, deglitch enable, and spare bits.
- Each `DP_AUXn_AUX_SW_CONTROL`, `AUX_SW_STATUS`, and `AUX_SW_DATA` group describes software AUX transactions: go/start delay/write-byte count, done/request/error status, reply-byte count, arbitration status, data read/write byte, indexed data access, and autoincrement disable.
- Each `DP_AUXn_AUX_LS_STATUS` and `AUX_LS_DATA` group provides the link-service side of AUX traffic, including done/request/error status, reply-byte count, CP IRQ, updated/ack state, and indexed data access.
- Each `DP_AUXn_AUX_ARB_CONTROL` group coordinates AUX register ownership among software and DMCU/firmware paths through priority, queued-go controls, use-reg requests, pending request state, and done-using-reg bits.
- Each `DP_AUXn_AUX_INTERRUPT_CONTROL` group defines SW done, LS done, GTC sync lock done, and GTC sync error interrupt status/ack/mask fields.
- Each `DP_AUXn_AUX_DPHY_*` group defines AUX physical-layer TX reference/rate/divider, precharge and output-enable timing, mode-detect delay, RX detection windows/threshold/filtering, timeout length, TX active/state/half-symbol period, and RX state/sync/half-symbol period readbacks.
- Each `DP_AUXn_AUX_GTC_SYNC_*` group defines GTC sync enable/impedance calibration/interval/retry/lock timing controls, potential/definite error thresholds, lock acquisition and maintenance status, critical and max-error ack bits, detailed AUX transaction error status, NACK state, and master-request state.
- Each `DP_AUXn_AUX_PHY_WAKE_CNTL` group provides wake go/pending/priority/ack fields for AUX PHY wake sequencing.
- `DC_I2C_CONTROL`, `DC_I2C_ARBITRATION`, and `DC_I2C_SW_STATUS` define software I2C transaction start/reset/DDC select/count fields, ownership/arbitration and abort controls, and completion/timeout/NACK/buffer-overflow status.
- `DC_I2C_DDC1..5_HW_STATUS`, `DC_I2C_DDC1..5_SPEED`, and `DC_I2C_DDC1..5_SETUP` repeat per-DDC hardware status, EDID-detect status/tries/state, threshold/filter/start-stop/prescale timing, line drive, reset length, EDID detection mode, enable, clock drive, byte/transaction delay, and time-limit fields.
- `DC_I2C_TRANSACTION0..3` define read/write, stop-on-NACK, start, stop, and byte-count fields for up to four queued I2C transaction descriptors. `DC_I2C_DATA` exposes the indexed transfer buffer. `DC_I2C_EDID_DETECT_CTRL` sets EDID detect wait time, valid-try count, and reset-send behavior. `DC_I2C_READ_REQUEST_INTERRUPT` packs occurred/int/ack/mask fields for DDC1-6 and DDCVGA plus global ack-enable and interrupt-type controls.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when DCN 3.1.5 display code combines these macros with matching offset registers and register access helpers. The typical flow is:

1. Driver code selects a VPG, DME, AUX, I2C/DDC, or DIO register offset from the generated DCN 3.1.5 offset header or a local register table.
2. The register helper layer uses this header's mask/shift constants to pack fields, perform read/modify/write updates, or decode status fields.
3. MMIO writes program hardware state or trigger side effects; MMIO reads observe volatile status, counters, handshakes, or scratch values.

The state represented here is hardware register state, not persistent driver-owned memory:

- Persistent configuration includes VPG packet RAM contents, generic packet update mode, VPG/DME memory-power controls, DME metadata enable/requestor/stream-type selections, AUX channel enable/timing/arbitration/interrupt mask settings, AUX DPHY timing windows, GTC sync thresholds and retry periods, DDC speed/setup timing, I2C transaction descriptors, EDID detect parameters, and read-request interrupt masks.
- Volatile readback includes VPG conflict/lock status, VPG/DME memory power state, DME double-buffer and missed-transmission state, AUX reset-done, SW/LS/GTC transaction status and errors, AUX arbitration state, DPHY TX/RX state, PHY wake pending/ack, I2C software completion/error/NACK status, DDC hardware/EDID detect state, read-request interrupt state, and DIO scratch values.
- Side-effecting bits include DME clear bits, VPG conflict clear, VPG frame/immediate update triggers, AUX reset/go/ack/done-using-reg/LS updated ack/GTC error acks/PHY wake go, I2C go/reset/status reset/abort/done-using-reg, indexed-data write controls, EDID reset-send, and DDC read-request acks.

## Dependencies And Integration Points

This chunk depends on generated-name consistency across the DCN 3.1.5 register header family. It is consumed with `dcn_3_1_5_offset.h` by DCN 3.1.5 resource, IRQ, GPIO, and DMUB code, and by shared Display Core modules that use chip-specific register tables.

Primary integration points include:

- `display/dc/dcn31/dcn31_vpg.*`: the VPG register and mask tables consume `VPG*_VPG_GENERIC_*`, update-control, status, and memory-power fields. Runtime code writes infoframe/generic-packet bytes through the indexed packet data window, clears conflicts, triggers immediate or frame updates, and controls VPG memory light sleep.
- Display link training and capability paths: DP AUX masks back the low-level AUX engine used for DPCD reads/writes, I2C-over-AUX, link-service status, HPD disconnect behavior, AUX error diagnostics, CP IRQ handling, LTTPR/sink probing, and GTC sync support.
- GPIO/DDC code: `display/dc/gpio/ddc_regs.h` and `hw_ddc.c` use DDC setup fields such as `DC_I2C_DDC1_ENABLE`, `DC_I2C_DDC1_EDID_DETECT_ENABLE`, and `DC_I2C_DDC1_EDID_DETECT_MODE` to configure DDC pins and EDID detection. Software I2C command paths use the control, arbitration, transaction, status, and data-buffer fields.
- IRQ service and firmware coordination: AUX and I2C arbitration/interrupt fields coordinate software, hardware, and DMCU/DMUB users. Incorrect ownership or ack handling can block display detection or lose interrupts.
- Dynamic metadata and info packet paths: DME4 and VPG4 fields integrate with HDMI/DP metadata, generic packets, ISRC, MPEG infoframes, and frame/immediate update scheduling.
- Power-management sequences: DME/VPG memory-power fields, AUX PHY wake fields, and DDC/AUX enable/reset state must be consistent across runtime power transitions, suspend/resume, and display link reinitialization.

Because this file is only macro definitions, missing names usually fail at compile time where referenced. Wrong numeric shifts or masks generally compile successfully but can misprogram MMIO at runtime.

## Risks And Maintenance Notes

- Numeric drift from the DCN 3.1.5 register specification is the main risk. A wrong field value can corrupt DME/VPG metadata programming, AUX transaction timing, I2C/DDC EDID reads, interrupt acks, or power gating.
- The DP AUX blocks are highly repetitive across instances 0-4. Prefix or copy-generation mistakes can silently bind an otherwise valid field layout to the wrong AUX channel.
- Several fields are side-effecting or handshake-based. Clear/ack/go/reset/update bits must be written deliberately; broad read/modify/write helpers can accidentally retrigger updates or clear latched diagnostics if masks are wrong.
- AUX and I2C arbitration fields coordinate multiple clients. Mishandling `*_USE_*_REG_REQ`, pending-request, and done-using fields can deadlock access between driver software and firmware paths.
- Indexed data windows require ordering discipline. VPG packet data, AUX SW/LS data, and DC I2C data all pair an index field with byte/data fields; callers must preserve autoincrement semantics and byte order.
- DDC and AUX timing fields are hardware-contract values. Prescale, timeout, threshold, phase-detect, precharge, and RX window mistakes may surface only with marginal cables, retimers, sinks, or I2C-over-AUX transactions.
- The chunk begins and ends inside logical register families. It starts after the first VPG3 MPEG checksum field and ends before `DIO_SCRATCH7`, so final per-file reconciliation must merge neighboring chunks for a complete file-level account.
- `DIO_SCRATCH*` fields are full-width and generic. Their meaning depends on firmware/driver convention outside this header, so consumers must not assume persistence or ownership from the mask alone.

## Test Signals

Useful validation is generated-header consistency plus hardware behavior:

- Build DCN 3.1.5 AMDGPU display code and ensure all generated macro names referenced by VPG, GPIO/DDC, IRQ, DMUB, and resource tables resolve.
- Run generated-header checks that every in-scope field has a matching `_SHIFT` and `_MASK`, masks fit in 32 bits, and fields do not overlap unexpectedly inside each register.
- Compare this range against the authoritative DCN 3.1.5 register specification, especially repeated DP AUX0-4 and DDC1-5 blocks.
- Exercise VPG generic packet programming by writing infoframes/metadata, clearing conflicts, triggering immediate and frame updates, and verifying pending/status behavior.
- Validate DME4 metadata operation with metadata engine enable, requestor selection, double-buffer pending/taken handshakes, missed-transmission clear, and DME memory-power state transitions.
- Run DP AUX DPCD read/write, I2C-over-AUX, link training, HPD disconnect, CP IRQ, and error-path tests on ports mapped to AUX0-4; confirm timeout, overflow, invalid symbol/start/stop, and reply-byte-count decoding.
- Test AUX arbitration with software and firmware users active, checking request/pending/done-using handshakes and interrupt ack/mask behavior.
- Validate AUX DPHY and GTC sync fields through link bring-up, low-power wake, and GTC sync lock/loss/error scenarios.
- Exercise DDC software I2C EDID reads on DDC1-5, including transaction descriptors 0-3, stop-on-NACK paths, buffer indexing, prescale/timing setup, reset/status reset, and timeout behavior.
- Test hardware EDID detect and DDC read-request interrupts across DDC1-6/DDCVGA, confirming occurred/int/ack/mask/global ack-enable semantics.
- Include suspend/resume and runtime power tests with active displays to verify VPG/DME memory-power, AUX PHY wake, DDC enable, and volatile status fields recover correctly.

## Chunk-Specific Summary

Lines 39827-42175 define DCN 3.1.5 display-I/O mask and shift constants for the end of VPG3 MPEG info, all DIG4 DME/VPG4 metadata and packet-generation fields, DP AUX0-4 software/link-service/DPHY/GTC/PHY-wake fields, the shared DC I2C/DDC controller and EDID-detect fields, and DIO scratch registers 0-6. Correctness depends on exact generated bit positions, instance-correct macro use, careful treatment of trigger/ack/clear fields, and hardware validation that covers info packet updates, dynamic metadata, AUX/DPCD and I2C-over-AUX traffic, DDC EDID reads, interrupt handling, arbitration, and power transitions.
