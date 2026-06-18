# sources/distributed-fs/ceph-client/drivers/usb/typec/altmodes/Kconfig

## Purpose

`drivers/usb/typec/altmodes/Kconfig` defines the selectable USB Type-C alternate-mode drivers for DisplayPort, NVIDIA VirtualLink, and Thunderbolt 3.

## Important APIs, Types, and Functions

Symbols are `TYPEC_DP_ALTMODE`, `TYPEC_NVIDIA_ALTMODE`, and `TYPEC_TBT_ALTMODE`. DisplayPort depends on `DRM`; NVIDIA depends on `TYPEC_DP_ALTMODE`; Thunderbolt has no explicit dependency beyond being in the Type-C alternate-mode menu.

## Control Flow

When sourced from the parent Type-C Kconfig, this file presents a submenu. Selecting a symbol enables the matching object in `altmodes/Makefile`. NVIDIA's dependency forces reuse of the DisplayPort altmode implementation exported by `displayport.c`.

## State and Persistence Behavior

No runtime state is stored here. Choices persist in `.config` and determine module availability.

## Dependencies and Integration Points

It integrates with the Type-C bus, DisplayPort DRM hotplug support, the NVIDIA wrapper driver, Thunderbolt altmode support, and the altmodes Makefile.

## Risks and Edge Cases

Dependency drift is the main risk. If DisplayPort starts depending on additional connector or firmware-node APIs, Kconfig must express them. NVIDIA support must remain tied to DisplayPort because its implementation delegates to `dp_altmode_probe()` and `dp_altmode_remove()`.

## Test Signals

Kconfig and build tests should cover each symbol disabled, built-in, and modular, with special attention to NVIDIA without DisplayPort being impossible and DisplayPort requiring DRM.
