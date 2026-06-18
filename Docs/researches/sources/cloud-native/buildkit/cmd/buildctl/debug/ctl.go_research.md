# Research: sources/cloud-native/buildkit/cmd/buildctl/debug/ctl.go

Purpose: implements `buildctl debug ctl`, a command for mutating build history records by pinning, unpinning, or deleting a reference.

Important APIs and flow: `CtlCommand` defines `--pin`, `--unpin`, and `--delete`. `ctl` requires a build ref argument, resolves the BuildKit client, validates that exactly one operation mode is selected, and calls `ControlClient().UpdateBuildHistory` with `Pinned` or `Delete` fields.

State and dependencies: this command mutates daemon history state stored by the control service, not local files. It depends on `controlapi.UpdateBuildHistoryRequest`, shared client resolution, and app context.

Risks and test signals: validation prevents contradictory flags, but delete is irreversible at daemon history level. There are no direct unit tests for this command in the listed files; history mutation is indirectly covered by control service behavior and debug CLI use.
