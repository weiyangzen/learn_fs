# sources/distributed-fs/ceph-client/drivers/net/dsa/vitesse-vsc73xx.h

Purpose: this header defines the shared state and bus abstraction for the Vitesse VSC73xx DSA drivers. It lets SPI and platform frontends provide register I/O while the common core owns switch behavior.

Important APIs, types, and functions: `VSC73XX_MAX_NUM_PORTS` fixes the DSA allocation at eight ports to cover 5+1 and 8-port chips while tolerating the invalid port-5 hole. `struct vsc73xx_portinfo` stores per-port PVID state for bridge VLAN filtering and tag_8021q modes. `struct vsc73xx` is the central core object with device, reset GPIO, DSA switch, GPIO chip, chip ID, control-frame MAC, ops, transport private pointer, per-port state, bridge VLAN list, and FDB lock. `struct vsc73xx_ops` provides `read` and `write` callbacks. `struct vsc73xx_bridge_vlan` mirrors bridge VLAN membership and untagged state in software.

Control flow: bus drivers allocate an object containing `struct vsc73xx`, fill `dev`, `priv`, and `ops`, then call `vsc73xx_probe()`. The core later calls transport `read`/`write` for every register operation and provides `vsc73xx_remove()`/`vsc73xx_shutdown()` for frontend teardown.

State and persistence: this header defines all long-lived common driver state but allocates none. The VLAN list is explicitly software-maintained because hardware VLAN state alone is insufficient to compute tag/untag/PVID transitions.

Dependencies and integration points: it includes Linux device, ethernet, and GPIO declarations and is shared by `vitesse-vsc73xx-core.c`, `vitesse-vsc73xx-platform.c`, and `vitesse-vsc73xx-spi.c`.

Risks: transport implementers must honor the `vsc73xx_ops` contract, including the core's block/subblock validity rules and 32-bit register semantics. The fixed eight-port representation means callers must consistently avoid invalid ports. Software VLAN mirror correctness is required for later hardware commits.

Test signals: compile all frontends, probe through both transport paths, validate portinfo transitions under tag_8021q and bridge VLAN filtering, confirm invalid ports are ignored by DSA operations, and exercise remove/shutdown using the shared declarations.
