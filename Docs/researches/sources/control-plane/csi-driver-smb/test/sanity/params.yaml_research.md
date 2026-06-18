# sources/control-plane/csi-driver-smb/test/sanity/params.yaml

## Purpose
This YAML provides CSI sanity test volume parameters for the SMB driver.

## Important APIs, Types, And Functions
The single parameter is `source: //127.0.0.1/share`.

## Control Flow
There is no code flow. `csi-sanity` reads the file via `--csi.testvolumeparameters`.

## State, Persistence, And Dependencies
The value assumes a local Samba server exposing a `share` over SMB on localhost, which is provisioned by `test/sanity/run-test.sh`.

## Integration Points
It integrates with SMB driver CreateVolume/NodeStage behavior during CSI sanity tests.

## Risks And Test Signals
The file is intentionally minimal; any additional driver parameters must come from test defaults or secrets. The test signal is whether CSI sanity can create and stage volumes using this source.
