# sources/cloud-native/moby/integration/image/commit_test.go

Purpose: tests image commit behavior for environment inheritance and user-namespace ownership preservation.

Important APIs and helpers: `TestCommitInheritsEnv` and `TestUsernsCommit` use `ContainerCommit`, `ImageInspect`, container create/run helpers, sub-daemon user namespace remap, and `RunAttach`.

Control flow: environment inheritance commits a container with `ENV PATH=/bin`, inspects the image config, creates a second container from that image, commits with `ENV PATH=/usr/bin:$PATH`, and asserts expansion to `/usr/bin:/bin`. Userns test starts a userns-remapped daemon, creates a file owned by UID/GID 1000 in a container, commits the image, runs it, and checks `stat` output.

State and persistence: validates committed image configuration and filesystem layer ownership metadata. The userns case tests remapped storage and committed tar metadata surviving into a new container.

Dependencies and integration: depends on Linux user namespace kernel support, non-rootless local daemon, daemon harness, busybox/stat behavior, image commit, and image inspect.

Risks: skipped in Windows, remote, rootless, or missing userns environments. Environment expansion semantics are Dockerfile-like and must remain stable.

Test signals: verifies commit preserves expected config inheritance and file ownership under user namespace remapping.
