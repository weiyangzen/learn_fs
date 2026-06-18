# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/lmac_common.h

## Purpose
Defines common per-LMAC and per-MAC state shared by CGX and RPM MAC drivers, abstracting differences in register offsets, interrupts, lane layout, stats counts, pause/PTP/FEC/reset operations, and LMAC discovery.

## Important APIs, Types, and Functions
`struct lmac` stores command completion wait state, command serialization lock, firmware response, link info, MAC filter bitmap, RX/TX flow-control bitmaps, event callback state, parent `cgx`, multicast filter count, LMAC ID/type, pending-command flag, and name. `struct mac_ops` is the CGX/RPM operation table for LMAC discovery, stats, pause/PFC/PTP, RX/TX enable, reset, FEC, X2P reset, and RX enable. `struct cgx` stores PCI/MMIO identity, LMAC mapping, command workqueue, list linkage, feature bits, ops pointer, enabled-LMAC bitmap, and CSR lock. Declared helpers include `cgx_write`, `cgx_read`, `lmac_pdata`, `cgx_fwi_cmd_send`, `cgx_fwi_cmd_generic`, `is_lmac_valid`, and `rpm_get_mac_ops`.

## Control Flow
No executable flow is present. Runtime MAC code uses the structs to serialize firmware commands, dispatch link events, and call device-specific methods through `mac_ops`.

## State and Persistence Behavior
LMAC state persists per physical port and caches link state, firmware command response state, filter/flow-control bitmaps, callback registration, and identity. `cgx` state persists per MAC block and owns MMIO base, workqueue, ops, feature flags, and LMAC map.

## Dependencies and Integration Points
Includes `rvu.h` and `cgx.h`. It is consumed by CGX/RPM implementations and AF mailbox handlers for link, MAC filters, flow control, PTP, PFC, FEC, and stats.

## Risks
The header is an abstraction boundary between similar MAC blocks. Missing or incorrect `mac_ops` callbacks can lead to NULL calls or unsupported features. Command and event locks must match implementation code. `MAX_LMAC_COUNT` and bitmap assumptions must match hardware generations.

## Test Signals
CGX/RPM probe, LMAC discovery, firmware command timeout/completion, link event register/unregister, RX/TX start/stop, MAC filter operations, pause/PFC/PTP/FEC, stats reset/read, internal loopback, X2P reset, remove with pending events, and invalid LMAC ID rejection.
