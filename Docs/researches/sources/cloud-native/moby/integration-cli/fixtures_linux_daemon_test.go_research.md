## sources/cloud-native/moby/integration-cli/fixtures_linux_daemon_test.go

Purpose: builds or loads Linux-only fixture images used by daemon integration tests: `syscall-test` and `nnp-test` for syscall/seccomp/no-new-privileges scenarios.

Control flow: `ensureSyscallTest` and `ensureNNPTest` first protect the image and return if it already exists. If daemon OS differs from host OS, they delegate to Docker-build paths that load frozen Debian images. Otherwise they compile C fixtures with `gcc`, write a temporary Dockerfile, honor `DOCKER_BUILD_ARGS`, and run `docker build`. The NNP image sets a setuid bit; syscall image optionally builds a 32-bit exit binary on linux/amd64.

State includes protected images, temporary build dirs, compiled binaries, Dockerfiles, and frozen base image availability. Dependencies include local `gcc`, `debian:trixie-slim`, contrib fixture sources, and `load.FrozenImagesLinux`. Risks include typo-like tag mismatch in `ensureNNPTestBuild` (`npp-test`), cross-platform build slowness, missing compiler, and environment build args. Test signals are successful image existence/protection and build command success.
