# sources/distributed-fs/ceph-client/drivers/soundwire/dmi-quirks.c

## Purpose
Provides DMI-based SoundWire `_ADR` remapping quirks for systems whose firmware reports incorrect SoundWire peripheral addresses. It lets discovery code replace bad ACPI addresses with hardware-accurate addresses on known Intel/Realtek laptop and NUC designs.

## Important APIs, Types, and Functions
The local type is `struct adr_remap`, containing original and remapped 64-bit SoundWire addresses. Quirk tables include `intel_tgl_bios`, `dell_sku_0A3E`, `hp_omen_16`, and `intel_rooks_county`. `adr_remap_quirk_table` matches DMI vendor/product/board/SKU strings. The exported function is `sdw_dmi_override_adr(struct sdw_bus *bus, u64 addr)`.

## Control Flow
`sdw_dmi_override_adr()` calls `dmi_first_match()` on the quirk table. If a system match is found, it scans that match's `adr_remap` table until the sentinel and replaces `addr` when an exact match is found, logging the remap with `dev_dbg()`. If no system or address match exists, it returns the original address unchanged.

## State and Persistence Behavior
All quirk data is static const. The function has no mutable state and no persistence beyond the returned address used by discovery. The remap affects runtime enumeration identity for the current boot only.

## Dependencies and Integration Points
Depends on Linux DMI matching and SoundWire bus logging. The declaration is in `bus.h`, and Intel SoundWire discovery includes this object through the Intel module build. It integrates with ACPI/MIPI DisCo parsing before slave IDs are extracted from `_ADR`.

## Risks
DMI string matches can overmatch product families and apply remaps to later firmware revisions where the addresses are fixed. Exact 64-bit address constants must encode link, unique ID, manufacturer, part, version, and class correctly. Because this file is linked into the Intel driver aggregate, non-Intel SoundWire discovery does not necessarily get these quirks. Remapping can make firmware-described devices appear as different hardware, affecting driver binding.

## Test Signals
Test DMI matches for listed HP Spectre, HP board 8709, Intel LAPBC/LAPRC variants, Avell B.ON, Dell SKU 0A3E, and HP Omen 16. Validate no remap on unmatched systems, correct remap for each bad address, unchanged return for unknown addresses on matched systems, and downstream slave modalias/driver binding after remap.
