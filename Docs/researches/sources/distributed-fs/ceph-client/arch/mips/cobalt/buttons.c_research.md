# sources/distributed-fs/ceph-client/arch/mips/cobalt/buttons.c

Purpose: registers the Cobalt front-panel buttons as a platform device.

Important APIs: `cobalt_add_buttons()` allocates a `"Cobalt buttons"` platform device, attaches one memory resource covering `0x1d000000..0x1d000003`, and registers it at `device_initcall` time.

Control flow and state: all state is static init data plus the platform device registered with the driver core. Failure paths release the allocated platform device.

Dependencies and integration: depends on a matching platform driver for `"Cobalt buttons"` and on the fixed Cobalt memory map. It integrates with the board setup through generic platform-device probing.

Risks and test signals: wrong address range breaks button input. Boot logs should show platform-device registration/probe; pressing hardware buttons should produce input events if the matching driver is enabled.
