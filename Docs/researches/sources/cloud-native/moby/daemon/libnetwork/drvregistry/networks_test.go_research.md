# Research: sources/cloud-native/moby/daemon/libnetwork/drvregistry/networks_test.go

Purpose: verifies core behavior of the network driver registry with a builtin mock driver. Important test fixtures are `mockDriverName`, `mockDriver`, `mockDriverCaps`, and `md`.

Control flow: subtests register the mock driver, attempt duplicate builtin registration, look up the stored driver/capability, and walk registered drivers to observe the inserted name. The mock implements `Type` and `IsBuiltIn`, which is important because duplicate rejection only blocks existing builtin drivers.

State/dependencies: tests use zero-value `Networks`, the `driverapi.Driver` interface, local-scope capability, and `gotest.tools` assertions. They confirm lazy map initialization and capability preservation. Gaps include no coverage for allocator registration, `Notify` forwarding, blank names, non-builtin replacement, nil driver handling, or concurrent registration. The duplicate test asserts only that an error exists, not the exact `ErrActiveRegistration` type.
