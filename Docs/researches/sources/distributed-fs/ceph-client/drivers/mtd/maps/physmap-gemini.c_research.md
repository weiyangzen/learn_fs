<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-gemini.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-gemini.c

Purpose: Gemini-specific physmap add-on that validates parallel flash hardware status and toggles pinctrl states around every map access.

Important APIs, types, and functions: `struct gemini_flash` stores device and pinctrl state. `of_flash_probe_gemini()` is called from physmap OF initialization. Custom hooks are `gemini_flash_map_read()`, `gemini_flash_map_write()`, `gemini_flash_map_copy_from()`, and `gemini_flash_map_copy_to()`.

Control flow: the probe helper returns immediately unless the flash node is compatible with `cortina,gemini-flash`. It allocates singleton state, reads a syscon global status register, rejects non-parallel flash, warns if DT bank width differs from hardware, obtains enabled/disabled pinctrl states, selects disabled as idle, and installs wrappers that enable pins for each inline map operation and disable them afterwards.

State and persistence: runtime state is a static singleton pointer and pinctrl states. Persistent flash contents are untouched except through normal map operations.

Dependencies and integration points: physmap OF path, syscon regmap, pinctrl, Gemini hardware global status bits, and MTD XIP-safe inline map helpers.

Risks: singleton `gf` assumes only one active Gemini flash context. Per-access pin toggling may be expensive and must be safe for nested/concurrent map operations. Test signals are syscon status validation, bank-width warnings, pinctrl state transitions during read/write/probe, and normal physmap registration afterward.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-gemini.c -->
