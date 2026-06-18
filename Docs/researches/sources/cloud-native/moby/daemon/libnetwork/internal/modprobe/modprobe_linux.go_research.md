# Research: sources/cloud-native/moby/daemon/libnetwork/internal/modprobe/modprobe_linux.go

Purpose: attempts to load Linux kernel modules with a docker-in-docker-friendly fallback strategy. Important APIs/types are `LoadModules`, internal `tryLoad`, `loader`, `ioctlLoader`, and `modprobeLoader`.

Control flow: `LoadModules` first calls `isLoaded`; if already loaded it logs and returns. Otherwise it tries `ioctlLoader`, which opens an AF_INET datagram socket and issues `SIOCGIFINDEX` on an ifreq named after each module, relying on kernel autoload behavior and ignoring the ioctl error. If `isLoaded` still fails, it tries `modprobeLoader`, which runs `modprobe -va` for each module. `tryLoad` logs load errors and final check result; the returned error is the last `isLoaded` failure.

State/dependencies: no persistent state. Dependencies include Linux unix syscalls, `os/exec`, context logging, and caller-supplied loaded checks. Integration points are firewall/network features that need kernel modules. Risks include CAP_SYS_MODULE requirements, external command availability, module names doubling as interface names, and losing individual load errors if final check succeeds. Test signal is not local.
