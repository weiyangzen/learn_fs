## sources/control-plane/rook/cmd/rook/util/doc.go

Purpose: package documentation for `cmd/rook/util`, stating that it contains top-level utility commands that are neither storage backends nor tied to a specific backend.

Important APIs and functions: no exported runtime symbols beyond the package declaration. The meaningful command in this subset is `CmdReporterCmd` in `cmdreporter.go`.

Control flow, state, and persistence: none. It affects Go documentation and package organization only.

Dependencies and integration points: no imports. It gives maintainers a place to add utility commands without conflating them with Ceph backend commands or user-facing command groups. Risks and tests are minimal; any behavior risk belongs to concrete files in the package.
