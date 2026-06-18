# sources/distributed-fs/ceph-client/sound/soc/sdca/sdca_functions.c

## Purpose
Parses ACPI DisCo metadata for SDCA devices and functions into structured in-kernel SDCA descriptors. It discovers function types, entity graphs, controls, ranges, clusters, file-download sets, HID descriptors, and helper lookup contracts used by regmap, ASoC, IRQ, FDL, HID, and jack code.

## APIs, Types, and Functions
Exports `sdca_lookup_functions()`, `sdca_parse_function()`, `sdca_find_terminal_name()`, `sdca_selector_find_control()`, `sdca_control_find_range()`, `sdca_selector_find_range()`, and `sdca_id_find_cluster()`. Major internal areas include draft function-type patching, control label/bit/datatype/volatility/reset derivation, initialization-table parsing, entity parsing for IT/OT/XU/CS/PDE/GE/HIDE, connection graph resolution, cluster parsing, and file-set parsing.

## Control Flow, State, and Persistence
`sdca_lookup_functions()` walks ACPI children of the SoundWire device, reads each child ADR, extracts function type from control 0x5 DisCo constant, applies revision/DMI quirks, maps the type to an auxiliary device name, and stores a short descriptor. `sdca_parse_function()` attaches the descriptor, reads busy/reset delays, parses raw init writes, parses entity IDs and Entity 0 controls, resolves entity connections and groups, parses channel clusters, and parses FDL file sets. Control parsing requires access mode/layer, CN list, optional DC/default/fixed values, ranges, interrupt position, derived label/datatype/bit width, reset default, and volatility. Connection parsing resolves clock connections, power-domain managed lists, group affected controls, and input pins by label or ID. HID entities may create a HID device after parsing HID/report descriptors. Parsed data persists in devm-allocated arrays under `struct sdca_function_data`.

## Dependencies and Integration
Depends on ACPI/fwnode property APIs, SoundWire slave data, SDCA public definitions, HID helper, quirk helpers from `sdca_device.c`, and FDL structures. Downstream users are `sdca_regmap.c`, `sdca_asoc.c`, `sdca_interrupts.c`, `sdca_fdl.c`, `sdca_hid.c`, `sdca_jack.c`, and the class function driver.

## Risks and Test Signals
Risks include extensive trust in firmware table correctness, property name case sensitivity, label-prefix fallback possibly matching the wrong entity, legacy function-type patching quirks, unaligned casts while parsing byte arrays, silent omission of missing optional lists, HID device creation during parse, and unsupported or implementation-defined controls defaulting to generic labels/types. Test signals are ACPI tables for old and new SDCA revisions, malformed range/list size rejection, multiple entity connection graphs, GE selected-mode affected controls, clusters with channel counts used by PCM constraints, FDL file-set parsing, HID report descriptor creation, and all exported lookup helpers returning expected failures for missing data.
