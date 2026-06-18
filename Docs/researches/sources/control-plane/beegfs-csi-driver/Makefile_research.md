<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/Makefile -->
# sources/control-plane/beegfs-csi-driver/Makefile

## Purpose
The Makefile defines project build, packaging, license, and test behavior around Kubernetes CSI release-tools. It adds BeeGFS-specific multi-arch driver builds and `chwrap` tarball packaging.

## Important Targets and Variables
`CMDS` defaults to `beegfs-csi-driver`; `TEST_GO_FILTER_CMD` excludes e2e and operator tests from normal unit tests. `all` runs build, `build-chwrap`, and `bin/chwrap.tar`. `check-go-version` verifies installed Go matches `go.mod`. `generate-notices` and `test-licenses` use `go-licenses`. `build-%` builds a named command for each `BUILD_PLATFORMS` entry. `bin/chwrap.tar` invokes `cmd/chwrap/chwrap.sh` for each platform. `container`, `push`, and `push-multiarch` connect local artifacts to release-tools behavior. The file includes `release-tools/build.make`.

## Control Flow
Multi-platform targets parse semicolon-separated `BUILD_PLATFORMS` rows into OS, architecture, suffix, and image fields. Each row drives `go build` output naming and `chwrap` tar creation. License testing regenerates `NOTICE.md`, runs a policy check with explicit ignores, then fails if `NOTICE.md` has uncommitted changes.

## State and Persistence
Build outputs are written to `bin/`. `generate-notices` rewrites `NOTICE.md`. Release-tools included targets may produce images and other build artifacts. The Makefile itself does not persist configuration outside outputs.

## Dependencies and Integration Points
It depends on Go, `go tool go-licenses`, repository `release-tools/build.make`, `cmd/chwrap/chwrap.sh`, and Docker/release-tools targets. The Dockerfile expects names produced by this Makefile.

## Risks
The custom `build-%` target depends on `check-go-version-go`, likely provided by release-tools; a missing include would break it. `BUILD_PLATFORMS` must be passed explicitly for correct multi-arch suffixes. License exceptions are policy-sensitive. Unit testing deliberately skips e2e and operator packages, so CI must run those elsewhere.

## Test Signals
Signals include `make check-go-version`, `make all` with single and multi-platform settings, `make test-licenses`, normal `make test`, image build targets, and CI generated-code/notice checks.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/Makefile -->
