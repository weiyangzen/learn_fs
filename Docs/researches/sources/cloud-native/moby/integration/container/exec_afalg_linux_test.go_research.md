# sources/cloud-native/moby/integration/container/exec_afalg_linux_test.go

Purpose: Linux security integration tests ensuring restricted socket families cannot be created by exec processes under the default security profile.

Important APIs and flow: Embedded C fixtures `af_alg.c`, `af_vsock.c`, and `socketcall.c` are copied into a Debian container, compiled with `gcc`, and executed as UID 1000. `compileAndExecSocketDenied` writes source via `ExecT`, compiles, runs the binary with `ExecCreateOptions.User`, and expects exit code 1 plus EPERM/EACCES output. The `socketcall_int80` path only runs on amd64 with AppArmor or SELinux and verifies AF_ALG denial while AF_INET still succeeds.

State and dependencies: The test installs packages with `apt-get` in a running `debian:trixie-slim` container. It depends on seccomp, LSM security options, Linux headers, compiler availability, and architecture-specific syscall behavior.

Risks and signals: It catches high-impact sandbox escapes or overblocking in seccomp/LSM socket filtering, especially the ia32 `int $0x80` compatibility path that seccomp cannot inspect by argument pointer.
