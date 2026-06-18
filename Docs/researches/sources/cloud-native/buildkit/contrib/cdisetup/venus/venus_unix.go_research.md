# Research: sources/cloud-native/buildkit/contrib/cdisetup/venus/venus_unix.go

Purpose: implements experimental on-demand CDI setup for Docker Desktop Virtio-GPU Venus devices on non-Windows platforms.

Important APIs and flow: init registers `docker.com/gpu`. `Validate` gets the kernel version, requires it to contain `linuxkit`, checks `/dev/dri`, and requires `renderD128` and `card0`. `Run` validates again, writes a fixed CDI YAML spec naming device `venus` with those DRI device nodes, and creates `/etc/cdi` as needed. `getKernelVersion` calls `unix.Uname` and trims the NUL-terminated release string.

State and persistence: reads kernel/device files and writes `/etc/cdi/venus.yaml` with mode 0600. Depends on CDI setup registration, unix uname, and filesystem state.

Risks and test signals: validation is tightly coupled to Docker Desktop/LinuxKit device naming and will reject other Virtio-GPU environments. There are no direct tests in this subset.
