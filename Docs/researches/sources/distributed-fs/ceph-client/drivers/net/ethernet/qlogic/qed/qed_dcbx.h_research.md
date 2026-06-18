# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_dcbx.h

## Purpose

`qed_dcbx.h` declares the QED DCBX state model and public APIs used by the driver core, MCP event path, PF update path, and optional DCB netlink support. It defines MIB read selectors, protocol result data, configuration override flags, metadata for application protocol matching, and the per-HWFN DCBX cache.

## Important APIs, Types, and Functions

- `enum qed_mib_read_type` identifies operational, remote, local, remote LLDP, and local LLDP MIB reads.
- `struct qed_dcbx_app_data` stores per-protocol enable/update/priority/TC/VLAN0 behavior used for PF update ramrods.
- `struct qed_dcbx_set` stores pending/admin configuration, including override flags for state, PFC, ETS, APP, and DSCP config.
- `struct qed_dcbx_results` stores negotiated state for all `DCBX_MAX_PROTOCOL_TYPE` protocols plus PF ID and enabled state.
- `struct qed_dcbx_info` is the driver cache for LLDP local/remote data, local admin MIB, operational/remote MIBs, negotiated results, pending set data, last get data, and capability.
- `struct qed_dcbx_mib_meta_data` packages MIB target pointers, size, and MCP public memory address for copy helpers.
- Public APIs include `qed_dcbx_mib_update_event()`, allocation/free helpers, PF update copy helper, `qed_dcbx_get_priority_tc()`, and `CONFIG_DCB` get/config functions. `qed_dcbnl_ops_pass` exports the DCB netlink ops table to the Ethernet layer.

## Control Flow

Consumers allocate `p_dcbx_info`, handle MCP MIB events with `qed_dcbx_mib_update_event()`, use cached negotiated results to fill PF update ramrods, and query priority-to-TC mappings for packet/offload behavior. When DCB netlink is enabled, userspace-facing operations call the declared config functions to read current settings, stage overrides, and commit local-admin MIB updates.

## State and Persistence Behavior

The header's main state object, `struct qed_dcbx_info`, is transient driver memory. It mirrors firmware/MCP MIB data and pending admin settings but does not itself persist across device reload. Firmware-visible persistence is handled by writing local-admin DCBX MIBs and issuing MCP commands in the implementation.

## Dependencies and Integration Points

The header depends on QED core, HSI, hardware access, MCP public-memory definitions, and register addresses. It exposes data consumed by slowpath ramrods (`pf_update_ramrod_data`), protocol-specific offload code, and Linux DCB netlink integration through `struct qed_eth_dcbnl_ops`.

## Risks and Edge Cases

- Override flags define which parts of a staged config are meaningful; callers must set them correctly or changes will not be included in local-admin MIB generation.
- `DCBX_CONFIG_MAX_APP_PROTOCOL` bounds app-entry arrays in the QED config view.
- `qed_dcbx_get_config_params()` and `qed_dcbx_config_params()` only exist under `CONFIG_DCB`, so non-DCB builds must avoid those symbols.
- `qed_dcbx_get_priority_tc()` depends on a valid operational snapshot and falls back to `QED_DCBX_DEFAULT_TC` in implementation when unavailable.

## Test Signals

Compile with `CONFIG_DCB=y` and disabled, run MCP DCBX MIB update paths, verify PF update ramrod data matches `qed_dcbx_results`, exercise DCB netlink get/set operations, and validate priority-to-TC lookups before and after operational MIB changes.
