# sources/cloud-native/moby/integration/container/run_linux_test.go

Purpose: Linux run-path tests spanning hostname/domainname, DNS, unprivileged networking sysctls, privileged devices, console size, alternate containerd shim runtimes, legacy MAC behavior, static IPs, workdir normalization, seccomp, writable cgroups, and shm size.

Important APIs and flow: Tests use `container.Run`, `Exec`, `ContainerLogs`, `daemon.New`, custom network helpers, raw legacy create requests, and `ContainerInspect`. They create host devices with `unix.Mknod`, symlink alternate shim names into PATH, create user networks/IPAM ranges, send deprecated `MacAddress` JSON for API v1.43, inject seccomp JSON, set `writable-cgroups`, and run a daemon with `--default-shm-size`.

State and dependencies: Heavy host integration includes local daemons, host `/dev`, containerd shim binaries, sysctls, cgroups, networks, and shm mounts. Many cases skip rootless, user namespace, remote, or non-Linux modes.

Risks and signals: This file is a broad run-time regression suite for runtime setup and API compatibility. It catches wrong namespace/sysctl/device setup, runtime lookup problems, security option parsing bugs, cgroup writability changes, and default shm-size persistence.
