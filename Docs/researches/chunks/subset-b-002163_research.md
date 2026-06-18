# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 30198-32638

## Purpose

This chunk is generated AMD DCN 4.1.0 register field metadata. It contains no executable C logic; it publishes preprocessor constants that describe bit positions and bit masks for DCN display-controller MMIO registers. Runtime display code combines these constants with the companion offset header to read, write, update, and poll individual hardware fields safely.

The requested range is a mid-file slice of `dcn_4_1_0_sh_mask.h`. It starts in the tail of the `OTG3` timing-generator field list, covers OPTC/GSL/ODM misc fields, covers a full `DP0` DisplayPort register-field block, covers the `DIG0` digital encoder block including HDMI, HDCP 1.x, and TMDS fields, then enters the beginning of the repeated `DP1` DisplayPort field block. The range contains 2,158 generated macros over 2,441 lines: 1,079 `__SHIFT` macros and 1,079 matching `_MASK` macros.

Although this file is under a local `ceph-client` source mirror, it is AMDGPU display-driver hardware metadata and has no distributed-filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locking primitives in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the zero-based bit offset of a field inside a 32-bit MMIO register.
- `<REGISTER>__<FIELD>_MASK`: the pre-shifted mask for the same field.

The chunk's major field families are:

- `OTG3_*`: dynamic refresh-rate trigger/window/control fields, constant DTO phase/modulo fields, pipe update pending/status bits, p-state keepout/extend/unblank controls, and spare register fields for timing generator instance 3.
- `GSL_SOURCE_SELECT`, `OPTC_DLPC_CONTROL`, `OPTC_CLOCK_CONTROL`, `ODM_MEM_PWR_*`, and `OPTC_MISC_SPARE_REGISTER`: global sync source routing, display link power/control snapshot selection, OPTC clock gate/status bits, ODM memory power force/disable/status fields, and misc spare fields.
- `DP0_DP_*`: DisplayPort link/stream enable and status, pixel format and MSA timing/colorimetry, video `M/N`, link framing, DPHY training/scrambler/FEC/CRC/PRBS/fast-training, transfer-unit overflow/size, secondary-data packet controls, MST/MSE payload allocation, DP generic SDP controls, ALPM without AUX, symbol counters, and panel replay tunneling optimization.
- `DIG0_DIG_*`, `DIG0_HDMI_*`, `DIG0_AFMT_*`, `DIG0_HDCP_*`, and `DIG0_TMDS_*`: digital front-end/back-end selection, clocks, FIFO, output CRC/test patterns, HDMI metadata/audio/ACR/VBI/infoframe/generic-packet controls, HDMI double-buffer status, AFMT bridge control, HDCP interrupt/status/I2C/local receiver-data fields, TMDS control characters/sync patterns/DC-balancer/control-bit generation, and DIG version.
- `DP1_DP_*`: the beginning of the repeated DisplayPort instance-1 field block, mirroring the DP0 link, stream, DPHY, secondary-data, MST/MSE, and MSA timing families through `DP1_DP_MSO_CNTL1` at the chunk boundary.

The `DP0` and `DP1` families are instance-prefixed variants of the same logical DP hardware fields. Consumers often use token-pasting helper macros to select instance-specific fields, so field names and masks must remain consistent across repeated instances where the hardware definition expects parity.

## Control Flow

This header has no runtime control flow. Runtime sequencing is owned by AMD display code:

1. DCN 4.1.0 code includes this header with `dcn_4_1_0_offset.h`.
2. Resource, IRQ, GPIO, clock-manager, and DMUB code build register and shift/mask tables using macros that paste register names and field names into tokens such as `DP0_DP_SEC_CNTL__DP_SEC_STREAM_ENABLE_MASK`.
3. Driver helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_GET`, `REG_SET`, `SRI`, `SR`, `SRI_ARR`, and field-list macros use the offsets plus these shifts/masks to manipulate individual MMIO fields.
4. Runtime logic in stream/link encoder, timing-generator, HDCP, HDMI, DP, MST, ALPM, and packet code performs the actual ordering: enabling clocks, programming formats, training links, committing secondary packets, updating MSE slot allocation, acknowledging interrupts, and polling status bits.

The macros do not encode whether a field is read-only, write-only, sticky, self-clearing, write-one-to-clear, double-buffered, or timing-sensitive. That behavior is implicit in the hardware spec and consuming driver code.

## State And Persistence Behavior

The chunk stores no software state and persists nothing on disk. It describes hardware-backed GPU state. The represented hardware state includes:

- OTG3 timing and update state, including DRR totals/windows, pending flip/register/cursor update flags, p-state keepout timing, and unblank state.
- OPTC/GSL/ODM state for ready-source selection, timing sync routing, clock gating, test clock selection, and ODM SRAM power modes/status.
- DP0 and DP1 link state for link-training completion/status, lane count, stream enable/status, FEC/scrambler/training patterns, symbol counters, video timing, packet stream framing, secondary-data packet scheduling, MST/MSE payload assignment, ALPM sleep/wake/FEC timing, and panel replay optimization.
- DIG0 encoder state for HDMI/TMDS output mode, metadata and audio packet scheduling, ACR values/status, generic-packet send/continuous/line-reference controls, AFMT control, FIFO calibration/error status, output CRC capture, and test pattern generation.
- HDCP 1.x local receiver and I2C transaction state, including authentication success/failure, AN/BKSV/AKSV/RI/PJ/V/H values, Bcaps/Bstatus, link0/link1 status, retries, abort/timeout/NACK indicators, and deauthentication controls.

Persistence is hardware-defined. Many configuration fields retain values until modeset, link reconfiguration, power gating, suspend/resume, or ASIC reset. Status, interrupt, pending, acknowledgement, counter, and local-data fields may change asynchronously with scanout, link training, packet transmission, HDCP state machines, AUX/DDC activity, or firmware actions.

## Dependencies And Integration Points

This chunk depends on the generated DCN 4.1.0 register database and must match `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h`. The offset header names the MMIO registers; this header names the fields within them.

Direct include sites visible in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn401/irq_service_dcn401.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_translate_dcn401.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_factory_dcn401.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn401.c`

Important downstream consumers include the shared DCE/DCN stream and link encoder code. For example, `dce_stream_encoder` updates `DP_SEC_CNTL` fields for stream, audio, and generic secondary packets; `dce_link_encoder` updates `DP_MSE_SAT*` and `DP_MSE_SAT_UPDATE` fields for MST payload allocation. HDMI/TMDS fields are consumed by digital encoder setup paths, and HDCP fields connect to authentication/status and I2C transfer handling.

## Risks And Edge Cases

- Shift/mask drift is the central risk. These constants are untyped preprocessor values, so an incorrect bit offset or mask can compile cleanly while updating the wrong hardware field.
- Offset/header mismatch is high impact. `dcn_4_1_0_offset.h` and this mask header must describe the same register database revision; otherwise valid field masks may be applied to the wrong MMIO addresses.
- Repeated instance families are copy-sensitive. `DP0` and `DP1` should match where the hardware repeats the block; a single instance typo can produce connector-specific failures that only appear on certain link encoders.
- The chunk boundary is artificial. It begins after the start of `OTG3_OTG_DRR_TRIGGER_WINDOW` and ends immediately after `DP1_DP_MSO_CNTL1`; adjacent chunks are required before making whole-file claims.
- Pending, ack, interrupt, and status fields are side-effect-sensitive. Incorrect use of fields such as packet pending bits, HDCP interrupt acknowledgements, DP training status, FIFO reset/status, ALPM wake interrupts, or MSE update pending bits can cause stuck interrupts, missed updates, or polling timeouts.
- Packet and timing fields interact with scanout timing. Bad secondary-data, HDMI generic-packet, ACR/audio, MSA, M/N, or DRR fields can lead to blank displays, audio loss, HDR/infoframe corruption, underflow, timing instability, or failures limited to specific modes.
- HDCP fields expose security/authentication state. Incorrect field definitions can cause false authentication success/failure, broken protected playback, repeated I2C retries, or failures only with repeaters or dual-link cases.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN 4.1.0 support enabled; missing or renamed field macros should fail in DCN401 resource, IRQ, GPIO, clock-manager, DMUB, stream-encoder, and link-encoder table construction.
- Mechanically verify that every `__SHIFT` macro in lines 30198-32638 has a matching `_MASK` macro for the same register field, and vice versa. This chunk currently contains 1,079 of each.
- Diff this chunk against AMD's authoritative DCN 4.1.0 register database and nearby generated headers such as `dcn_3_5_1_sh_mask.h`, `dcn_3_6_0_sh_mask.h`, and `dcn_4_2_0_sh_mask.h` where field compatibility is expected.
- Exercise DP0 and DP1 links independently: link training, lane-count changes, FEC, fast training, MST payload allocation, MSE SAT updates, secondary-data packets, ALPM wake/sleep, panel replay, and suspend/resume.
- Exercise HDMI/TMDS paths on DIG0: deep color, scrambling, metadata packets, audio/ACR generation, generic/infoframe packets, Dolby Vision metadata where supported, output CRC, TMDS test/control symbols, and error interrupt handling.
- Exercise HDCP 1.x authentication over HDMI and DP, including link0/link1 status, retry/timeout/NACK paths, deauthentication, repeaters, protected playback start/stop, and resume.
- Watch kernel logs and display diagnostics for link-training failures, packet deadline misses, stuck pending bits, AUX/DDC/HDCP I2C failures, audio dropouts, CRC mismatches, hotplug/resume regressions, MST allocation failures, and ALPM wake issues.

## Cross-Chunk Notes

Earlier chunks own the beginning of the OTG3 timing-generator and surrounding DCN 4.1.0 register-field namespace. Later chunks continue the `DP1` field block after `DP1_DP_MSO_CNTL1` and likely cover the remaining repeated DIO/DIG/DP instances. The final per-file report should merge adjacent chunk reports before making complete claims about all DCN 4.1.0 timing generators, display encoders, DP links, HDMI paths, or HDCP register coverage.
