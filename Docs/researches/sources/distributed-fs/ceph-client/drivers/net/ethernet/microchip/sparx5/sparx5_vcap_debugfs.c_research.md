# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_vcap_debugfs.c

## Purpose
`sparx5_vcap_debugfs.c` provides Sparx5-specific debugfs reporting for VCAP port classification state. It prints which key selection modes are programmed for each VCAP lookup on a netdev port and reports, then clears, sticky bits that show which classifier key types have been selected by hardware.

## Important APIs, Types, and Functions
- `sparx5_port_info()` is the exported callback installed in `sparx5_vcap_ops.port_info`.
- IS0 helpers translate etype/MPLS/MLBS selector values to strings and print `ANA_CL_ADV_CL_CFG` lookup state.
- `sparx5_vcap_is2_port_keys()` prints IS2 enable bits and key selection from `ANA_ACL_VCAP_S2_CFG` and `ANA_ACL_VCAP_S2_KEY_SEL`.
- `sparx5_vcap_is2_port_stickies()` reads `ANA_ACL_SEC_LOOKUP_STICKY`, prints classifier sticky flags, and writes the same value back to clear them.
- `sparx5_vcap_es0_port_keys()` reports ES0 global enable and per-port key mode from `REW_ES0_CTRL` and `REW_RTAG_ETAG_CTRL`.
- `sparx5_vcap_es2_port_keys()` and `sparx5_vcap_es2_port_stickies()` report ES2 selectors and sticky flags from EACL registers.

## Control Flow
Debugfs calls enter `sparx5_port_info(ndev, admin, out)`. The function resolves `struct sparx5_port` from the netdev, obtains the VCAP name from `sparx5->vcap_ctrl`, prints the VCAP stage name, and switches on `admin->vtype`. Each stage-specific helper loops over configured lookups, reads the relevant register fields, and emits formatted text through the callback in `struct vcap_output_print`.

## State and Persistence Behavior
Most helpers are read-only diagnostics, but the IS2 and ES2 sticky printers have side effects: after reading sticky registers, they write the read value back, which clears the latched bits. The file does not maintain in-memory state. Its output reflects current hardware register programming and transient sticky events since the previous clear.

## Dependencies and Integration Points
It depends on Sparx5 register macros, `spx5_rd()`/`spx5_wr()`, VCAP enum values from the generated model, `struct vcap_admin`, and the generic VCAP debugfs callback interface. `sparx5_vcap_debugfs.h` compiles this file's public callback only when `CONFIG_DEBUG_FS` is enabled, and `sparx5_vcap_impl.c` registers it in the VCAP operations table.

## Risks and Edge Cases
- Reading debugfs clears sticky bits, so diagnostic access can consume evidence needed by another troubleshooting session.
- Switch statements generally omit default output inside nested selector printers; unknown hardware values may be silent or appear as generic `unknown` only for IS0 helper functions.
- The output assumes `netdev_priv(ndev)` is a valid `struct sparx5_port`; misuse with non-Sparx5 netdevs would be unsafe.
- Register field interpretations must stay synchronized with key selection programming in `sparx5_vcap_impl.c`.

## Test Signals
- Build with and without `CONFIG_DEBUG_FS` to verify real callback and stub behavior.
- Debugfs smoke tests should read port info for IS0, IS2, ES0, and ES2 and confirm stage names and lookup counts.
- Sticky-bit tests should inject or observe hardware stickies and verify a first read reports them and a second read no longer does.
- Selector programming tests should compare debugfs output before and after `sparx5_vcap_set_port_keyset()`.
