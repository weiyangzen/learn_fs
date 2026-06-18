# sources/distributed-fs/ceph-client/sound/soc/sdca/sdca_regmap.c

## Purpose
Provides SDCA-aware regmap access policy and cache/default population based on parsed DisCo controls.

## APIs, Types, and Functions
Exports `sdca_regmap_readable()`, `sdca_regmap_writeable()`, `sdca_regmap_volatile()`, `sdca_regmap_deferrable()`, `sdca_regmap_mbq_size()`, `sdca_regmap_count_constants()`, `sdca_regmap_populate_constants()`, `sdca_regmap_write_defaults()`, and `sdca_regmap_write_init()`. Internal helpers locate entities/controls for a register and populate defaults for one control.

## Control Flow, State, and Persistence
Regmap policy helpers validate SDCA control register encoding, find the matching entity/control, ensure the requested control number is present in `cn_list`, and apply access-mode/layer rules. DC constants and reset defaults are counted and exposed as regmap defaults so firmware constants can be read through regmap. `sdca_regmap_write_defaults()` writes default/fixed values for non-device-layer controls and reads non-volatile physical registers without defaults to seed the cache; reset-backed entries may have their cache region dropped first. `sdca_regmap_write_init()` writes the parsed function initialization table to the device-level regmap.

## Dependencies and Integration
Depends on regmap, SoundWire SDCA register macros, parsed `struct sdca_function_data`, and helper metadata from `sdca_functions.c`. It is used by class function regmap callbacks and boot/resume/default-writing paths.

## Risks and Test Signals
Risks include rejecting multi-register `NEXT_CTL` access except dual controls, MBQ byte-size clamping from bit width, default writes to controls whose firmware descriptions are wrong, cache seeding reads failing while hardware is inaccessible, and DC values being treated as cache defaults despite no physical register. Test signals are readable/writeable/volatile callbacks for all parsed controls, regcache defaults sorted and usable, default/fixed writes on boot, cache reads during runtime suspend, init-table writes, and invalid register/control-number rejection.
