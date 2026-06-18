## sources/distributed-fs/ceph-client/drivers/platform/x86/firmware_attributes_class.h

Purpose: declares the shared `firmware_attributes_class` exported by `firmware_attributes_class.c`.

Important APIs/types: includes `<linux/device/class.h>` and declares `extern const struct class firmware_attributes_class;`. The class name and registration are implemented in the companion C file.

Control flow and integration: platform drivers include this header when they need to create a device in `/sys/class/firmware-attributes`. For example, Dell sysman calls `device_create(&firmware_attributes_class, ...)` and then creates driver-specific ksets under that class device.

State and persistence: no state in the header. The declared class is global runtime state owned by the class helper module.

Dependencies: depends on the Linux device class type definition and correct linkage against the helper object/module.

Risks and test signals: this header is intentionally tiny, so risk is mostly build/configuration coupling. Consumers need Kconfig dependencies or selects to ensure the class symbol exists. Build tests should cover each consumer as built-in and module where supported. Runtime tests should verify that consumer class devices appear under the expected class and are removed cleanly when the consumer unloads.
