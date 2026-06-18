# Research: sources/cloud-native/moby/daemon/libnetwork/drivers_linux.go

Purpose: registers Linux network drivers and portmapper implementations during libnetwork controller initialization. Important APIs are `registerNetworkDrivers` and `registerPortMappers`.

Control flow: `registerNetworkDrivers` iterates fixed driver registrations for bridge, host, ipvlan, macvlan, null, and overlay, passing the datastore, bridge config, and portmapper registry where needed. It wraps each registration failure with the driver type for diagnostics. `registerPortMappers` optionally creates a rootlesskit port driver client when rootless mode is enabled, registers the NAT portmapper with that client, then registers the routed portmapper.

State/dependencies: this file is glue rather than stateful logic; it populates the driver registry and portmapper registry used by network creation and endpoint external connectivity. Dependencies include Linux driver packages, `drvregistry`, rootlesskit client support, and config data. Risks include startup failure if any builtin registration or rootless port driver initialization fails. Test signal is indirect through controller startup and driver package tests.
