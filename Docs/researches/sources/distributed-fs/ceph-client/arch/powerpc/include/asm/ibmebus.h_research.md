# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ibmebus.h

Purpose: Declares IBM eBus device/driver structures and registration helpers for pSeries virtual platform buses.

Important APIs, types, and functions: `struct ibmebus_dev` wraps `struct device`, an OF node, and bus resource metadata. `struct ibmebus_driver` includes name, OF match table, probe/remove/shutdown callbacks, and embedded `device_driver`. Helpers convert device/driver types and register/unregister drivers.

Control flow: Drivers register an `ibmebus_driver`, the bus matches OF nodes against `id_table`, invokes probe with an `ibmebus_dev`, and later calls remove/shutdown.

State and persistence: Device/driver state is normal Linux device-model runtime state. No persistent storage.

Dependencies and integration points: Depends on OF device tree and Linux device model. It integrates IBM platform bus devices with module driver binding.

Risks: OF match tables and resource metadata must accurately describe platform devices. Driver callbacks must handle hotplug/removal if supported.

Test signals: Driver registration/unregistration, OF matching, probe/remove/shutdown ordering, module unload, and resource exposure for representative eBus devices.
