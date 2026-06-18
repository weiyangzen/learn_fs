# sources/cloud-native/cri-o/crictl.yaml

## Purpose
crictl client endpoint configuration for using CRI-O over its Unix socket.

## Important APIs, Types, and Functions
runtime-endpoint and image-endpoint both point at unix:///var/run/crio/crio.sock; timeout is 10.

## Control Flow
crictl reads this YAML and directs runtime/image RPCs to CRI-O.

## State and Persistence
No persistent state beyond config file.

## Dependencies
Depends on crictl schema and CRI-O socket path.

## Integration Points
Used by operators/tests invoking crictl against local CRI-O.

## Risks and Edge Cases
Socket path differs from some newer /run paths; stale config causes failed diagnostics.

## Test Signals
crictl info/images/ps against CRI-O validates it.
