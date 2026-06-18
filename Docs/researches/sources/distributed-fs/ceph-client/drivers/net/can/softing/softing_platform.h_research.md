# sources/distributed-fs/ceph-client/drivers/net/can/softing/softing_platform.h

Purpose: platform-data ABI for Softing CAN platform devices.

Important APIs/types/functions: `fw_dir` defines the firmware directory prefix `softing-4.6/`. `struct softing_platform_data` describes manufacturer/product IDs, generation, bus count, controller frequency, bittiming limits, DPRAM size, boot/load/app firmware offset/address/name triples, and optional reset/IRQ-enable callbacks.

Control flow: no executable flow. Bridge drivers populate this data; the generic platform driver uses it during boot, firmware loading, CAN timing setup, IRQ/reset handling, and naming.

State and persistence: platform data is static or device-provided configuration. Firmware filenames refer to persistent files loaded at runtime.

Dependencies/integration: platform device API and Softing generic driver. PCMCIA bridge fills this structure for card variants.

Risks: incorrect offsets/addresses/firmware names can brick boot for a device instance until reload. Generation controls DPRAM reset/IRQ behavior and memory width expectations. `nbus` must fit the generic driver's two-netdev array.

Test signals: platform probe should reject missing/invalid data; each card variant should load expected firmware triplet; reset and enable_irq callbacks should be invoked in boot/shutdown paths.
