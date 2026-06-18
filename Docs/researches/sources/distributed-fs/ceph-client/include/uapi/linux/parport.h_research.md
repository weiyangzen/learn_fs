# sources/distributed-fs/ceph-client/include/uapi/linux/parport.h

Purpose: Defines user-visible constants for parallel port hardware classes, status/control bits, capability modes, IEEE1284 negotiation modes, and transfer flags.

Important APIs/types/functions: Exports `PARPORT_MAX`, IRQ/DMA auto/none/probe constants, control and status register bits, `parport_device_class`, `PARPORT_MODE_*` hardware capabilities, `IEEE1284_MODE_*` negotiation values, address/data flags, and EPP fast-transfer flags.

Control flow: Drivers and tools use these constants to describe port capabilities, interpret device IDs, negotiate IEEE1284 transfer modes, and select block transfer behavior. There are no functions in the header.

State and persistence behavior: The header describes runtime port configuration and attached-device capabilities. It does not persist state; port probing and negotiated mode live in parport core/driver state.

Dependencies and integration points: Integrates with parallel printer/scanner/storage drivers, IEEE1284 probing, ppdev userspace, and architecture-specific parport backends.

Risks: Mode bits have hardware timing implications; selecting unsafe EPP fast modes can produce unreliable counts. Magic IRQ/DMA values overlap negative sentinel meanings and must be interpreted in the correct context.

Test signals: Probe legacy, ECP, EPP, and tristate-capable ports; validate IEEE1284 negotiation; exercise ppdev read/write paths; test IRQ/DMA auto and probe-only settings; and compare status/control bit decoding against hardware.
