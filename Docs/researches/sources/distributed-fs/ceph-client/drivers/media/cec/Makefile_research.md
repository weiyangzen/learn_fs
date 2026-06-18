# sources/distributed-fs/ceph-client/drivers/media/cec/Makefile

Purpose: This Kbuild file descends into all CEC subtrees: core, I2C, platform, and USB.

Important APIs, types, and functions: It uses `obj-y += core/ i2c/ platform/ usb/`, leaving each subtree to decide which objects are actually built based on configuration.

Control flow and state: The CEC subtree is entered from `drivers/media/Makefile` when `CONFIG_CEC_CORE` is enabled. Within this directory, all child Makefiles are parsed so drivers can be built when their config symbols are set.

State and persistence behavior: No runtime state; object traversal only.

Dependencies and integration points: Integrates top-level media Kbuild with CEC-specific core and driver directories.

Risks and edge cases: New CEC driver families must be added here or they will never be reached by Kbuild. Since all child directories are unconditional from this file, child Makefiles must correctly guard their objects.

Test signals: Build with selected CEC I2C, platform, and USB drivers to confirm the relevant child directories are reached.
