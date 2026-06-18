# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/nsenter_test.go

Purpose: tests `Config.buildCommand` flag construction.

Important APIs and flow: tests cover missing target, minimal target, namespace booleans without file paths, namespace booleans with explicit file paths, and credential/directory flags such as follow-context, setgid, no-fork, preserve-credentials, root, setuid, and working directory.

State and persistence: no process execution; only command argument construction is inspected.

Dependencies and integration: protects the `nsenter` command contract used by `copyFromContainer` and `syncFilesystem`.

Risks and test signals: strong for argument assembly. It does not run `ExecuteContext`, so stdout/stderr streaming, cancellation, and process wait behavior are not validated here.
