# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_opregion.h

Purpose: public OpRegion interface for display code, with ACPI-enabled implementations and no-op stubs when `CONFIG_ACPI` is disabled.

Important APIs: setup/cleanup, register/unregister, resume/suspend, ASLE presence/interrupt, encoder and adapter notifications, panel type, EDID, VBT, headless SKU, and debugfs registration. The stubs return neutral values such as `0`, `false`, `NULL`, or `-ENODEV`.

Control flow/state: the header owns no state; it hides whether OpRegion support is compiled in. This lets display code call OpRegion helpers unconditionally where appropriate.

Dependencies/integration: depends on Linux PCI power-state types and display connector/encoder/display forward declarations. It is used by BIOS parsing, display init/resume, interrupt handling, modeset setup, and debugfs registration.

Risks/test signals: conditional-compilation mismatches can silently drop firmware integration. Build both ACPI and non-ACPI configurations, and verify callers handle `-ENODEV`/`NULL` fallback results.
