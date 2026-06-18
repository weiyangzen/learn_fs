<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/loopDevicePV.sh -->
# sources/control-plane/rook/tests/scripts/loopDevicePV.sh

Purpose: creates block-mode local PVs pointing at `/dev/loopN` devices for loop-device OSD tests.

Important APIs and control flow: reads OSD count from the first argument, loops from 1 to that count, and applies a PV named `local-vol-loop-dev<N>` with `manual` StorageClass, 6Gi capacity, block volume mode, local path `/dev/loop<N>`, and node affinity for `rook.io/has-disk=true`.

State, persistence, and integration: creates PV resources that bind to later PVCs. Dependencies include pre-created loop devices, a labeled node, and `kubectl`. Risks include no argument validation, fixed PV names, and assumption that loop devices are safe and available. Test signals are PV listing and later PVC/OSD binding.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/loopDevicePV.sh -->
