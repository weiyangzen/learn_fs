# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_dcb.c

## Purpose

`cxgb4_dcb.c` implements Data Center Bridging and DCBX support for the Chelsio `cxgb4` Ethernet driver when `CONFIG_CHELSIO_T4_DCB` is enabled. It is the driver-side bridge between firmware DCB messages, the per-port `struct port_dcb_info` cache, and Linux DCB netlink operations exposed through `struct dcbnl_rtnl_ops`.

The file supports both firmware-managed DCBX and host-managed DCBX. Firmware events drive a small state machine, populate priority-group, priority-flow-control, and application-priority state, and then the DCBNL callbacks translate Linux CEE/IEEE requests into Chelsio firmware mailbox reads/writes.

## Important APIs, Types, And Functions

- `dcb_ver_array[]` maps firmware DCB version ids to log strings. It is exported via the header for diagnostics such as debugfs DCB information.
- `cxgb4_dcb_state_init()` clears a port's `struct port_dcb_info`, preserves a previously selected DCB version, and moves the state to `CXGB4_DCB_STATE_START`.
- `cxgb4_dcb_version_init()` defaults the per-port DCBX version request to `FW_PORT_DCB_VER_AUTO`.
- `cxgb4_dcb_reset()` removes registered DCB application mappings and reinitializes DCB state, typically after link-down or firmware de-sync.
- `cxgb4_dcb_state_fsm()` is the central state machine. Inputs are firmware disabled, firmware enabled, firmware incomplete, and firmware all-synced events. It transitions among start, host, firmware-incomplete, and firmware-all-synced states and fires `linkwatch_fire_event()` when externally visible DCB state changes.
- `cxgb4_dcb_handle_fw_update()` consumes `struct fw_port_cmd` DCB payloads from firmware. Control messages drive the FSM; data messages update PGID, PGRATE/TSA, PRIORATE, PFC, and application-priority caches.
- `cxgb4_dcb_ops` is the exported DCBNL operation table. It wires IEEE callbacks (`ieee_getets`, `ieee_getpfc`, `ieee_getapp`, `ieee_setapp`, peer ETS/PFC) and CEE callbacks (`getpgtccfg*`, `setpgtccfg*`, `getpfccfg`, `setpfccfg`, app table, peer app table, peer PG/PFC).
- The internal helpers `INIT_PORT_DCB_*_CMD()` are used throughout to form `FW_PORT_CMD` mailbox commands for local, peer, sync, and write DCB actions.
- `bitswap_1()` from the header is used to convert firmware PFC bit ordering to the IEEE/CEE representation expected by the kernel.

## Control Flow

Initialization starts in the main driver by calling `cxgb4_dcb_version_init()` and `cxgb4_dcb_state_init()` for each netdev/port. At this point the port has no active negotiated DCB information.

Firmware DCB control updates enter through `cxgb4_dcb_handle_fw_update()`. For `FW_PORT_DCB_TYPE_CONTROL`, the code decodes the `ALL_SYNCD` bit into either `CXGB4_DCB_INPUT_FW_ALLSYNCED` or `CXGB4_DCB_INPUT_FW_INCOMPLETE`. If the current requested version is not unknown, it also reads the running firmware DCB version from `dcb_version_to_app_state`, accepts CEE 1.01 or IEEE, logs the negotiated version, and marks unknown on mismatch. The state machine then updates the per-port state.

Non-control firmware DCB updates are rejected if the port is still in `START` or host-managed state. Otherwise the switch on firmware DCB type updates the per-port cache:

- `FW_PORT_DCB_TYPE_PGID` stores the firmware priority-group map and marks `CXGB4_DCB_FW_PGID`.
- `FW_PORT_DCB_TYPE_PGRATE` stores supported traffic classes, per-PG bandwidth, TSA values, and may fake IEEE sync once PGID is already known.
- `FW_PORT_DCB_TYPE_PRIORATE` stores strict priority rates.
- `FW_PORT_DCB_TYPE_PFC` stores PFC enablement and max PFC TCs and may fake IEEE sync.
- `FW_PORT_DCB_TYPE_APP_ID` translates firmware selector/priority representation to `struct dcb_app`, registers it with either `dcb_ieee_setapp()` or `dcb_setapp()`, stores the firmware table entry in `dcb->app_priority[]`, and marks the app message bit.

DCBNL get paths either return cached state or issue firmware mailbox reads for fresh local/peer values. Priority-group callbacks read PGID and PGRATE, convert the firmware's reversed TC order where needed, and expose bandwidth/priority-type fields. PFC callbacks read or update the cached `pfcen` bitmap and use firmware write commands for changes. App callbacks search the firmware APP table, use empty protocol id as end-of-table, and translate CEE and IEEE selector/priority encodings.

DCBNL set paths mostly write firmware DCB subcommands. PGID/PGRATE updates read the current firmware table, update one nibble or bandwidth entry, then write back. PFC writes update the `FW_PORT_DCB_TYPE_PFC` payload and update the software cache only after firmware success. App writes locate an existing or empty table slot, emit `FW_PORT_DCB_TYPE_APP_ID`, optionally set `FW_PORT_CMD_APPLY_F` for host-managed state, and then register the app in the kernel DCB app table.

## State And Persistence

The durable in-memory state lives in `struct port_dcb_info` embedded in each `struct port_info`. It caches:

- FSM state and DCBNL capability mask.
- `enabled` flag visible through `getstate()`.
- received firmware message bitmap.
- negotiated DCBX version.
- PGID, PFC enable bitmap, supported TC counts, bandwidth rates, priority rates, TSA values.
- up to eight firmware application-priority entries.

Firmware is the persistent source of truth for actual DCB configuration. The driver cache is reset on `cxgb4_dcb_reset()` and repopulated from firmware updates or explicit mailbox reads. Link transitions matter: `__cxgb4_setapp()` rejects app writes when carrier is down because DCB info is discarded on link-up. Host-managed writes set `FW_PORT_CMD_APPLY_F` to push changes immediately.

The Linux DCB app tables are also updated as side effects through `dcb_setapp()`, `dcb_ieee_setapp()`, `dcb_ieee_delapp()`, and `dcb_setapp()` with priority zero for cleanup. This means software-visible state spans both the Chelsio per-port cache and the kernel DCB app registry.

## Dependencies And Integration Points

- Requires `CONFIG_CHELSIO_T4_DCB`; otherwise the header provides no-op initialization.
- Depends on `cxgb4.h` for `struct adapter`, `struct port_info`, `netdev2pinfo()`, port/channel mapping, and firmware mailbox helpers.
- Uses Chelsio firmware APIs and constants from `t4fw_api.h`, especially `FW_PORT_CMD`, `FW_PORT_DCB_TYPE_*`, and DCB version/capability fields.
- Uses `t4_wr_mbox()` to synchronously read/write firmware DCB state.
- Integrates with Linux DCBNL through `struct dcbnl_rtnl_ops`.
- Uses `linkwatch_fire_event()` to notify the networking core when DCB sync state affects link-visible behavior.
- Uses kernel DCB app helpers (`dcb_setapp`, `dcb_ieee_setapp`, `dcb_ieee_getapp_mask`, `dcb_ieee_delapp`) to keep the OS registry aligned.
- Debug output is consumed by `cxgb4_debugfs.c` when `dcb_info` is enabled.

## Risks And Edge Cases

- Firmware DCB events received in `START` or `HOST` state are logged and ignored. If event ordering changes, the driver may fail to populate DCB state.
- Version mismatch handling logs a warning and sets version unknown; later code indexes `dcb_ver_array` by firmware-provided ids, so invalid firmware version values would be risky if they escape expected enum ranges.
- Several setter callbacks return `void` due to DCBNL API shape and can only log firmware failures; callers may not get precise failure propagation for PG/PFC changes.
- App table handling is capped at `CXGB4_MAX_DCBX_APP_SUPPORTED` eight entries and returns `-EBUSY` when full.
- IEEE app priority conversion uses `ffs(prio) - 1`; empty priority masks can produce `-1` if not guarded by successful firmware/kernel app lookup.
- DCB write paths depend on carrier state and firmware state; attempts during link transitions can return `-ENOLINK` or silently expose stale cached values until firmware refreshes.
- The code assumes firmware bit ordering for PFC differs from spec and corrects with `bitswap_1()` in some paths; inconsistent use would produce reversed priority reporting.

## Test Signals

Useful validation signals include:

- Build coverage with `CONFIG_CHELSIO_T4_DCB=y` and without it to confirm the header stubs and operation table references are correct.
- DCBNL queries via `dcbtool` or `lldptool` for CEE and IEEE modes, checking PG, PFC, app, peer app, and DCBX capability reporting.
- Firmware event injection or hardware link tests that cover `START -> FW_INCOMPLETE -> FW_ALLSYNCED`, de-sync back to incomplete, and host-managed mode.
- App table set/get/delete tests for ethertype and port selectors, including full-table behavior.
- Link down/up tests to confirm `cxgb4_dcb_reset()` clears app registrations and that firmware repopulates state.
- Debugfs `dcb_info` inspection for negotiated version, state, PG/PFC/app values, and message bit progression.
