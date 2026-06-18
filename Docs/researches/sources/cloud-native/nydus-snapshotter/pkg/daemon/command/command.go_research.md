# Research: sources/cloud-native/nydus-snapshotter/pkg/daemon/command/command.go

This file implements a reflection-based command-line builder for launching `nydusd`. `DaemonCommand` declares supported subcommand, parameter, and flag fields using struct tags. `BuildCommand` applies option functions, scans the tagged fields in struct order, appends non-zero parameters as `--name value`, appends boolean flags when true, and prepends the subcommand.

Important option helpers include `WithMode`, `WithFscacheDriver`, `WithFscacheThreads`, `WithThreadNum`, `WithConfig`, `WithBootstrap`, `WithMountpoint`, `WithAPISock`, `WithLogFile`, `WithLogLevel`, `WithLogRotationSize`, `WithSupervisor`, `WithID`, `WithUpgrade`, `WithBackendSource`, `WithPrefetchFiles`, and `WithFailoverPolicy`. The builder is consumed by `pkg/manager/daemon_adaptor.go` to translate daemon state and configuration into an `exec.Cmd`.

The main dependency is Go reflection plus `strconv` for numeric string conversion. There is no persistence; state lives only in the temporary `DaemonCommand`. Risks are tag-sensitive: field order defines argument order, zero values silently omit parameters, non-bool `flag` tags fail at runtime, and invalid tag types are runtime errors. The unit test checks expected ordering for singleton fscache command construction with and without `--upgrade`, but not every option or error path.
