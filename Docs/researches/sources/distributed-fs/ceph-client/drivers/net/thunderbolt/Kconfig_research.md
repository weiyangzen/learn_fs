# sources/distributed-fs/ceph-client/drivers/net/thunderbolt/Kconfig

Purpose: declares the `USB4_NET` driver option for networking over USB4 and Thunderbolt cables using the ThunderboltIP/USB4NET protocol.

Important APIs/types/functions: `USB4_NET` is a tristate depending on `USB4 && INET`. Help text describes interoperability with Apple ThunderboltIP hosts, including Windows and macOS, and names the module `thunderbolt_net`.

Control flow: build-time config controls whether the Thunderbolt networking driver is built in, modular, or omitted.

State and persistence: no runtime state; kernel configuration only.

Dependencies and integration: integrates with the Thunderbolt/USB4 subsystem and IPv4/INET networking availability required by the driver.

Risks: disabling `INET` or `USB4` hides the driver. Built as a module, users need service-driver matching or manual load for Thunderbolt network services.

Test signals: build with `USB4_NET=y/m`, verify `thunderbolt_net` module or built-in object, and confirm dependency constraints in Kconfig resolution.
