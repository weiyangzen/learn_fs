# Research: sources/cloud-native/moby/daemon/libnetwork/drivers_unsupported.go

Purpose: provides a non-Linux, non-Windows build-tag fallback for network driver registration. Its only API is `registerNetworkDrivers`, which returns nil and registers no builtin drivers on unsupported platforms.

Control flow: there is no runtime control flow beyond the no-op function. It exists to satisfy shared controller build requirements when neither Linux nor Windows driver implementations are compiled.

State/dependencies: the function signature references controller config, `driverapi.Registerer`, datastore, and portmapper registry types from the package imports expected in sibling platform files. As shown, the file relies on package-level imports not present in this snippet, so build correctness depends on the actual source context and build tags. Risk is platform skew: unsupported targets get no drivers and may fail later if callers assume at least the null driver exists. Test signal is only compile-time coverage on unsupported build targets.
