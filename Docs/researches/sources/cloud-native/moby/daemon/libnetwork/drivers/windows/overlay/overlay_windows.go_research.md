# Research: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/overlay/overlay_windows.go

Purpose: registers the Windows overlay network driver and restores already-existing HNS overlay networks into Docker's in-memory overlay tables at daemon startup. Important APIs/types are `NetworkType`, `driver`, `Register`, `restoreHNSNetworks`, `convertToOverlayNetwork`, `Type`, and `IsBuiltIn`; the driver also satisfies `driverapi.TableWatcher` elsewhere in the package.

Control flow: `Register` constructs a driver with an empty `networkTable`, calls `restoreHNSNetworks`, then registers the driver with global data/connectivity scopes. Restore lists HNS networks, filters `Type == "overlay"`, converts subnets, VSID/VNI policy, gateway IP, HNS ID, and management IP into overlay `network`/`subnet` structs, and inserts them via `addNetwork`.

State and persistence: this file treats HNS as the startup source for existing Windows overlay networks; endpoint restore is intentionally skipped because networks are expected to be recreated on restart. Dependencies include `hcsshim`, `driverapi`, `scope`, JSON policy parsing, and libnetwork overlay tables. Risks include silently continuing past malformed subnet CIDRs and VSID policies defaulting if not present. Test signal is indirect; behavior depends on HNS integration rather than local unit tests in this subset.
