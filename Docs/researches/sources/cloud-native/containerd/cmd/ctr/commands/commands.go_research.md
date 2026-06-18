# sources/cloud-native/containerd/cmd/ctr/commands/commands.go

Purpose: provides shared flag sets and helper functions reused across `ctr` commands.

Important APIs/functions: exported flag groups `SnapshotterFlags`, `SnapshotterLabels`, `LabelFlag`, `RegistryFlags`, `RuntimeFlags`, `ContainerFlags`; `ObjectWithLabelArgs()`, `LabelArgs()`, `AnnotationArgs()`, `PrintAsJSON()`, and `WritePidFile()`.

Control flow: command packages append or consume these flag groups. Label parsing treats missing `=` as `true`; annotation parsing rejects missing `=`. `WritePidFile()` uses an atomic file writer after resolving an absolute path.

State and persistence: `WritePidFile()` writes a pid file atomically. Other helpers only parse CLI input or print JSON.

Dependencies/integration: containerd defaults, atomicfile helper, urfave/cli, JSON encoding.

Risks: `LabelArgs()` accepts empty keys and treats bare keys as true. `PrintAsJSON()` prints an error to stderr but still prints the marshaled string variable, which will be empty on marshal failure.

Test signals: no local tests in this subset; functions are exercised by command behavior elsewhere.
