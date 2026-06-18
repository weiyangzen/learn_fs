# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l41_hda_property.h

## Purpose
This header exposes the CS35L41 HDA property-override entry point to the shared CS35L41 HDA driver. It is intentionally small: it gives the common code a way to ask the property table layer to synthesize or correct DSD-style hardware data.

## Important APIs, types, and functions
The only exported declaration is `cs35l41_add_dsd_properties(struct cs35l41_hda *cs35l41, struct device *physdev, int id, const char *hid)`. The header includes `linux/device.h` for `struct device` and `cs35l41_hda.h` for `struct cs35l41_hda`.

## Control flow
There is no executable flow here. Include guards prevent duplicate declarations. Callers include this file, then call the function during CS35L41 HDA ACPI/platform setup when normal firmware properties need augmentation.

## State and persistence
No state is declared or persisted. The function operates on caller-owned device state in the implementation file.

## Dependencies and integration points
It couples the property override module to the CS35L41 HDA core data structure. Any signature change in `struct cs35l41_hda` setup requirements must be reflected here and in callers.

## Risks and edge cases
The main risk is interface mismatch: callers must pass the physical ACPI device, bus id/address/chip-select, and HID consistently with the implementation's matching tables. Because the API returns Linux errno values, callers must distinguish unsupported systems (`-ENOENT`) from hard setup failures.

## Test signals
Build coverage should confirm the declaration matches the implementation. Runtime testing should verify that CS35L41 core code can call the property layer and preserve fallback behavior when no model row matches.
