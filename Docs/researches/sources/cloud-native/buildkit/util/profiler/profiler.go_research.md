## sources/cloud-native/buildkit/util/profiler/profiler.go

Purpose: attaches hidden profiling flags to a urfave CLI command and starts/stops requested profile collectors around command execution.

Important API: `Attach(app *cli.Command)` mutates flags and wraps `Before`/`After` hooks. Hidden flags include CPU, memory, memory rate, block, mutex, and trace profile paths.

Control flow: wrapped `Before` calls any existing hook first, then starts each requested profile via `pkg/profile.Start` with `NoShutdownHook`, storing stoppers. Wrapped `After` calls existing hook first, then stops all stoppers.

State/persistence: process-global profiling side effects and profile files under requested paths. `stoppers` slice is captured in `Attach` closure. Dependencies: `pkg/profile`, urfave/cli v3.

Integration points: BuildKit command binaries can opt into hidden profiling flags. Risks: if existing `After` returns error, stoppers are not stopped; repeated command executions on the same attached command may accumulate stoppers; profile path semantics are delegated to pkg/profile. Test signals: no local tests.
