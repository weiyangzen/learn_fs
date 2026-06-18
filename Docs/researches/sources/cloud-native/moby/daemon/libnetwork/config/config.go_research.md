<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/config/config.go -->
# sources/cloud-native/moby/daemon/libnetwork/config/config.go

## Purpose
Defines the central libnetwork controller configuration object and option setters used during controller construction.

## Important APIs, Types, And Functions
`Config` embeds `PlatformConfig` and holds data directory, exec root, defaults, labels, cluster provider, control-plane MTU, default address pools, datastore bucket, active sandboxes, plugin getter, firewall backend, rootless flag, and userland proxy settings. `New` applies variadic `Option`s. Option setters configure default network/driver, address pools, data dir, exec root, plugin getter, MTU, active sandboxes, firewall backend, rootless mode, and userland proxy.

## Control Flow
`New` starts with default datastore bucket and applies non-nil options in order. `OptionNetworkControlPlaneMTU` warns for low MTU values and clamps below the hard minimum.

## State And Persistence
This file creates in-memory boot configuration. The data directory and datastore bucket influence persistent libnetwork state opened later by `controller.New`.

## Dependencies And Integration Points
Used by `libnetwork.New`, platform config files, datastore, cluster provider, IPAM default pools, plugin discovery, and bridge/firewall setup.

## Risks And Edge Cases
Options mutate shared config without validation beyond MTU clamping and trimming. Some fields are platform-specific but live in the common struct. Option order matters when multiple setters target the same field.

## Test Signals
Controller initialization and platform-specific tests are the main signals; direct config tests would assert default bucket, trimming, and MTU clamping.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/config/config.go -->
