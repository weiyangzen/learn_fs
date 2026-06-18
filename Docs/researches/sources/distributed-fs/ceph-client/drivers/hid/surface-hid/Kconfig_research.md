# sources/distributed-fs/ceph-client/drivers/hid/surface-hid/Kconfig

Purpose: Kconfig menu for Surface Aggregator HID transports.

Important symbols: `SURFACE_HID` builds the generic SSAM HID transport and depends on `SURFACE_AGGREGATOR_REGISTRY`; `SURFACE_KBD` builds the legacy Surface Laptop 1/2 keyboard transport; both select hidden `SURFACE_HID_CORE`. The menu depends on `SURFACE_AGGREGATOR`.

Control flow: configuration choice determines whether generic SSAM HID devices, legacy keyboard devices, and the shared core are compiled.

State and persistence: no runtime state; it controls kernel build state.

Dependencies and integration: integrates with the Surface Aggregator subsystem and HID subsystem via selected objects in the Makefile.

Risks: `SURFACE_KBD` has no explicit `SURFACE_AGGREGATOR_REGISTRY` dependency because it is platform/ACPI based; build coverage must ensure selected core dependencies remain sufficient.

Test signals: `olddefconfig`, module build, and boot probing on Surface Laptop generations covered by help text.
