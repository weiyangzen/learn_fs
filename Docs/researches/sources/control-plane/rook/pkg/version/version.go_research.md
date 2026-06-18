# sources/control-plane/rook/pkg/version/version.go

Purpose: this file defines the package-level Rook version string used by binaries and tests that import `pkg/version`. Its only exported API is `var Version = "0.0.0"`, with the documented expectation that release builds override it through Go linker `-X`.

Important APIs/types/functions: no functions or custom types exist. The mutable exported `Version` variable is the integration point. Any package importing `github.com/rook/rook/pkg/version` can read it after build-time injection.

Control flow: none at runtime beyond global initialization. The default value is assigned during package init before dependents execute.

State and persistence behavior: state is in-process only. Persistence comes indirectly from build metadata embedded into the binary. Because it is a mutable global, tests or other code could change it in-process.

Dependencies and integration points: no imports. The file depends on build tooling to inject the real version and on consumers to tolerate the local default in unversioned/dev builds.

Risks: incorrect linker flags leave binaries reporting `0.0.0`. The mutable global has no validation, so accidental test mutation can leak within a process.

Test signals: test coverage should validate build/release pipelines rather than this file itself. Unit tests that rely on a specific version should account for the default local value.
