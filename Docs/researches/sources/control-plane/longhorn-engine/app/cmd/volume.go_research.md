# sources/control-plane/longhorn-engine/app/cmd/volume.go

## Purpose
Defines volume-level CLI commands: `info`, `expand`, `unmap-mark-snap-chain-removed`, and `frontend start|shutdown`.

## Important APIs, Types, and Functions
- `InfoCmd()`, `ExpandCmd()`, `UnmapMarkSnapChainRemovedCmd()`, `FrontendCmd()`, `FrontendStartCmd()`, `FrontendShutdownCmd()`.
- Helpers `info()`, `expand()`, `startFrontend()`, `shutdownFrontend()`, and `unmapMarkSnapChainRemoved()`.

## Control Flow
All helpers open a controller client, defer close, and call one controller RPC. `info` marshals `VolumeGet` as indented JSON. `expand` reads `--size` as int64. `frontend start` requires a frontend name positional arg. The unmap mark command requires exactly one of `--enable` or `--disable`.

## State and Persistence Behavior
`info` is read-only. `expand` changes volume size and triggers controller/replica expansion workflows. Frontend start/shutdown changes exposed block device/socket state. Unmap mark toggles controller behavior for removing snapshot chains during unmap.

## Dependencies and Integration Points
Uses controller client APIs and logrus. Integration helpers `info_get` and `set_unmap_mark_snap_chain_removed` wrap these commands. Data tests verify frontend device creation, endpoint reporting, and frontend switching.

## Risks and Edge Cases
`expand` does not locally reject zero or shrinking sizes; controller must enforce. Unmap mark command rejects both/no flags. Frontend start validates missing name but frontend type validity is server-side.

## Test Signals
`integration/data/test_basic_ops.py` validates `info` endpoint output, device creation, metrics after IO, and cleanup of leftover block devices. `test_frontend.py` validates no-frontend start/shutdown persistence. Expansion is tested in `test_controller.py` and `test_cli.py`.
