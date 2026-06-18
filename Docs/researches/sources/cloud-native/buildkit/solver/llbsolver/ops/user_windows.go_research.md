# sources/cloud-native/buildkit/solver/llbsolver/ops/user_windows.go

Purpose: Windows-specific file operation user resolution that maps a username to a Windows SID for fsutil copy ownership.

Important APIs/types/functions: `getReadUserFn` and `readUser`. The returned closure captures the worker so it can access the executor for SID resolution.

Control flow: nil chown returns nil. If a named user is present, the user mountable is mounted, `windows.ResolveUsernameToSID` resolves the name against root mounts using the worker executor, and a `copy.User{SID: sid}` is returned. Other user forms/defaults return the Container Administrator SID.

State/persistence: no persistence. Root mounts are released through the mount release callback.

Dependencies/integration: file backend ownership resolution, snapshot mountables, `util/windows`, worker executor, and fsutil copy user model.

Risks: group is ignored on Windows (`mg` is unused). Missing user mount for named lookup is fatal. Defaulting to Container Administrator is platform-specific and must align with Windows container filesystem expectations.

Test signals: no direct tests in this subset; Windows behavior is likely covered by platform-specific file backend tests.
