# sources/cloud-native/nydus/tests/bats/Makefile

Purpose: defines a BATS-based CI target for end-to-end container/image tests.

Important APIs/types/functions: includes `/usr/lib/os-release` or `/etc/os-release`, then defines target `ci`. The target runs `install_bats.sh` and executes six BATS suites with TAP formatting: Docker image build, nydusd compile, nydus snapshotter compile, container run with RAFS, container run with zran, and RAFS plus Linux compile.

Control flow: `make ci` first ensures BATS is installed, then invokes each `.bats` file sequentially. Any failing shell command stops make.

State and persistence: the Makefile itself persists no state, but the invoked tests build images/binaries and may affect local Docker/containerd/system state.

Dependencies and integration points: integrates with BATS, Docker/container runtimes, nydusd, nydus-snapshotter, and host OS release files. The included OS release variables may be used by invoked BATS scripts or inherited make context.

Risks: assumes Linux-like OS release paths. Sequential BATS invocations can leave partial environment if a later test fails. Requires elevated/container runtime environment not available in many developer shells.

Test signals: this is a top-level CI entry point for smoke and integration behavior beyond Rust unit tests. It is valuable for packaging/runtime validation rather than library-level correctness.
