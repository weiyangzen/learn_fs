# sources/cloud-native/cri-o/pkg/config/config_unix.go

This platform-specific source provides default CRI-O paths for non-Windows, non-FreeBSD builds. It is configuration data, not executable control flow. The constants define CNI config and binary directories, conmon exit and attach socket directories, the primary config file and drop-in directory, the CRI-O socket path, the temporary version file, and the clean shutdown marker.

These constants feed `DefaultConfig` and related default config initialization in the broader package. State/persistence implications are significant because the paths point at daemon state on disk: `/var/run/crio` for sockets, exit files, and temporary version state, `/var/lib/crio/clean.shutdown` for durable shutdown state, and `/etc/crio` for operator-managed config. Dependencies are limited to build tags and the package namespace.

Risks are path compatibility and distro packaging assumptions. Any change here affects default daemon startup, config discovery, wipe behavior, and kubelet socket integration on Linux-like systems. Tests in this subset validate behavior built on these defaults through `DefaultConfig`, validation, template generation, and reload tests rather than this file directly.
