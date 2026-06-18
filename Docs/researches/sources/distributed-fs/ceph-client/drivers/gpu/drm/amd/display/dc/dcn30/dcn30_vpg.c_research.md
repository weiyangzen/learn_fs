# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_vpg.c

Purpose: Implements the DCN 3.0 VPG generic packet programming path. The VPG object is a hardware block used to write generic secondary data packets into double-buffered GSP memory and trigger either immediate or next-frame updates.

Important APIs/types/functions: `vpg3_update_generic_info_packet()` is the only behavior exposed through `struct vpg_funcs`; `vpg3_construct()` wires a `struct dcn30_vpg` to context, instance id, register table, shifts, masks, and the function table. The implementation depends on `struct dc_info_packet` headers `hb0..hb3` and payload `sb[]`, `REG_WAIT`, `REG_UPDATE`, `REG_SET_4`, and `REG_WRITE`.

Control flow: packet programming validates `packet_index <= 14`, waits for `VPG_GENERIC_CONFLICT_OCCURED` to clear, clears the conflict flag, sets `VPG_GENERIC_DATA_INDEX` to `packet_index * 9`, writes one header dword and eight payload dwords, then sets one of the per-slot update bits. Immediate updates go through `VPG_GSP_IMMEDIATE_UPDATE_CTRL`; deferred updates go through `VPG_GSP_FRAME_UPDATE_CTRL`.

State/persistence: The object persists only pointers to register metadata and base context. Runtime state is hardware register state: generic packet memory, conflict status, and update latches. The function does not retain a software copy of packets.

Dependencies/integration: Used by DCN3 VPG users through the `vpg` abstraction. It integrates with DC register helpers and the display core's info-packet generation path.

Risks: Invalid indexes assert but then fall through to default no-op update behavior; release builds may still program data index for out-of-range values. The payload is cast to `uint32_t *`, so callers must provide the expected packet layout and alignment. Poll timeout is a fixed local value with no error propagation.

Test signals: Exercise all valid packet slots, immediate and frame update modes, conflict-clear behavior, and header/payload dword ordering. Register-trace tests should verify data index increments by nine per packet.
