# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fip.h

## Purpose

`fip.h` defines FNIC-specific FIP constants, FIP discovery state enums, VLAN list entries, packed FIP wire-frame layouts, and prototypes for `fip.c`. It connects FIP protocol structures from the kernel FC stack with FNIC's FDLS/iport state.

## Important APIs, Types, and Definitions

- FIP constants: all-FCF MAC, maximum FCoE size, VLAN/FCF timeout values, maximum solicitation constant, and descriptor-list lengths for discovery, VLAN requests, keepalives, and FLOGI.
- `enum fdls_vlan_state`: per-VLAN availability vs sent state.
- `enum fdls_fip_state`: FIP progression from init, VLAN discovery, FCF discovery, FLOGI started, to FLOGI complete.
- `struct fcoe_vlan`: list entry containing VLAN ID, solicitation count, and state.
- Packed wire structures: `fip_vlan_req`, `fip_vlan_notif`, `fip_vn_port_ka`, `fip_enode_ka`, `fip_cvl`, `fip_flogi_desc`, `fip_flogi_rsp_desc`, `fip_flogi`, `fip_flogi_rsp`, `fip_discovery`, and `fip_disc_adv`.
- FIP function prototypes for VLAN, FCF discovery, FLOGI, CVL, timers, and the global `fnic_fip_queue`.
- `fnic_debug_dump_fip_frame()`: debug-only FIP frame dump wrapper; compiles to a no-op without `FNIC_DEBUG`.

## Control Flow and Design Role

The header models the frames that `fip.c` allocates and sends or receives. VLAN request and discovery structures include Ethernet headers because they are transmitted as complete Ethernet/FIP frames. Response/notification structures start at the FIP header because receive handlers pass a pointer after the Ethernet header. FLOGI structures embed `fc_std_flogi` from `fdls_fc.h`, allowing FIP LS messages to carry FC login payloads.

## State and Persistence Behavior

The header defines in-memory state shapes but does not mutate them. `struct fcoe_vlan` entries persist in `fnic->vlan_list` between VLAN discovery response handling and FCF discovery attempts. `enum fdls_fip_state` values persist in `iport->fip.state` and drive timeout behavior. Packed FIP structures represent transient wire frames.

## Dependencies and Integration Points

`fip.h` includes `fdls_fc.h`, `fnic_fdls.h`, and `<scsi/fc/fc_fip.h>`. It is used by `fip.c` and by FNIC initialization/teardown code that declares FIP work queues and timers. It bridges standard kernel FIP descriptor types with FNIC-specific FCoE discovery and FDLS startup.

## Risks and Edge Cases

- Descriptor-list length constants must match the packed structures and FIP `fip_dlen` units.
- Flexible arrays in VLAN notification and CVL structures require receive handlers to validate FIP descriptor lengths before indexing.
- `struct fip_flogi_rsp` assumes the response descriptor and MAC descriptor order used by FCFs.
- Debug dump code assumes an Ethernet header followed by a FIP header and must only be called with full FIP Ethernet frames.

## Test Signals

Useful validation includes compile-time structure size checks by observation, packet capture comparison for VLAN request, discovery solicitation, FIP FLOGI, enode keepalive, VN keepalive, CVL parsing, debug-frame logging when enabled, and state transitions through all `fdls_fip_state` values.
