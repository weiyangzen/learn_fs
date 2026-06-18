# File Research: sources/block-storage/thin-provisioning-tools/src/pack/mod.rs

This module file exposes pack subsystem modules.

Public modules:
- `node_encode`
- `toplevel`
- `vm`

Private module:
- `delta_list`

Integration points:
- `spindle.rs` and `pack/toplevel.rs` use node encoding and VM packing to compact metadata blocks.
