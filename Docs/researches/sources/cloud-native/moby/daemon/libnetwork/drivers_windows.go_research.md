# Research: sources/cloud-native/moby/daemon/libnetwork/drivers_windows.go

Purpose: registers Windows libnetwork drivers and provides a Windows no-op portmapper registration hook. Important APIs are `registerNetworkDrivers` and `registerPortMappers`.

Control flow: network registration first installs the null and Windows overlay drivers, wrapping errors with the network type, then delegates to `windows.RegisterBuiltinLocalDrivers` to register HNS-backed local drivers such as NAT and transparent. `registerPortMappers` returns nil because Windows port mapping is handled inside HNS endpoint policy creation rather than Linux-style pluggable portmappers.

State/dependencies: this file mutates the shared driver registry during controller startup and passes the datastore to Windows local drivers for persistence. Dependencies include `drivers/null`, `drivers/windows`, `drivers/windows/overlay`, `drvregistry`, and controller config types. Risks include HNS restore/register failures aborting startup and the lack of a portmapper registry on Windows requiring all port binding behavior to stay in the Windows driver. Test signal is indirect through Windows driver registration and skipped HNS tests.
