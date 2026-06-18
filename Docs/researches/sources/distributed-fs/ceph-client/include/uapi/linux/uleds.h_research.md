# sources/distributed-fs/ceph-client/include/uapi/linux/uleds.h

Purpose: Defines the userspace LED device creation ABI.

Important APIs/types/functions: `LED_MAX_NAME_SIZE` is 64. `struct uleds_user_dev` contains a LED class device name and maximum brightness.

Control flow: Userspace writes the structure to the uleds device to create a virtual LED; subsequent brightness control flows through LED class sysfs or related kernel APIs.

State and persistence behavior: The virtual LED exists while the userspace file/session is active. Brightness is runtime state managed by LED core.

Dependencies and integration points: Integrates with the LED subsystem, sysfs LED class, and userspace LED emulators/tests.

Risks: Name truncation/collision and invalid brightness ranges should be handled by the driver. The ABI is small, so future expansion would require a new structure or versioning.

Test signals: Create virtual LEDs, verify sysfs registration/name length, set brightness through LED class, close creator and confirm cleanup, and validate invalid max brightness handling.
