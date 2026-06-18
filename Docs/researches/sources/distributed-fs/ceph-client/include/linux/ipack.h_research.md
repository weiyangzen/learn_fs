# sources/distributed-fs/ceph-client/include/linux/ipack.h

## Purpose
`ipack.h` defines the IndustryPack bus framework contract for carrier boards and mezzanine drivers: device identity, address spaces, bus operations, driver registration, and carrier module reference handling.

## Important APIs, types, and functions
Key definitions include IDPROM offsets, vendor/device constants, `enum ipack_space`, `struct ipack_region`, `struct ipack_device`, `struct ipack_driver_ops`, `struct ipack_driver`, `struct ipack_bus_ops`, and `struct ipack_bus_device`. Public functions include bus, driver, and device register/unregister/add/delete/get/put helpers, plus `DEFINE_IPACK_DEVICE_TABLE`, `IPACK_DEVICE`, `ipack_get_carrier`, and `ipack_put_carrier`.

## Control flow
Carrier drivers register an `ipack_bus_device`, populate an `ipack_device` with slot and regions, call `ipack_device_init`, then add it. Mezzanine drivers register an `ipack_driver` with an ID table and probe/remove callbacks. Bus operations provide IRQ and error/clock handling while direct memory access remains carrier-specific.

## State and persistence
State lives in kernel device objects, mapped regions, parsed IDPROM fields, module references, and carrier-private bus data. No on-disk state exists.

## Dependencies and integration points
It integrates with the Linux device model, module refcounts, mod_devicetable matching, and interrupt handling.

## Risks and test signals
Risks include carrier/device lifetime bugs, IDPROM CRC or endianness mistakes, stale mapped regions, and missing module references. Tests should cover failed init/add cleanup, driver match/probe/remove, carrier unregister with devices present, IRQ request/free, and clock/error callbacks.
