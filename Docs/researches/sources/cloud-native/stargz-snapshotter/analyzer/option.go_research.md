# sources/cloud-native/stargz-snapshotter/analyzer/option.go

Purpose: Defines the functional options used to configure image access analysis runs.

Important APIs: `Option`, `SpecOpts`, `WithSpecOpts`, `WithTerminal`, `WithStdin`, `WithPeriod`, `WithWaitOnSignal`, `WithSnapshotter`, `WithWaitLineOut`, and `WithPreMonitor`. `SpecOpts` allows callers to provide OCI spec options and a cleanup callback based on the selected image and mounted rootfs.

Control flow: Each option mutates `analyzerOpts`; `Analyze` in the sibling analyzer package reads those fields to decide runtime duration, container IO, snapshotter, signal behavior, line-based termination, and whether to run a pre-container fanotify phase.

State and persistence: Only transient configuration. There is no I/O here.

Dependencies and integration: Couples analyzer configuration to containerd image and OCI spec option types. `cmd/ctr-remote/commands/optimize.go` constructs these options from CLI flags and sampler flags.

Risks: `WithTerminal` depends on `WithStdin`, but enforcement is performed by callers rather than this option package. Nil `SpecOpts` means analyzer must fall back to defaults.

Test signals: No direct tests in this file; coverage comes from optimize/analyzer command behavior.
