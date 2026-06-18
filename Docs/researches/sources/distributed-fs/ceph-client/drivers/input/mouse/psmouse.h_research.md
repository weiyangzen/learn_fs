# sources/distributed-fs/ceph-client/drivers/input/mouse/psmouse.h

`psmouse.h` defines the shared psmouse contract: PS/2 commands/responses, states, return codes, protocol types, protocol descriptors, the live `struct psmouse`, sysfs attribute helpers, logging macros, and optional SMBus APIs/stubs.

`struct psmouse_protocol` describes a protocol's type, names, detection/init functions, parity/pass-through/SMBus policy, and max-protocol eligibility. `struct psmouse` stores private state, input device, ps2dev, resync work, packet buffer, current state, tunables, callbacks, pass-through hooks, and protocol metadata. `PSMOUSE_DEFINE_*` macros create per-protocol sysfs attributes routed through helper functions.

State persists per serio-bound device; the header itself stores none. Dependencies are serio/libps2/input/workqueue users and optional SMBus Kconfig. Risks are callback contract mistakes, wrong `pktsize` or return codes breaking resync, attribute macro mismatches, and enum ordering with `PSMOUSE_AUTO` last. Test signals are all Kconfig builds, sysfs protected deactivation, protocol type IDs, logging context, and SMBus stub behavior.
