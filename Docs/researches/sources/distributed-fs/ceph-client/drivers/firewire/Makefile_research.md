# sources/distributed-fs/ceph-client/drivers/firewire/Makefile

### Purpose
The FireWire Makefile composes the kernel objects for the IEEE 1394 stack and wires Kconfig symbols to their built modules or built-in objects.

### Important APIs, Types, And Functions
`firewire-core-y` is built from `core-trace.o`, `core-card.o`, `core-cdev.o`, `core-device.o`, `core-iso.o`, `core-topology.o`, and `core-transaction.o`. Optional targets include `firewire-ohci.o`, `firewire-sbp2.o`, `firewire-net.o`, `nosy.o`, `init_ohci1394_dma.o`, and KUnit objects `uapi-test.o`, `packet-serdes-test.o`, `self-id-sequence-helper-test.o`, and `ohci-serdes-test.o`.

### Control Flow, State, And Persistence
There is no runtime state. Build-time control flows from `obj-$(CONFIG_...)` selections. The core module is a composite object, while protocol/controller modules are separate objects.

### Dependencies, Integration Points, Risks, And Test Signals
The Makefile must stay aligned with `Kconfig` and source-level conditional includes. One notable integration point is that `FIREWIRE_KUNIT_DEVICE_ATTRIBUTE_TEST` is not listed as a separate object because `device-attribute-test.c` is included directly by `core-device.c` under `#ifdef CONFIG_FIREWIRE_KUNIT_DEVICE_ATTRIBUTE_TEST`. Risks include missing an object in the composite core, stale KUnit wiring, or unresolved symbols if cross-file exports change. Test signals are successful modular and built-in links for each Kconfig combination.
