# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_hdcp.c

## Purpose
Adapts the generic i915 HDCP engine to DisplayPort SST and MST transports. It implements HDCP 1.x and HDCP 2.2 message I/O over DP AUX, link-integrity checks, capability detection, and MST stream encryption hooks.

## Important APIs, types, and functions
- Exported entry point: `intel_dp_hdcp_init()`, which installs either the SST or MST `intel_hdcp_shim`.
- HDCP 1.x helpers read/write `An`, `Aksv`, `Bksv`, `Binfo/Bstatus`, `Bcaps`, `Ri'`, KSV FIFO, and `V'` parts over `drm_dp_dpcd_read/write()`.
- HDCP 2.2 message metadata is encoded in `struct hdcp2_dp_msg_data` and `hdcp2_dp_msg_data[]`, mapping message IDs to DP offsets, wait behavior, and read timeouts.
- HDCP 2.2 helpers include `intel_dp_hdcp2_write_msg()`, `intel_dp_hdcp2_read_msg()`, `intel_dp_hdcp2_wait_for_msg()`, `_intel_dp_hdcp2_get_capability()`, and `intel_dp_hdcp2_config_stream_type()`.
- MST-specific hooks include `intel_dp_mst_hdcp_stream_encryption()`, `intel_dp_mst_hdcp2_stream_encryption()`, remote capability reads through `connector->mst.port->aux`, and the `intel_dp_mst_hdcp_shim`.

## Control flow
For HDCP 1.x authentication, the shim writes `An`, triggers hardware-backed `Aksv` output by writing the Aksv DPCD address, reads receiver keys/status over AUX, detects repeaters via `Bcaps`, and checks link health from `DP_AUX_HDCP_BSTATUS`.

For HDCP 2.2, write operations strip the leading generic message ID because DP DPCD message windows do not include it, then write chunks bounded by `DP_AUX_MAX_PAYLOAD_BYTES`. Read operations wait for either a fixed timeout or CP_IRQ plus RXSTATUS readiness bits, optionally fetch receiver ID count first for repeater topology, read the message in AUX-sized chunks, enforce whole-message deadlines where configured, and restore the message ID into the caller buffer.

MST stream encryption toggles `TRANS_DDI_HDCP_SELECT`, waits for per-transcoder stream encryption status in HDCP or HDCP2 registers, and validates stream type fields around enable. MST HDCP2 link checks only perform port authentication checks for the connector marked as the repeater/authentication participant.

## State and persistence
Persistent state lives in `struct intel_hdcp` on the connector, including CP_IRQ counters, pairing state, repeater state, stream transcoder, and stream type data. This file updates `cp_irq_count_cached` after HDCP2 reads. Hardware state persists in HDCP/DDI registers and sink DPCD authentication windows until disabled or link reset.

## Dependencies and integration points
Depends on DRM HDCP constants/helpers, DP AUX/DPCD helpers, i915 HDCP core/shim interfaces, DDI register programming, `intel_de_wait_ms()`, MST topology AUX, and display version conditionals for stream status registers. Called from DP and MST connector initialization paths and later by the generic HDCP state machine.

## Risks
HDCP is timing-sensitive. Incorrect wait mode, CP_IRQ handling, partial AUX transfer handling, or message-size calculation can cause authentication failures. HDCP 2.2 receiver capability is retried because some monitors report bad first reads, so reducing retries can regress compatibility. MST stream encryption status differs by display generation, and wrong transcoder/pipe mapping can leave streams unencrypted or time out. The Aksv flow relies on the AUX transfer hook recognizing the DPCD address to emit secret hardware data.

## Test signals
Signals include HDCP enable success for DP SST and MST, CP_IRQ wait timeout debug logs, AUX read/write length failures, HDCP2 link status values such as reauth/link integrity/topology change, stream encryption timeout errors, and content-protection property transitions. Test matrices should include repeaters, MST branch devices, paired and unpaired HDCP2 receivers, and display version 30 stream-type status behavior.
