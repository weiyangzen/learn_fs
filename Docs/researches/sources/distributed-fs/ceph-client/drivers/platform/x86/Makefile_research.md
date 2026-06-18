# sources/distributed-fs/ceph-client/drivers/platform/x86/Makefile

Purpose: Maps x86 platform-driver Kconfig symbols to objects and subdirectories.

Important APIs and types: Acer entries build `acerhdf.o`, `acer-wireless.o`, and `acer-wmi.o`. The file also adds WMI drivers, vendor subdirectories, firmware attributes, platform-specific drivers, Intel helpers, and miscellaneous laptop drivers through `obj-*` assignments.

Control flow: Kbuild compiles each object or descends into subdirectories according to the resolved configuration. Object ordering matters for comments such as linking `toshiba_acpi` after WMI-related support.

State and persistence: Build metadata only; no runtime state.

Dependencies and integration points: Must stay synchronized with `drivers/platform/x86/Kconfig` symbols and actual source filenames. Subdirectory entries integrate vendor-specific Makefiles.

Risks: Stale object names or missing entries cause selected Kconfig options to produce no module or link failure. Because this directory has many subsystems, accidental ordering or unconditional `obj-y` changes can bloat builds.

Test signals: `make drivers/platform/x86/` with selected configs; module filenames match help text; `CONFIG_ACER_WIRELESS` builds `acer-wireless.o`; `CONFIG_ACER_WMI` builds `acer-wmi.o`.
