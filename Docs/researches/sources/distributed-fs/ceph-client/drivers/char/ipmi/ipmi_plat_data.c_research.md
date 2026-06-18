# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_plat_data.c

Purpose: This helper creates software-described IPMI platform devices for discovery sources that do not already have a native device instance, especially hardcoded and hot-added SI devices and SSIF descriptors.

Important APIs, types, and functions: The exported `ipmi_platform_add` takes a platform device name, instance number, and `struct ipmi_plat_data`. It constructs `struct resource` entries for SI register windows and IRQs, constructs software-node properties such as `ipmi-type`, `i2c-addr`, `slave-addr`, `addr-source`, `reg-shift`, and `reg-size`, allocates a `platform_device`, attaches resources/properties, and adds it to the platform bus.

Control flow: SI platform data derives a resource count from the SI type: KCS/SMIC use two register resources, BT uses three, and invalid SI uses no register resource. Default register size and spacing are filled when missing. SSIF data emits an I2C address property and no SI register resources. If an IRQ is present, an IRQ resource is appended. Any failure after allocation drops the platform device with `platform_device_put`.

State and persistence behavior: The function creates runtime platform devices with managed software-node properties and optional resources. There is no filesystem persistence; state persists until the platform device is unregistered, usually by the hardcode/hotmod cleanup paths or by platform device removal.

Dependencies and integration points: It depends on `ipmi_plat_data.h` for the data contract, `ipmi_si.h` for SI type defaults and constants, the platform-device API, and the property-entry software-node API. Consumers include `ipmi_si_hardcode.c`, `ipmi_si_hotmod.c`, and firmware/platform discovery glue that wants the normal platform driver probe path.

Risks and edge cases: Invalid SI and SSIF devices intentionally have no resources, so consumers must rely on properties. `regspacing` is not emitted directly; it is represented by separated register resources, so callers must provide coherent `regsize`, `regspacing`, and address data. The property array is fixed-size and relies on the last zeroed entry for termination.

Test signals: Exercise KCS/SMIC/BT resource counts, invalid SI with no resources, SSIF property creation, IRQ appending, default register values, property visibility in platform probe, and error unwinding for resource/property/add failures.
