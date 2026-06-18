# sources/distributed-fs/ceph-client/include/linux/platform_data/clk-fch.h

Purpose: defines platform data for AMD FCH miscellaneous clock framework support.

Important APIs and types: `struct fch_clk_data` contains an MMIO `base` pointer and a clock `name`.

Control flow: platform setup passes this data to the FCH clock driver; the driver maps register operations relative to `base` and registers a named clock provider/output.

State and persistence: the struct is static registration data. Runtime clock state is in MMIO registers and common clock framework objects.

Dependencies and integration points: includes compiler attributes for `__iomem` and integrates AMD platform devices, MMIO register access, and the common clock framework.

Risks and test signals: risks include invalid MMIO base, mutable string lifetime, duplicate clock names, and register bit drift. Test clock registration, enable/disable/rate operations if supported, invalid base handling, and remove cleanup.
