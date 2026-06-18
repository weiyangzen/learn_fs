# subset-b-004085 research

This grouped report covers the MIPI CCS/SMIA camera sensor driver files under `sources/distributed-fs/ceph-client/drivers/media/i2c/ccs`. Each section preserves the source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-core.c

## Purpose
`ccs-core.c` is the main V4L2 I2C subdevice driver for MIPI CCS, SMIA, and SMIA++ camera sensors. It detects sensor/module identity, reads CCS capability limits, builds a media graph with source, scaler, binner, and pixel-array subdevices, exposes controls, manages runtime PM, configures PLL/timing/crop/scaling/CSI output, and starts or stops streaming.

## Important APIs, Types, and Functions
The central object is `struct ccs_sensor` from `ccs.h`. Limit helpers `ccs_replace_limit()`, `ccs_get_limit()`, and `ccs_read_all_limits()` cache generated `ccs_limits[]` register values in `sensor->ccs_limits`. Probe helpers include `ccs_get_hwconfig()`, `ccs_identify_module()`, `ccs_firmware_name()`, and `ccs_probe()`. Format and topology are handled by `ccs_get_mbus_formats()`, `ccs_init_subdev()`, `ccs_init_state()`, `ccs_set_format()`, `ccs_set_selection()`, and `ccs_get_frame_desc()`. Runtime behavior centers on `ccs_power_on()`, `ccs_power_off()`, `ccs_pm_get_init()`, `ccs_enable_streams()`, `ccs_disable_streams()`, `ccs_pre_streamon()`, and `ccs_post_streamoff()`. Controls are created in `ccs_init_controls()` and `ccs_init_late_controls()` and applied by `ccs_set_ctrl()`.

## Control Flow
Module init precomputes `ccs_limit_offsets[]` from the generated limit table, then registers the I2C driver. Probe parses the fwnode endpoint, gets regulators, clock, GPIOs, and a CCI regmap, powers the sensor, identifies it, optionally loads sensor and module static-data firmware, reads all limits, parses frame-format descriptors, applies limit quirks, discovers binning/scaling capabilities, computes PLL flags and valid media-bus formats/link frequencies, creates subdevices and controls, writes manufacturer-specific registers, enables runtime PM, and registers the source subdevice asynchronously. Streaming first restores runtime PM state and controls, then writes CSI data format, binning, PLL, analog crop, optional digital crop, scaler mode, output size, optional flash strobe, quirk pre-stream hooks, and finally `MODE_SELECT=STREAMING`. Stopping clears the stream mask, writes software standby when the last stream stops, runs post-stream quirks, and autosuspends.

## State and Persistence Behavior
Driver state is in `struct ccs_sensor`: cached limits, parsed static data, V4L2 controls, PLL solution, media-bus format masks, binning subtype table, runtime streaming mask, frame skip and embedded/image-line offsets, identity data, and device resources. Persistent storage is not written. Static-data firmware blobs are parsed into `sensor->sdata` and `sensor->mdata`; their `backing` allocations own all nested arrays until remove/error cleanup. Runtime PM persists control values in V4L2 handlers and reapplies them on resume through `ccs_pm_get_init()`. Hardware state is volatile and rebuilt on power-on/stream-on.

## Dependencies and Integration Points
The file integrates Linux I2C, regmap/CCI, runtime PM, regulators, clocks, GPIO descriptors, firmware loading, V4L2 subdev active-state APIs, media-controller pad links, fwnode endpoint parsing, MIPI CSI-2 formats, CCS PLL calculation from `../ccs-pll.h`, generated CCS register and limit metadata, static-data parsing from `ccs-data.c`, register access from `ccs-reg-access.c`, and sensor-specific quirks from `ccs-quirk.c`. It exposes sysfs `ident` and optional `nvm` attributes.

## Risks and Edge Cases
Probe has many capability-dependent branches: missing endpoint link frequencies, zero external clock, unsupported bus type, invalid pixel order, no valid PLL/link-frequency combination, malformed limits, or unsupported PHY control can abort setup. Stream configuration depends on active-state consistency across pixel-array, binner, scaler, and source subdevices. `ccs_cleanup()` loops over `ssds_used` but calls `v4l2_subdev_cleanup(&sensor->ssds[2].sd)` inside the loop, which is suspicious because the loop index is ignored. There is also a likely bug in `ccs_get_limit()`: conversion uses `ccs_limits[limit].reg` instead of the `ccs_limit_offsets[limit].info` entry used to read width, which can be wrong when logical limit IDs and table entries diverge because of `CCS_L_FL_SAME_REG`. PM usage-count pairing around pre-stream manual-LP and normal stream enable should be tested carefully. Static-data firmware is optional, but malformed firmware causes probe failure after power-on.

## Test Signals
Useful validation includes probe on CCS and legacy SMIA sensors; firmware-present and firmware-absent paths; module identification and quirk matching; all runtime PM suspend/resume paths; media graph registration and link validation; enumeration and selection across pixel-array, binner, scaler, and source pads; link-frequency menu updates when changing compressed media-bus formats; streaming with crop, binning, scaling, digital crop, flash strobe, and manual-LP pre-stream; sysfs `ident` and `nvm`; and remove/error cleanup under failed probe stages. Hardware traces should show correct CCI writes for PLL, crop, output size, `MODE_SELECT`, and standby.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-data-defs.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-data-defs.h

## Purpose
`ccs-data-defs.h` defines the packed on-wire/on-firmware binary format for CCS static data files consumed by `ccs-data.c`. It is not a runtime parser; it documents block IDs, length encodings, register encodings, frame-format descriptors, rule records, PDAF descriptors, and the end block layout.

## Important APIs, Types, and Functions
Important definitions include `CCS_STATIC_DATA_VERSION`, the variable-width length specifier structs, `struct __ccs_data_block`, `enum __ccs_data_block_id`, packed register block variants, frame-format descriptor pixelcode enums, rule IDs, PDAF readout orders, PDAF pixel-location record structs, and `struct __ccs_data_block_end`. All structs are `__packed` because parser offsets must match the binary blob exactly.

## Control Flow
There is no executable control flow. `ccs_data_parse()` uses the first block's high ID bits as the static-data format version, decodes length specifiers, dispatches block IDs, then interprets payloads according to the packed structs and enums here.

## State and Persistence Behavior
The header stores no state. It defines firmware block formats that are parsed into `struct ccs_data_container`; those parsed containers can override or supplement live sensor/module registers and manufacturer-specific registers.

## Dependencies and Integration Points
It includes `ccs-data.h` for in-memory type relationships and is tightly coupled to `ccs-data.c`. Parsed data is later used by `ccs-reg-access.c` for read-only register lookup and by `ccs-core.c` for manufacturer-specific register writes.

## Risks and Edge Cases
Any layout drift breaks binary compatibility with CCS static-data firmware. Length specifier interpretation, big-endian multi-byte fields, and variable register address deltas are especially sensitive. The duplicate numeric value for vendor/original-order PDAF pixelcode is intentional-looking but can confuse consumers that expect unique symbolic values.

## Test Signals
Build coverage should catch missing symbols. Runtime tests need valid and malformed static-data firmware with every block family: version, sensor/module read-only registers, manufacturer registers, rules, FFD, PDAF readout/location, license, dummy, and end blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-data-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-data.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-data.c

## Purpose
`ccs-data.c` parses CCS static-data firmware blobs into `struct ccs_data_container`. These blobs can contain version metadata, sensor/module read-only register snapshots, manufacturer-specific register writes, conditional rule blocks, frame-format descriptors, PDAF metadata, licenses, and end markers.

## Important APIs, Types, and Functions
The exported API is `ccs_data_parse()`. Internally, `struct bin_container` implements a two-pass arena allocator: first pass reserves aligned sizes, second pass allocates one `kvzalloc()` backing store and fills pointers. Key parsers are `ccs_data_parse_length_specifier()`, `ccs_data_block_parse_header()`, `ccs_data_parse_regs()`, `ccs_data_parse_rules()`, `ccs_data_parse_ffd()`, `ccs_data_parse_pdaf_readout()`, `ccs_data_parse_pdaf()`, `ccs_data_parse_license()`, and `ccs_data_parse_end()`.

## Control Flow
`ccs_data_parse()` calls `__ccs_data_parse()` once with no backing store to validate structure and compute allocation size. It then allocates the backing arena and calls the same parser again to populate the in-memory container. The parser validates the static-data version, walks blocks until the blob end, decodes each header's payload length, and dispatches by block ID. Rule-based blocks require an IF rule to start a rule group; subsequent rule entries attach read-only registers, manufacturer registers, frame format, or PDAF readout to the current rule.

## State and Persistence Behavior
The parser creates one self-contained backing allocation stored in `ccsdata->backing`; all nested pointers reference that allocation. On parse failure it frees the backing and zeroes the container. No disk state is written. The resulting parsed register arrays persist in memory until probe cleanup or device remove and are consulted before live sensor reads or during manufacturer-register programming.

## Dependencies and Integration Points
The parser depends on packed binary definitions from `ccs-data-defs.h`, kernel allocation/string helpers, and a `struct device` for diagnostics. `ccs-core.c` loads firmware with `request_firmware()` and calls this parser for sensor and module blobs. `ccs-reg-access.c` uses parsed read-only registers to satisfy some CCS register reads without touching hardware.

## Risks and Edge Cases
The code is bounds-check heavy, but pointer arithmetic on `void *` is a GNU C extension. Rule parsing assumes non-IF entries follow an IF entry; malformed ordering fails. PDAF block parsing derives `max_block_type_id` from block descriptors and then expects matching pixel descriptor groups; malformed block type IDs or truncated groups return errors. `ccs_data_parse_pdaf()` checks `__bdesc->block_type_id >= num_block_descs`, which compares a block type ID to the current group's descriptor count rather than the eventual number of pixel descriptor groups; this may be overly strict for some legal encodings. License data is copied without appending a NUL terminator, so consumers must use `license_length`.

## Test Signals
Use parser tests or firmware fixtures covering one-, two-, and three-byte length specifiers; register encodings with address deltas and absolute addresses; empty and multi-entry register lists; rule ordering errors; FFD row/column descriptors; PDAF location/readout data; license payloads; unknown block IDs; short headers; and backing-size mismatch detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-data.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-data.h

## Purpose
`ccs-data.h` defines the in-memory representation of parsed CCS static data and declares `ccs_data_parse()`. It is the contract between firmware parsing, register access, and core sensor setup.

## Important APIs, Types, and Functions
Important types include `struct ccs_data_block_version`, `struct ccs_reg`, `struct ccs_if_rule`, `struct ccs_frame_format_descs`, `struct ccs_pdaf_readout`, `struct ccs_rule`, PDAF pixel-location descriptor/group structs, and `struct ccs_data_container`. `struct ccs_data_container` aggregates sensor and module register arrays, rule arrays, PDAF data, license data, end marker state, and the opaque `backing` allocation.

## Control Flow
The header has no control flow. Runtime flow is: `ccs-core.c` loads firmware, `ccs_data_parse()` fills a `ccs_data_container`, `ccs-reg-access.c` reads static read-only register arrays, and `ccs-core.c` writes parsed manufacturer-specific register arrays after power-on.

## State and Persistence Behavior
All fields are memory state only. Pointer fields are owned by `backing`; freeing `backing` invalidates registers, rules, frame descriptors, PDAF data, and license pointers. The parser zeroes the container on failure, so callers can use a zeroed container to mean no usable static data.

## Dependencies and Integration Points
The header depends only on kernel integer types plus forward declaration of `struct device`. It integrates with CCS firmware loading, static register lookup, manufacturer-specific register programming, and any future code that consumes PDAF or rule data.

## Risks and Edge Cases
Consumers must honor counts before dereferencing arrays and must not independently free nested pointers. The typo `num_pixel_desc_grups` is part of the public in-tree struct field. License data is length-delimited, not guaranteed string-terminated. Rule contents may be absent even when `num_*_rules` is nonzero depending on parse block content.

## Test Signals
Compile-time users should include this header without circular dependencies. Runtime tests should validate parser output counts/pointers, backing lifetime across probe/remove, static read-only register lookup, and manufacturer-register writes from both sensor and module containers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-limits.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-limits.c

## Purpose
`ccs-limits.c` is a generated table that maps logical CCS limit IDs to physical CCS/CCI registers, byte spans, grouping flags, and human-readable names. `ccs-core.c` uses it to bulk-read sensor capabilities into a compact cache.

## Important APIs, Types, and Functions
The single exported object is `const struct ccs_limit ccs_limits[]`. Each entry contains a `CCS_R_*` register macro, size in bytes, flags such as `CCS_L_FL_SAME_REG`, and a name. A zeroed guardian terminates the table.

## Control Flow
There is no executable control flow. At module init, `ccs-core.c` iterates this table to build `ccs_limit_offsets[]`. During probe, `ccs_read_all_limits()` iterates the table again, reads each register range, stores values into `sensor->ccs_limits`, and skips repeated logical offsets when `CCS_L_FL_SAME_REG` is set.

## State and Persistence Behavior
The table is immutable kernel data. It describes volatile sensor capability/register state but does not store per-device state. Cached values live in each `ccs_sensor`.

## Dependencies and Integration Points
It includes generated `ccs-regs.h` for register macros and `ccs-limits.h` for `struct ccs_limit`. It must stay synchronized with `CCS_L_*` IDs and offset macros in `ccs-limits.h`.

## Risks and Edge Cases
Generated table/header drift would make `ccs_limit_offsets[]` point at wrong data. `CCS_L_FL_SAME_REG` entries for split lane bitrate arrays rely on core offset logic to accumulate size without advancing the logical limit counter. Sizes must be multiples of register width for correct iteration.

## Test Signals
Module init should pass its `WARN_ON()` checks for guardian and `CCS_L_LAST` count. Probe logs with dynamic debug should show sane values for every named limit. Hardware validation should cover multi-register limits such as frame descriptors, binning subtypes, HDR subtypes, and per-lane bitrate arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-limits.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-limits.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-limits.h

## Purpose
`ccs-limits.h` is the generated public index for CCS capability limits. It defines `struct ccs_limit`, declares `ccs_limits[]`, and assigns stable `CCS_L_*` numeric IDs and offset macros used by `CCS_LIM()` and `CCS_LIM_AT()`.

## Important APIs, Types, and Functions
`struct ccs_limit` stores register, size, flags, and name metadata. `CCS_L_FL_SAME_REG` marks table entries that share a logical limit range. `CCS_L_*` constants cover frame/data descriptors, gain/exposure/timing/PLL constraints, crop/output limits, binning/scaling/HDR/PHY/compression/test-pattern/correction/flash/PDAF/bracketing capabilities, and `CCS_L_LAST`.

## Control Flow
No functions are implemented here. `ccs_module_init()` in `ccs-core.c` consumes the IDs and generated table to build offsets; runtime limit access goes through `ccs_get_limit()` and `ccs_replace_limit()`.

## State and Persistence Behavior
The header has no state. It defines symbolic access to per-device cached limit state. Offset macros such as `CCS_L_FRAME_FORMAT_DESCRIPTOR_OFFSET(n)` and `CCS_L_BINNING_SUB_TYPE_OFFSET(n)` define byte offsets into multi-entry cached limit regions.

## Dependencies and Integration Points
It depends on kernel bits/types and is generated together with `ccs-limits.c` and `ccs-regs.h`. It is included by `ccs.h`, `ccs-core.c`, `ccs-quirk.c`, and register-access code.

## Risks and Edge Cases
Generated numeric IDs are ABI-like inside this driver; reordering without regenerating the table breaks cached-limit access. Offset macros must match the register width and size in `ccs_limits[]`. `CCS_L_LAST` must equal the number of logical limits, not raw table rows.

## Test Signals
Build-time table/header consistency is checked by module init. Probe should be tested with sensors exercising descriptor arrays, same-register split arrays, and optional capability groups so all offset macros are used against real cached data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-limits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-quirk.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-quirk.c

## Purpose
`ccs-quirk.c` provides sensor-specific workarounds for known SMIA/CCS modules that do not behave fully according to generic CCS limits or recommended register programming.

## Important APIs, Types, and Functions
The file exports quirk objects `smiapp_jt8ew9_quirk`, `smiapp_imx125es_quirk`, `smiapp_jt8ev1_quirk`, and `smiapp_tcm8500md_quirk`. Helper `ccs_write_addr_8s()` writes arrays of `struct ccs_reg_8`. Quirk callbacks include limit replacement, post-power-on register sequences, pre-stream-on, post-stream-off, and init hooks.

## Control Flow
`ccs_identify_module()` selects a matching quirk from `ccs_module_idents[]`. During probe and runtime, `ccs-core.c` calls `limits`, `post_poweron`, `pre_streamon`, `post_streamoff`, and `init` through `ccs_call_quirk()`. JT8EW9 adjusts frame skip and analog gain limits and writes Toshiba-recommended registers after power-on. IMX125ES writes a small power-on register sequence. JT8EV1 adjusts limits, writes multiple recommendation registers, applies extra registers for 9.6 MHz external clock, clears/restores one register around streaming, and sets PLL lane-speed flags. TCM8500MD raises the minimum PLL input clock limit.

## State and Persistence Behavior
Quirks mutate per-device cached limits, `frame_skip`, and PLL fields, and write volatile sensor registers after each power-on or stream transition. They do not persist state outside the device.

## Dependencies and Integration Points
The file depends on `ccs.h`, `ccs-limits.h`, CCI register writes through `ccs_write_addr()`, and core identity matching. It integrates with probe, runtime power-on, stream start/stop, and PLL setup.

## Risks and Edge Cases
Hard-coded manufacturer-specific register sequences are sensor revision and clock sensitive. JT8EV1 only has extra programming for 9.6 MHz external clock and warns for other rates. Limit quirks must run after the generic limit cache is populated and before controls/PLL decisions rely on those limits. Failed quirk writes abort power-on or streaming.

## Test Signals
Test each matched module ID, especially JT8EW9 revisions below 0x0300, JT8EV1 at 9.6 MHz and other clocks, analog gain ranges after limit replacement, stream start/stop register side effects, and probe failure logging when a quirk write fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-quirk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-quirk.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-quirk.h

## Purpose
`ccs-quirk.h` defines the quirk callback interface for sensor modules that need behavior outside the generic CCS/SMIA path.

## Important APIs, Types, and Functions
`struct ccs_quirk` contains optional callbacks for `limits`, `post_poweron`, `pre_streamon`, `post_streamoff`, `pll_flags`, `init`, and `reg_access`, plus quirk flags. `CCS_QUIRK_FLAG_8BIT_READ_ONLY` alters read access. `struct ccs_reg_8` and `CCS_MK_QUIRK_REG_8()` support compact register-write tables. `ccs_call_quirk()` and `ccs_needs_quirk()` are the main dispatch helpers.

## Control Flow
Core code stores a selected quirk pointer in `sensor->minfo.quirk`. Call sites use `ccs_call_quirk()` to run a callback only when present. Register access quirks can rewrite the register/value, handle a read/write completely by returning `-ENOIOCTLCMD`, or return an error.

## State and Persistence Behavior
The header declares behavior only. Quirk callbacks can mutate cached limits, PLL flags, controls, and hardware registers, but no state is stored in this header.

## Dependencies and Integration Points
It forward-declares `struct ccs_sensor` and exports quirk objects implemented in `ccs-quirk.c`. It is included by `ccs.h`, making quirk support available to core and register-access layers.

## Risks and Edge Cases
The `reg_access` callback has broad authority and must preserve register width/value semantics. Returning `-ENOIOCTLCMD` means the core treats access as handled, with default read value zero for reads. Flag and callback semantics must remain synchronized with `ccs-reg-access.c`.

## Test Signals
Exercise devices with and without quirks, register-access quirks that redirect/suppress reads and writes, 8-bit-read-only behavior, and each lifecycle hook under probe, power cycle, stream on, and stream off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-quirk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-reg-access.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-reg-access.c

## Purpose
`ccs-reg-access.c` centralizes CCS register reads and writes over the CCI/regmap layer, including conversion of CCS real-number encodings, static-data read-only register lookup, quirk interception, and bulk writes of manufacturer-specific register data.

## Important APIs, Types, and Functions
Exported functions are `ccs_reg_conv()`, `ccs_read_addr()`, `ccs_read_addr_8only()`, `ccs_read_addr_noconv()`, `ccs_write_addr()`, and `ccs_write_data_regs()`. Conversion helpers are `float_to_u32_mul_1000000()` and `ireal32_to_u32_mul_1000000()`. Static-data lookup is implemented by `__ccs_static_data_read_ro_reg()` and `ccs_static_data_read_ro_reg()`.

## Control Flow
Reads call `ccs_read_addr_raw()`. If enabled, it first searches parsed sensor and module static read-only register arrays. If not found, it calls a register-access quirk that may handle, redirect, or fail the access. It then reads the register through `cci_read()` and optionally converts float/ireal values. Writes first call a write quirk and then use `cci_write()`. Bulk writes iterate parsed `struct ccs_reg` arrays in chunks up to `MAX_WRITE_LEN`, log a hex string, retry failed `regmap_bulk_write()` calls up to ten times with 1 ms sleeps, and abort on persistent error.

## State and Persistence Behavior
The file stores no long-lived state. It reads from `sensor->sdata` and `sensor->mdata`, writes volatile hardware registers, and returns converted scalar values to callers. Manufacturer-specific writes are not persisted beyond sensor power state.

## Dependencies and Integration Points
It depends on `ccs.h`, generated register flags from `ccs-regs.h`, limit access for `CLOCK_CAPA_TYPE_CAPABILITY`, V4L2 subdev client lookup, CCI/regmap APIs, parsed static data from `ccs-data.h`, and quirk hooks from `ccs-quirk.h`.

## Risks and Edge Cases
`__ccs_read_addr()` accepts `only8` but does not currently use it directly; 8-bit-read-only behavior relies on the CCI/reg encoding and quirk path. Static read-only lookup assumes sorted/non-overlapping parsed register ranges; malformed or unsorted firmware can cause unexpected misses. Conversion saturates infinity/overflow to `~0` or `U32_MAX` and reports NaN/negative values as zero. Bulk writes to manufacturer registers may partially program a device before a later retry failure.

## Test Signals
Validate live CCI reads/writes for 8/16/32-bit registers; static-data override reads; float and ireal conversion paths; 8-bit-read-only quirked sensors; quirk-suppressed accesses; manufacturer-register bulk writes with chunks larger than 32 bytes; and retry/error logging on transient bus failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-reg-access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-reg-access.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-reg-access.h

## Purpose
`ccs-reg-access.h` declares the CCS register access abstraction used by the core driver and quirks. It wraps generated `CCS_R_*` register macros into readable `ccs_read()` and `ccs_write()` call sites.

## Important APIs, Types, and Functions
The header declares `ccs_read_addr()`, `ccs_read_addr_8only()`, `ccs_read_addr_noconv()`, `ccs_write_addr()`, `ccs_write_data_regs()`, and `ccs_reg_conv()`. `CCS_REG_ADDR(reg)` strips a register descriptor to the 16-bit address. Macros `ccs_read(sensor, REG, val)` and `ccs_write(sensor, REG, val)` expand to generated `CCS_R_REG` descriptors.

## Control Flow
No implementation is present. The macros route typed logical register names to the functions in `ccs-reg-access.c`, where static data, quirks, CCI/regmap access, and conversion are applied.

## State and Persistence Behavior
The header stores no state. It defines accessors that operate on `struct ccs_sensor` runtime state and hardware registers.

## Dependencies and Integration Points
It includes Linux I2C/types and generated `ccs-regs.h`; it forward-declares `struct ccs_sensor`. It is included by `ccs.h`, so all core and quirk code can use symbolic CCS register accesses.

## Risks and Edge Cases
Callers must pass generated CCS register names without the `CCS_R_` prefix to the convenience macros. Using `ccs_read_addr_noconv()` bypasses real-number conversion and is appropriate for raw limit caching, not normal consumers. `CCS_REG_ADDR()` discards width and private conversion flags, so it is only suitable when a raw 16-bit address is intended.

## Test Signals
Compile coverage should catch invalid register names. Runtime tests should compare macro-based access against direct address access and verify converted versus non-converted reads for float/ireal capability registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-reg-access.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-regs.h

## Purpose
`ccs-regs.h` is a generated register definition header for MIPI CCS/SMIA camera sensors. It assigns CCI register descriptors, field masks, shifts, enumerated values, and generated array bounds for identity, mode, timing, PLL, crop/output, CSI/PHY, binning/scaling, test pattern, correction, flash, PDAF, and bracketing registers.

## Important APIs, Types, and Functions
Important macros include `CCS_R_*` register descriptors, `CCS_FL_FLOAT_IREAL`, `CCS_FL_IREAL`, and `CCS_BUILD_BUG`. Register descriptors use V4L2 CCI width macros such as `CCI_REG8`, `CCI_REG16`, and `CCI_REG32`, with private CCS flags for real-number conversion. Field macros follow `*_SHIFT`, `*_MASK`, and symbolic value patterns. Arrayed registers include descriptor arrays, lane bitrate arrays, binning subtype arrays, lane seed values, data-transfer page data, and bracketing LUT entries.

## Control Flow
There is no executable control flow. Core and register-access code use the macros to build CCI reads/writes, parse field values, calculate limits, and program sensor state. `CCS_BUILD_BUG` verifies that CCS private flags fit inside CCI private mask space.

## State and Persistence Behavior
The file stores no runtime state. It describes volatile hardware register state and generated constants. Some registers represent read-only capabilities, some are controls, and some are streaming-time state with side effects.

## Dependencies and Integration Points
It depends on Linux bit macros and `media/v4l2-cci.h`. It is consumed by `ccs-limits.c`, `ccs-core.c`, `ccs-reg-access.c`, quirks, and any code using `ccs_read()`/`ccs_write()`. Real-number flags integrate with `ccs_reg_conv()`.

## Risks and Edge Cases
Because the file is generated, manual edits risk mismatching the CCS specification. Register aliases and overlapping addresses, such as some PHY/USL definitions, require consumers to use the correct symbolic context. Private conversion flags must not be stripped before reads that need converted MHz/Mbps values. Array bounds macros must agree with generated limit sizes.

## Test Signals
Build with `CCS_BUILD_BUG`, probe hardware covering CCS 1.0/1.1 and SMIA compatibility, validate field decoding for identity/capabilities, confirm PLL/PHY timing writes use the correct widths, and compare generated register values against the CCS specification or known sensor traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs.h

## Purpose
`ccs.h` is the central private header for the CCS/SMIA sensor driver. It collects common constants, hardware configuration structures, module identity structures, media-bus format descriptors, subdevice wrappers, and the main `struct ccs_sensor`.

## Important APIs, Types, and Functions
Key constants include SMIA/SMIAPP version/profile values, reset delays, default I2C addresses, pad indices, and stream ID. `CCS_LIM()` and `CCS_LIM_AT()` wrap cached capability access. Important structs are `ccs_flash_strobe_parms`, `ccs_hwconfig`, `ccs_module_ident`, `ccs_module_info`, `ccs_csi_data_format`, `ccs_binning_subtype`, `ccs_subdev`, and `ccs_sensor`. It declares `ccs_replace_limit()` and `ccs_get_limit()`.

## Control Flow
The header implements no control flow, but its macros and structs shape the whole driver. `to_ccs_subdev()` and `to_ccs_sensor()` convert V4L2 subdev pointers back to driver state. Identity macros such as `CCS_IDENT_LQ()` initialize the module ID table used during probe.

## State and Persistence Behavior
`struct ccs_sensor` owns nearly all per-device runtime state: mutex, subdevices, hardware config, regulators/clock/GPIO/regmap handles, cached limits, parsed static data, frame format offsets, streaming flag, initialization flags, identity/quirk pointer, PLL state, valid link-frequency masks, and V4L2 control pointers. This is in-memory only and is destroyed on remove or probe failure.

## Dependencies and Integration Points
It includes V4L2 controls/subdev APIs, regmap, mutexes, generated CCS data/limit/register headers, quirk/register-access interfaces, PLL definitions, and legacy SMIAPP register definitions. It is included by all CCS driver implementation files in this subset.

## Risks and Edge Cases
The main state struct is shared across subdevices and protected by `sensor->mutex` except for V4L2 control internals as documented. Optional pointers such as `scaler`, `strobe_setup`, controls, static-data arrays, and GPIOs require null checks. Cached limit access depends on `ccs-core.c` initializing `ccs_limit_offsets[]` and `sensor->ccs_limits` before use.

## Test Signals
Compile coverage should catch structure/API drift across all CCS files. Runtime validation should exercise devices with and without scaler, static-data firmware, alternate I2C address, flash strobe, quirks, all control families, and all media graph subdevices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs.h -->
