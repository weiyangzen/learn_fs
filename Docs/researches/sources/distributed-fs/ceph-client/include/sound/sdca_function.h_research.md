<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sdca_function.h -->
# sources/distributed-fs/ceph-client/include/sound/sdca_function.h

## Purpose
`sdca_function.h` is the central public model for parsed MIPI SDCA audio functions. It maps the SDCA specification's function, entity, terminal, connector, channel, control, range, UMP, and firmware-download concepts into kernel enums, limits, helper macros, and runtime data structures consumed by SoundWire SDCA component drivers.

## Important APIs, types, and functions
Important constants cap parser-controlled allocation: `SDCA_MAX_ENTITY_COUNT`, `SDCA_MAX_CLUSTER_COUNT`, `SDCA_MAX_CHANNEL_COUNT`, `SDCA_MAX_DELAY_COUNT`, and `SDCA_MAX_AFFECTED_COUNT`. The main types are `sdca_function_data`, `sdca_entity`, `sdca_control`, `sdca_control_range`, `sdca_cluster`, `sdca_channel`, `sdca_entity_iot`, `sdca_entity_cs`, `sdca_entity_pde`, `sdca_entity_ge`, `sdca_entity_hide`, `sdca_entity_xu`, and FDL types `sdca_fdl_data`, `sdca_fdl_set`, and `sdca_fdl_file`. `SDCA_CTL_TYPE()` and `SDCA_CTL_TYPE_S()` form unique control-type identifiers from entity and selector values. `sdca_range()` and `sdca_range_search()` are inline table helpers. External APIs include `sdca_parse_function()`, `sdca_find_terminal_name()`, `sdca_selector_find_control()`, `sdca_control_find_range()`, `sdca_selector_find_range()`, and `sdca_id_find_cluster()`.

## Control flow
This header does not implement the parser, but it defines the data flow expected from it. A SoundWire SDCA function descriptor is parsed into `sdca_function_data`: initialization writes, entities, controls, clusters, delays, group-mode affected controls, HIDE descriptors, XU firmware-download metadata, and FDL filesets. Later SDCA regmap, IRQ, HID, jack, UMP, and ASoC code searches those parsed arrays by entity ID, selector, range shape, or cluster ID.

## State and persistence behavior
All state is runtime topology state. Arrays are dynamically allocated by the parser and attached to the function object; control metadata records access mode, volatility, deferrability, defaults, resets, fixed values, interrupt positions, valid control numbers, and optional range tables. FDL state references ACPI SWFT firmware table content but the header itself persists nothing.

## Dependencies and integration points
The header depends on Linux bit/type definitions and HID descriptors, forward-declares ACPI SWFT, SoundWire slave, devices, and SDCA descriptors, and provides shared definitions for `sdca_hid.h`, `sdca_interrupts.h`, `sdca_regmap.h`, `sdca_ump.h`, codec component drivers, and SDCA function registration.

## Risks and test signals
Risks include parser allocation overruns if firmware reports counts beyond the sanity caps, invalid range indexing in `sdca_range()`, duplicated control-name macros, entity/control selector reuse without `SDCA_CTL_TYPE()`, stale interrupt positions, and incorrect ownership handling for UMP/FDL/HID message buffers. Test signals are SDCA descriptor parse tests with maximum entity/cluster/channel counts, missing ranges, volatile/default/reset controls, group-entity mode writes, HIDE report descriptors, FDL sets, jack terminals, and all function types including reserved or implementation-defined values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sdca_function.h -->
