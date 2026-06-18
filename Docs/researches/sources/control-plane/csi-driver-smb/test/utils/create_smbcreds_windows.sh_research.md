# sources/control-plane/csi-driver-smb/test/utils/create_smbcreds_windows.sh

## Purpose
This script creates the `smbcreds` Kubernetes Secret needed by Windows host-process SMB tests.

## Important APIs, Types, And Functions
It decodes base64-encoded `username` and `pwd` values, deletes any existing `smbcreds` secret in `default`, and recreates it with username, password, and mount options.

## Control Flow
With `set -e`, it decodes credentials, runs `kubectl delete secret smbcreds --ignore-not-found`, then runs `kubectl create secret generic` with literal values.

## State, Persistence, And Dependencies
It mutates the default namespace by replacing a Secret. Dependencies include base64, kubectl, and a valid cluster context.

## Integration Points
`suite_test.go` invokes this for Windows host-process deployments before rewriting SMB source to an Azure File endpoint.

## Risks And Test Signals
The script embeds encoded credential material and uses unquoted shell expansions. It overwrites any existing default `smbcreds`. Signal is kubectl exit status.
