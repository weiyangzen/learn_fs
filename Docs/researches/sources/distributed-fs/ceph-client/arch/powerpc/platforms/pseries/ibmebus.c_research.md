# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/ibmebus.c

Purpose: Implements the IBM eBus platform bus for GX-bus based pseries adapters, with simple DMA ops, OF device creation, driver registration wrappers, IRQ mapping helpers, sysfs probe/remove controls, and bus/device attributes.

Important APIs/types/functions: Defines fake parent `ibmebus_bus_device`, exported `ibmebus_bus_type`, default matches for `IBM,lhca` and `IBM,lhea`, DMA ops, `ibmebus_create_device()`, `ibmebus_create_devices()`, exported `ibmebus_register_driver()`/`ibmebus_unregister_driver()`, exported IRQ helpers, sysfs `probe`/`remove`, bus match/probe/remove/shutdown callbacks, device attributes, and `ibmebus_bus_init()`.

Control flow: Postcore init registers the bus and fake parent, then creates devices for default OF matches. Driver registration creates any matching devices not already on the bus before registering the platform driver on `ibmebus`. Sysfs `probe` creates a device from an OF path if not already present; `remove` unregisters a matching platform device. Bus probe calls the platform driver's probe after OF match and holds an extra device reference until remove.

State and persistence: Persistent state includes registered bus, fake parent device, platform devices on the bus, sysfs attributes, and driver bindings. DMA operations map coherent memory and physical/scatterlist addresses as direct virtual addresses, reflecting the eBus platform model.

Dependencies and integration points: Depends on OF platform device allocation, Linux driver core, IRQ domain mapping, platform drivers for IBM GX adapters, and pseries machine postcore init.

Risks: DMA ops are nonstandard direct virtual mappings and only support a 64-bit mask. Manual sysfs probe/remove must handle invalid paths and duplicate devices. Probe path `get_device()` must be balanced by remove; driver probe failures drop the reference. IRQ helpers use a NULL irqdomain mapping and assume firmware interrupt specifiers are globally resolvable.

Test signals: eBus init on big-endian pseries, auto-created LHEA/LHCA devices, manual sysfs probe/remove, driver bind/unbind, IRQ request/free, DMA map_sg/coherent behavior, and OF modalias uevents are relevant.

Source read size: 480 lines, 11482 bytes.
