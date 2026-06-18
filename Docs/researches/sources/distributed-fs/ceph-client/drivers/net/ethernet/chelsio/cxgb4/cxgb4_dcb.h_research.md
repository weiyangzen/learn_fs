# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_dcb.h

## Purpose

`cxgb4_dcb.h` declares the Chelsio `cxgb4` DCB support contract. It defines DCB capability masks, firmware command-initialization macros, DCB state enums, firmware-message tracking bits, the per-port DCB cache structure, and the public DCB entry points used by the rest of the driver.

When `CONFIG_CHELSIO_T4_DCB` is disabled, the header collapses DCB initialization to a no-op and exposes `CXGB4_DCB_ENABLED false`, allowing common driver code to compile without DCB support.

## Important APIs, Types, And Constants

- `CXGB4_DCBX_FW_SUPPORT` combines CEE, IEEE, and `DCB_CAP_DCBX_LLD_MANAGED` for firmware-managed DCBX.
- `CXGB4_DCBX_HOST_SUPPORT` combines CEE, IEEE, and `DCB_CAP_DCBX_HOST` for host-managed DCBX.
- `CXGB4_MAX_PRIORITY` and `CXGB4_MAX_TCS` are aliases for `CXGB4_MAX_DCBX_APP_SUPPORTED`, currently eight.
- `INIT_PORT_DCB_CMD()` constructs a `struct fw_port_cmd` with operation, request/execution flag, port id, DCB action, and length. It is the common mailbox command initializer for the implementation.
- `INIT_PORT_DCB_READ_PEER_CMD()`, `INIT_PORT_DCB_READ_LOCAL_CMD()`, `INIT_PORT_DCB_READ_SYNC_CMD()`, and `INIT_PORT_DCB_WRITE_CMD()` specialize the generic initializer for firmware DCB read/write actions.
- `IEEE_FAUX_SYNC()` advances IEEE DCB state to all-synced when the firmware provides enough IEEE sub-state without a normal all-synced control transition.
- `enum cxgb4_dcb_state` describes per-port DCB state: start, host, firmware incomplete, firmware all-synced.
- `enum cxgb4_dcb_state_input` defines inputs accepted by the FSM.
- `enum cxgb4_dcb_fw_msgs` tracks which DCB data message types have been received: PGID, PGRATE, PRIORATE, PFC, APP_ID.
- `struct port_dcb_info` is the per-port cache used by DCBNL, debugfs, and firmware event handling.
- Public functions include `cxgb4_dcb_state_init()`, `cxgb4_dcb_version_init()`, `cxgb4_dcb_reset()`, `cxgb4_dcb_state_fsm()`, and `cxgb4_dcb_handle_fw_update()`.
- `cxgb4_dcb_ops` is the exported Linux DCBNL ops table.
- `bitswap_1()` reverses bits in a byte, used to convert firmware PFC priority bit ordering to the OS-visible representation.
- `dcb_ver_array[]` is declared for shared version-name reporting.

## Control Flow

The header is included from `cxgb4_dcb.c` and indirectly from common driver code through `cxgb4.h` integration. With DCB enabled, initialization code can call the declared state/version init routines, firmware event handling can call `cxgb4_dcb_handle_fw_update()`, and netdev setup can attach `cxgb4_dcb_ops` to expose DCBNL operations.

The command macros centralize mailbox command construction. Each call zeroes the command, fills `op_to_portid` with `FW_CMD_OP_V(FW_PORT_CMD)`, `FW_CMD_REQUEST_F`, either `FW_CMD_READ_F` or `FW_CMD_EXEC_F`, and the firmware port id, then fills `action_to_len16` with the DCB action and length. This avoids repeated open-coded firmware command setup in the implementation.

When DCB support is compiled out, only `cxgb4_dcb_state_init()` remains as an inline empty function. Code guarded by `CXGB4_DCB_ENABLED` or `CONFIG_CHELSIO_T4_DCB` should avoid referencing DCB-only declarations in that configuration.

## State And Persistence

`struct port_dcb_info` is the authoritative in-driver cache format. It persists for the life of a `struct port_info` and is reset/repopulated by the implementation. It stores both state-machine metadata and firmware-derived DCB content:

- `state`, `msgs`, `supported`, and `enabled`.
- `pgid`, `dcb_version`, `pfcen`, max PG/PFC TC counts.
- `pgrate[8]`, `priorate[8]`, and `tsa[8]`.
- `app_priority[8]`, each containing user priority map, selector field, and protocol id.

No on-disk persistence is defined here. Actual DCB configuration persists in firmware/hardware; this structure is the kernel runtime mirror.

## Dependencies And Integration Points

- Includes `<linux/netdevice.h>`, `<linux/dcbnl.h>`, and `<net/dcbnl.h>` for netdev and DCBNL types.
- Uses firmware command macros and constants from the broader `cxgb4` include graph, so this header expects to be included in contexts where `FW_PORT_CMD`, `FW_CMD_*`, `FW_LEN16`, and related fields are available.
- The fallback no-op path is controlled by `CONFIG_CHELSIO_T4_DCB`.
- `struct port_dcb_info` is embedded in `struct port_info`, linking this header to the main adapter/port object model.

## Risks And Edge Cases

- `CXGB4_MAX_PRIORITY` and `CXGB4_MAX_TCS` being aliases for the app-table size assumes all relevant DCB arrays are eight entries; changing app support without revisiting TC/priority semantics could introduce bounds bugs.
- `IEEE_FAUX_SYNC()` is a macro with side effects; callers must pass valid netdev and DCB pointers and understand it can trigger the FSM.
- `bitswap_1()` accepts `unsigned char` and returns `__u8`; callers must not use it for wider masks without truncation awareness.
- The disabled-DCB branch exposes only one no-op function. Any unguarded use of other DCB symbols will fail builds without `CONFIG_CHELSIO_T4_DCB`.

## Test Signals

- Compile-test with `CONFIG_CHELSIO_T4_DCB=y` and `n`.
- Static checks that every DCB mailbox command path uses the initializer macros and sets the expected sub-type before `t4_wr_mbox()`.
- Runtime DCB tests confirming `struct port_dcb_info` fields reported by debugfs match DCBNL outputs.
- Bit-order tests for `bitswap_1()` using representative PFC masks such as `0x80`, `0x01`, and mixed masks.
