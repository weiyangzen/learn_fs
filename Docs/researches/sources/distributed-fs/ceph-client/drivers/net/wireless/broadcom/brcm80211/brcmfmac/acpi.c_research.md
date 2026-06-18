# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/acpi.c

## Purpose
Extracts brcmfmac platform identity hints from ACPI, primarily for Apple/Asahi systems that expose module instance and antenna SKU metadata.

## Important APIs, Types, and Functions
`brcmf_acpi_probe()` looks up the ACPI companion, reads the `"module-instance"` string property, assigns `settings->board_type` as `"apple,<module-instance>"`, evaluates `RWCV`, and if it returns a buffer with at least two bytes, stores a two-character `settings->antenna_sku`.

## Control Flow, State, and Persistence
The function returns early without an ACPI companion or without `module-instance`. Allocations use `devm_kasprintf()` and `devm_kzalloc()`, so state persists for device lifetime. The ACPI buffer from `RWCV` is freed after parsing when present.

## Dependencies and Integration Points
Depends on ACPI property/evaluate APIs, brcmfmac `struct brcmf_mp_device`, and debug logging. It is included when `CONFIG_ACPI` selects `acpi.o` in the brcmfmac Makefile and feeds firmware/board file selection through `settings`.

## Risks and Test Signals
Risks include malformed ACPI objects, missing buffer cleanup on unusual paths, and board-type strings that do not match firmware naming. Test ACPI systems with and without `module-instance`, with valid/absent `RWCV`, and firmware board selection for Apple modules.
