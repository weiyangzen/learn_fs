# sources/control-plane/csi-driver-nfs/pkg/nfs/version.go

Purpose: reports build and runtime version metadata for logs and identity responses.

Important APIs and types: build-time variables `driverVersion`, `gitCommit`, and `buildDate`; `VersionInfo`; `GetVersion`; and `GetVersionYAML`.

Control flow: `GetVersion` constructs a `VersionInfo` from the requested driver name, ldflag-populated build variables, and Go runtime metadata. `GetVersionYAML` marshals that structure with `sigs.k8s.io/yaml` and trims surrounding whitespace.

State and persistence behavior: all state is process-global build metadata and runtime information. No external state is read or written.

Dependencies and integration points: used by `NewDriver`, `Driver.Run`, and identity server version reporting. Depends on `runtime`, `fmt`, `strings`, and YAML marshaling.

Risks: default values are `N/A` unless build ldflags set them. YAML key names come from JSON tags with spaces, so downstream parsers should not assume Go field names.

Test signals: `version_test.go` verifies default `VersionInfo` construction and YAML output consistency with the same marshaller.
