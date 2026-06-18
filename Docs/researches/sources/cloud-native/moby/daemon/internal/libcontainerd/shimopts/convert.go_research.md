<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/shimopts/convert.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/shimopts/convert.go

Purpose: converts generic daemon runtime option maps into containerd shim option protobuf structs that can be typeurl-marshaled by the containerd client.

Important APIs and types: `Generate(runtimeType string, opts map[string]any) (any, error)`.

Control flow: selects an output struct based on runtime type: runc v2 options, runhcs v1 options, or generic runtimeoptions. It TOML-marshals the map and TOML-unmarshals into the selected struct to handle loose numeric/map conversion.

State and persistence: no persistent state; pure conversion.

Dependencies and integration: depends on hcsshim runhcs options, containerd runc/runtimeoptions, containerd plugin runtime constants, and `go-toml/v2`. Its output is passed to `containerd.WithRuntime`.

Risks: TOML round-tripping can reject field names/types differently than JSON/YAML config paths. Unknown runtime types get generic options, which may silently ignore runtime-specific fields.

Test signals: no direct tests in this subset; runtime option coverage is integration-driven.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/shimopts/convert.go -->
