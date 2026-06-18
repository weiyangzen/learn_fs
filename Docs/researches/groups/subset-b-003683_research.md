# Research group subset-b-003683

Grouped research for Nouveau NVKM BAR, VBIOS, bus, and clock build files. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/tu102.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/tu102.c

### Purpose

Turing TU102 BAR subdevice implementation. It binds the GF100 BAR allocator and VMM code to TU102-specific BAR1/BAR2 MMIO control registers, and selects the R535/GSP-backed constructor when the GPU is running through GSP RM.

### Important APIs, types, and functions

`tu102_bar_new()`, `tu102_bar_bar1_init/fini/wait()`, `tu102_bar_bar2_init/fini/wait()`, and the `tu102_bar` `nvkm_bar_func` table. BAR1 uses instance memory from `bar[1].inst`; BAR2 uses `bar[0].inst` plus the `bar2_halve` bit.

### Control flow

Device creation installs the function table through `gf100_bar_new_()` or `r535_bar_new_()`. BAR init writes the shifted instance memory address and enable bit to `0xb80f40` or `0xb80f48`; fini clears the enable bit; wait polls `0xb80f50` for outstanding BAR status bits to clear.

### State and persistence behavior

Persistent state is inherited from `struct gf100_bar`: backing instance memory, BAR VMMs, and the BAR2 half-size flag. This file only drives hardware registers and does not allocate durable state itself.

### Dependencies and integration points

Depends on `gf100.h`, `core/memory.h`, GSP detection, timer polling, and shared BAR flush/VMM helpers. It integrates with NVKM device bring-up for TU102-family GPUs and with R535 firmware-managed paths.

### Risks

Wrong register offsets or address shifts can leave BAR windows disabled or pointed at invalid instance memory. Wait loops have a 2s timeout and rely on status bit definitions matching TU102 hardware.

### Test signals

Source read size: 103 lines, 3108 bytes. Build coverage for TU102, boot on TU102 with and without GSP RM, BAR1 mmap/VRAM access tests, BAR2 VM setup tests, suspend/resume BAR reinit, and timeout/error logging under forced BAR faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/tu102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/Kbuild -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/Kbuild

### Purpose

Build manifest for the Nouveau NVKM VBIOS parser objects. It ensures all table parsers, shadowing backends, init-script interpreter, and newer memory/power table readers are linked into the NVKM module.

### Important APIs, types, and functions

Adds `base.o`, `bit.o`, table readers such as `dcb.o`, `dp.o`, `pll.o`, `rammap.o`, `timing.o`, `volt.o`, shadow backends, and the newer `M0203.o`, `M0205.o`, `M0209.o`, and `P0260.o` objects to `nvkm-y`.

### Control flow

Kbuild has no runtime control flow; kernel build aggregation compiles every listed source into the Nouveau object set.

### State and persistence behavior

No runtime state. The persistent effect is build composition: omitting a line removes exported parser helpers and can break link or runtime VBIOS discovery.

### Dependencies and integration points

Depends on the parent Nouveau Kbuild including this directory. It integrates all `subdev/bios/*.h` declared helpers with display, memory, clock, therm, and power-management code.

### Risks

Missing objects lead to unresolved symbols or silent loss of table support. Ordering is not semantically important, but stale entries can break incremental builds.

### Test signals

Source read size: 41 lines, 1442 bytes. Kernel `make drivers/gpu/drm/nouveau/`, allmodconfig build, and symbol checks for exported parser helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/M0203.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/M0203.c

### Purpose

Parser for the BIT `M` subtable at offset 0x03, used to map memory strap information to logical RAM configuration groups on newer VBIOS layouts.

### Important APIs, types, and functions

`nvbios_M0203Te/Tp()` parse the table header and table metadata; `nvbios_M0203Ee/Ep()` parse entries; `nvbios_M0203Em()` searches entries by RAMCFG strap when the table type is `M0203T_TYPE_RAMCFG`.

### Control flow

The code locates BIT entry `M`, requires version 2 and enough length, reads a 16-bit pointer at `M+0x03`, accepts table version 0x10, then walks fixed-size entries. Match flow iterates entries until the strap matches and returns the decoded group.

### State and persistence behavior

No stored state. Decoded `struct nvbios_M0203T` and `struct nvbios_M0203E` values are caller-owned snapshots derived from `bios->data`.

### Dependencies and integration points

Depends on generic VBIOS reads and `bit_entry()`. `ramcfg.c` uses `nvbios_M0203Em()` to translate boot strap bits into RAM group indexes.

### Risks

Unsupported table type or version returns zero; callers must handle missing translations. Bad header length/count can point into invalid data, with bounds safety delegated to `nvbios_rd*()`.

### Test signals

Source read size: 129 lines, 3563 bytes. VBIOS samples with BIT M v2, strap-to-group translation tests, memory init on boards with M0203 tables, and fallback behavior when the table is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/M0203.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/M0205.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/M0205.c

### Purpose

Parser for BIT `M` subtable at offset 0x05, a nested memory table carrying per-entry data plus subentries.

### Important APIs, types, and functions

`nvbios_M0205Te/Tp()` parse table/version/header/count and table frequency; `nvbios_M0205Ee/Ep()` parse top-level entries; `nvbios_M0205Se/Sp()` parse subentries and expose raw subentry data.

### Control flow

The table pointer is read from BIT M version 2 at `M+0x05`. Version 0x10 tables include a top-level entry length plus subentry count and size, so entry addressing skips `len + snr * ssz` for each top-level record and then indexes subrecords within the selected entry.

### State and persistence behavior

No persistent state; all decoded structures are zeroed before filling. Frequency and type/data fields are transient interpretations of firmware bytes.

### Dependencies and integration points

Depends on `bit_entry()` and `nvbios_rd*()`. It is part of the memory-configuration parser family used by RAM and memory training code.

### Risks

Nested size arithmetic is the main risk: malformed `snr`, `ssz`, or count fields can make callers see missing entries or wrong subrecords. Only table version 0x10 is understood.

### Test signals

Source read size: 135 lines, 3626 bytes. Parse fixtures for M0205 v0x10, boundary tests for entry/subentry counts, and memory-clock/memory-training boot tests on boards that expose this table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/M0205.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/M0209.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/M0209.c

### Purpose

Parser for another BIT `M` version-2 memory table at offset 0x09. It exposes top-level memory records, nested subrecords, and matching helpers used by newer RAM configuration paths.

### Important APIs, types, and functions

`nvbios_M0209Te/Tp()`, `nvbios_M0209Ee/Ep()`, `nvbios_M0209Se/Sp()`, and match helpers follow the same table/entry/subentry pattern as M0205 but decode M0209-specific fields from the structures declared in `M0209.h`.

### Control flow

Control flow validates BIT M, reads the table pointer, accepts known table versions, derives header/count/entry/subentry lengths, and computes entry offsets before decoding fields or scanning for a caller-specified configuration.

### State and persistence behavior

The file stores no state. It returns offsets and fills caller-provided decoded structs from immutable shadowed VBIOS data.

### Dependencies and integration points

Depends on the generic BIOS accessor layer and the M0209 public header. It integrates with memory init code that needs newer VBIOS memory-strap metadata.

### Risks

Unsupported versions silently return zero. Any change to field offsets must be synchronized with the hardware memory code and with the public `struct nvbios_M0209*` layouts.

### Test signals

Source read size: 135 lines, 3926 bytes. Boot tests on GPUs carrying M0209 tables, table parser unit fixtures, malformed count/length fuzzing, and comparison with known-good VBIOS dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/M0209.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/P0260.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/P0260.c

### Purpose

Parser for BIT `P` subtable at offset 0x60, part of the newer power/performance table family.

### Important APIs, types, and functions

`nvbios_P0260Te/Tp()` parse the table header; `nvbios_P0260Ee/Ep()` decode entries; `nvbios_P0260Se/Sp()` address and parse subentries according to entry-local subentry count and size fields.

### Control flow

The table is found through BIT `P` version 2 and a pointer at the expected offset. Known table versions expose header length, entry length/count, and optional nested records; callers receive either the raw offset or a zeroed/fill decoded structure.

### State and persistence behavior

No persistent state. Returned offsets point into `bios->data`; decoded power/performance metadata is owned by the caller.

### Dependencies and integration points

Depends on `bit_entry()`, `nvbios_rd*()`, and `P0260.h`. It integrates with performance and power-management code that consumes BIT P extension tables.

### Risks

Version skew and malformed nested sizes are the main risks. Missing table support can degrade power limits or boost behavior without a link failure.

### Test signals

Source read size: 107 lines, 3005 bytes. Parser fixtures from VBIOS dumps with P0260, power-management bring-up, and regression tests for absent/short BIT P entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/P0260.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/base.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/base.c

### Purpose

Core VBIOS subdevice implementation and safe read helpers. It shadows a usable ROM image, provides endian-safe byte/word/dword access with bounds checks and image-D address remapping, detects BMP/BIT signatures, and records the VBIOS version.

### Important APIs, types, and functions

`nvbios_pointer()`, `nvbios_rd08/rd16/rd32()`, `nvbios_checksum()`, `nvbios_findstr()`, `nvbios_memcmp()`, `nvbios_extend()`, and `nvkm_bios_new()` are the central APIs. `nvkm_bios_dtor()` releases shadowed data.

### Control flow

Construction allocates `struct nvkm_bios`, calls `nvbios_shadow()`, enumerates ROM images to discover image0 and image-D remapping, scans for BMP and BIT signatures, extracts version from BIT `i` or BMP, then logs the version. Reads route through `nvbios_addr()` so image-D offsets and OOB reads are handled consistently.

### State and persistence behavior

`bios->data`, `bios->size`, image remap fields, BMP/BIT offsets, and version fields persist for the BIOS subdevice lifetime. `nvbios_extend()` can replace the backing buffer during shadow reads.

### Dependencies and integration points

Depends on shadow backends, `bit_entry()`, image parsing, BMP helpers, unaligned little-endian accessors, and NVKM subdevice lifecycle. All other BIOS parsers depend on this file.

### Risks

Bounds behavior returns zero on OOB, which prevents memory corruption but can hide corrupted firmware as absent fields. Shadow selection and image-D remapping affect every table parser.

### Test signals

Source read size: 213 lines, 5432 bytes. Boot with ROM, ACPI, PCI, OF, platform, and firmware sources; invalid ROM/OOB fuzzing; known VBIOS version checks; and parser regression against VBIOS dump corpus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/bit.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/bit.c

### Purpose

Minimal parser for the BIT table directory in NVIDIA VBIOS images.

### Important APIs, types, and functions

`bit_entry()` locates one BIT directory entry by one-byte id and returns its id, version, length, and 16-bit offset in `struct bit_entry`.

### Control flow

If `bios->bit_offset` is present, the function reads the entry count and entry stride from the BIT header, then linearly scans entries until the requested id matches. Missing entries return `-ENOENT`; absent BIT support returns `-EINVAL`.

### State and persistence behavior

No state is stored. The function exposes immutable directory metadata from the shadowed BIOS image.

### Dependencies and integration points

Depends on `nvbios_rd08/rd16()`. Almost every modern table parser uses it to find BIT `C`, `D`, `I`, `M`, `P`, `x`, and other directories.

### Risks

A wrong entry stride or BIT offset compromises all downstream parsers. Only 16-bit entry offsets are decoded here, matching the table format used by these VBIOS revisions.

### Test signals

Source read size: 49 lines, 1781 bytes. BIT table parser fixtures, boot logs showing BIT signature detection, and fallback tests on BMP-only legacy VBIOS images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/bit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/boost.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/boost.c

### Purpose

Parser for boost clock tables referenced from BIT `P`. It describes per-pstate boost frequency ranges and per-domain boost percentage/min/max records.

### Important APIs, types, and functions

`nvbios_boostTe()`, `nvbios_boostEe/Ep()`, `nvbios_boostEm()`, and `nvbios_boostSe/Sp()` parse table headers, entries, pstate matches, and subentries.

### Control flow

BIT P version 2 must be at least 0x34 bytes; the boost table pointer is read at `P+0x30`. Version 0x11 tables use fixed header/count/entry/subentry sizes. Match flow walks entries until the requested pstate is found, then callers may enumerate subentries.

### State and persistence behavior

No persistent state. Parsed pstate, min/max kHz, domain, percent, and subentry min/max values are returned in caller-owned structs.

### Dependencies and integration points

Depends on BIT P and VBIOS readers. It feeds clock and performance-management code that constructs boost ranges.

### Risks

Only version 0x11 is supported. Unit conversion multiplies table MHz values by 1000; bad fields can lead to invalid boost envelopes.

### Test signals

Source read size: 126 lines, 3628 bytes. Boost table parse fixtures, pstate/boost sysfs or debug output validation, and frequency transition tests on GPUs with boost tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/boost.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/conn.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/conn.c

### Purpose

Parser for the connector table nested under modern DCB tables. It maps connector indexes to physical connector type, location, HPD, DP, display-id, and LCD metadata.

### Important APIs, types, and functions

`nvbios_connTe/Tp()` find and validate the connector table; `nvbios_connEe/Ep()` locate and decode individual entries into `struct nvbios_connE`.

### Control flow

The parser first calls `dcb_table()`, requires DCB version >= 0x30 and header >= 0x16, reads the connector table pointer from DCB+0x14, then decodes v0x30/v0x40 records. Four-byte records expose extended HPD/DP/DI/SR/LCD id fields.

### State and persistence behavior

No state is stored; output is a decoded snapshot from the VBIOS image.

### Dependencies and integration points

Depends on DCB parsing and generic VBIOS reads. Display output discovery, init scripts, AUX selection, and panel handling use connector metadata.

### Risks

Short entries lose extended metadata by design. Incorrect bit extraction can misroute HPD/AUX/display output and break hotplug or eDP handling.

### Test signals

Source read size: 97 lines, 3151 bytes. DCB/connector dump comparison, hotplug tests across connector types, eDP init-script condition tests, and multi-output boot on boards with v0x30/v0x40 connector tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/conn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/cstep.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/cstep.c

### Purpose

Parser for clock-step tables from BIT `P`, used to map pstates to clock-step indexes and voltage/frequency step descriptors.

### Important APIs, types, and functions

`nvbios_cstepTe()`, `nvbios_cstepEe/Ep()`, `nvbios_cstepEm()`, `nvbios_cstepXe/Xp()` parse the table, pstate entries, pstate match, and extra step records.

### Control flow

BIT P version 2 length >= 0x38 provides a pointer at `P+0x34`. Version 0x10 tables include entry count/size and extra-record count/size. Entries encode pstate and step index; extra records encode frequency in kHz, two unknown bytes, and voltage id.

### State and persistence behavior

No persistent state. It decodes into caller-provided structures and returns offsets for further enumeration.

### Dependencies and integration points

Depends on BIT P and VBIOS reads. Clock and voltage transition code uses cstep metadata with pstate/perf tables.

### Risks

Unsupported table versions return zero. Misinterpreting the pstate bitfield or voltage byte can destabilize reclocking.

### Test signals

Source read size: 122 lines, 3467 bytes. VBIOS parser fixtures, reclocking tests through pstate changes, voltage-step validation, and absent-table fallback tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/cstep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/dcb.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/dcb.c

### Purpose

Parser for the Display Configuration Block. DCB describes display outputs, OR/head/link routing, connector indices, I2C buses, DisplayPort link capabilities, and external encoders.

### Important APIs, types, and functions

`dcb_table()`, `dcb_outp()`, `dcb_outp_parse()`, `dcb_outp_match()`, and `dcb_outp_foreach()` are the main APIs. Internal hash helpers summarize output type/location/extdev and OR/head/link fields.

### Control flow

The table pointer is read from legacy location 0x36 on post-NV04 devices. The parser validates DCB signatures and handles versions >=0x30, >=0x20, and >=0x15 with different header/count/length rules. Output parsing decodes v2+ records and adds v4+ DP link bandwidth/lane and SOR/external-device fields.

### State and persistence behavior

No persistent state; decoded `struct dcb_output` instances are transient. The VBIOS image is the persistent source of truth.

### Dependencies and integration points

Depends on `nvbios_memcmp()` and VBIOS readers. Display engine, connector, I2C, DP, external-device, and init-script code consume DCB output records.

### Risks

DCB version handling is compatibility-sensitive. Bad parsing can disable displays, select wrong I2C/AUX buses, or misprogram SOR links. Very old DCB versions are intentionally rejected as not useful.

### Test signals

Source read size: 235 lines, 6205 bytes. Display enumeration on NV1x through modern GPUs, DCB dump comparison, DP lane/bandwidth validation, multi-head tests, and malformed DCB signature tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/dcb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/disp.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/disp.c

### Purpose

Parser for display script/table pointers from the BIT `U`/display table family. It exposes output-specific init script locations and display table metadata to the display engine.

### Important APIs, types, and functions

`nvbios_disp_table()`, entry accessors, and parsing helpers decode display table headers and script pointers into `struct nvbios_disp*` data declared in `disp.h`.

### Control flow

The parser locates the display table through the relevant BIT entry, validates supported versions, calculates entry offsets from header/count/length fields, and returns script/data offsets for callers that execute display init sequences.

### State and persistence behavior

No mutable state. Offsets and decoded records are transient views into `bios->data`.

### Dependencies and integration points

Depends on BIT directory parsing and generic VBIOS reads. It integrates with display output init, SOR/DAC programming, and `bios/init.c` script execution.

### Risks

Display table versions vary significantly; unsupported versions can leave boards reliant on fallback paths. Wrong script offsets can cause unsafe MMIO sequences.

### Test signals

Source read size: 174 lines, 4822 bytes. Mode-set tests, display init-script tracing, VBIOS dump comparison, and boot validation across LVDS/eDP/DP/HDMI boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/disp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/dp.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/dp.c

### Purpose

Parser for DisplayPort output and AUX/link policy tables nested under DCB/display data.

### Important APIs, types, and functions

`nvbios_dp_table()`, `nvbios_dpout_match()`, output parse helpers, and DP data accessors decode DP flags, link settings, and condition data used by display init scripts.

### Control flow

The code derives DP table locations from DCB/output metadata, validates header/version fields, scans records by output type and OR/link mask, and fills `struct nvbios_dpout` for the matched output.

### State and persistence behavior

No persistent state. Parsed flags and link capabilities are returned to callers while the ROM image remains immutable.

### Dependencies and integration points

Depends on DCB output parsing, connector data, and generic BIOS access. `init_generic_condition()` uses `nvbios_dpout_match()` for SPPLL and eDP-related conditions.

### Risks

Incorrect matching can choose the wrong PLL or AUX behavior for a DP output. Version/length mismatches must fail cleanly to avoid using garbage flags.

### Test signals

Source read size: 232 lines, 6321 bytes. DP/eDP link training tests, init-script condition tracing, SPPLL selection tests, and VBIOS corpus comparison for DP output records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/dp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/extdev.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/extdev.c

### Purpose

Parser for external display/device entries attached to DCB. It identifies external encoder/controller functions and whether probing should be skipped.

### Important APIs, types, and functions

`nvbios_extdev_skip_probe()`, `nvbios_extdev_parse()`, and `nvbios_extdev_find()` are the exported helpers. Internal code locates the extdev table from DCB+18 and decodes type, I2C address, and bus selector.

### Control flow

The table is accepted only for DCB versions 0x30, 0x40, and 0x41. Header flags can request skipped probing. Parse/find functions index or scan entries and fill `struct nvbios_extdev_func`.

### State and persistence behavior

No persistent state. External-device metadata is decoded on demand from VBIOS data.

### Dependencies and integration points

Depends on DCB parsing and generic reads. It integrates with external TMDS/LVDS/encoder discovery and with ICC sense parsing that references external power monitors.

### Risks

Limited DCB version acceptance may miss future layouts. Wrong bus/address parsing can probe the wrong I2C device or skip a required external encoder.

### Test signals

Source read size: 110 lines, 3140 bytes. External encoder detection tests, VBIOS fixtures with skip-probe flags, I2C probe traces, and display bring-up on boards with external display chips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/extdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/fan.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/fan.c

### Purpose

Parser for the BIT P fan table, primarily used for simple PWM/toggle fan descriptions on newer VBIOS layouts.

### Important APIs, types, and functions

`nvbios_fan_parse()` is the public entry. Internal helpers locate the fan table and first fan entry.

### Control flow

BIT P version 2 length >= 0x5c provides the fan table pointer at `P+0x58`. Version 0x10 entries decode fan type, min/max duty, default linear mode, and 24-bit PWM frequency.

### State and persistence behavior

No stored state. The caller-owned `struct nvbios_therm_fan` receives decoded fan policy fields.

### Dependencies and integration points

Depends on BIT P and therm fan type definitions. Thermal/fan subdevices use it alongside `therm.c` table parsing.

### Risks

Only the first fan entry is parsed. Type 1 and 2 are both treated as PWM with an explicit TODO, so behavior may be approximate on some boards.

### Test signals

Source read size: 94 lines, 2704 bytes. Fan table fixtures, PWM frequency/duty validation, therm fan mode tests, and fallback to thermal-table fan parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/fan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/gpio.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/gpio.c

### Purpose

Parser for GPIO function tables referenced from DCB. It maps logical GPIO functions to line numbers, polarity, parameters, and optional extended GPIO provider data.

### Important APIs, types, and functions

`dcb_gpio_table()`, `dcb_gpio_entry()`, `dcb_gpio_parse()`, `dcb_gpio_match()`, and iteration helpers decode GPIO records. It also coordinates with XPIO parsing for external GPIO blocks.

### Control flow

The parser finds the GPIO table through DCB v0x30+ header fields or older DCB backpointers, handles pre-0x30 and 0x30-0x41 header formats, computes entry offsets, and decodes function/line/log/param/polarity fields by table version.

### State and persistence behavior

No persistent state. Decoded GPIO records are transient, while the GPIO subdevice later owns live line state.

### Dependencies and integration points

Depends on DCB, XPIO, and generic BIOS reads. GPIO, therm, fan, hotplug, and init-script code consume these mappings.

### Risks

Version-specific bitfields are fragile. Bad parsing can invert GPIO polarity, drive wrong lines, or miss HPD/fan/thermal GPIOs.

### Test signals

Source read size: 150 lines, 4315 bytes. GPIO table dump comparison, hotplug GPIO interrupts, fan/tach GPIO tests, init-script GPIO opcode tests, and old/new DCB compatibility coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/i2c.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/i2c.c

### Purpose

Parser for DCB I2C bus tables. It maps logical I2C indices used by DCB outputs and init scripts to bus type, drive/sense pins, and AUX/I2C metadata.

### Important APIs, types, and functions

`dcb_i2c_table()`, entry accessors, parse and match helpers decode `struct dcb_i2c_entry` values from versioned DCB I2C tables.

### Control flow

The parser locates the I2C table from DCB metadata, validates version/header/count/length, indexes entries, and decodes bus type and pin assignments according to table version.

### State and persistence behavior

No runtime state is kept here. The I2C subdevice owns bus objects created from decoded records.

### Dependencies and integration points

Depends on DCB and BIOS access helpers. Display output probing, connector detection, AUX routing, and BIOS init I2C opcodes depend on these records.

### Risks

Wrong I2C table parsing can probe EDID or external devices on the wrong bus. Legacy table handling is compatibility-sensitive.

### Test signals

Source read size: 164 lines, 4773 bytes. EDID read tests across DCB outputs, AUX/I2C bus enumeration, init-script I2C opcode tests, and VBIOS dump comparison.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/iccsense.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/iccsense.c

### Purpose

Parser for input-current/current-sense metadata from BIT P. It describes external/current-sense devices and rails used by power monitoring.

### Important APIs, types, and functions

`nvbios_iccsense_parse()` and table helpers locate version 0x10/0x20 ICC sense tables and fill `struct nvbios_iccsense` records with rail/device/address/resistor configuration.

### Control flow

The table pointer comes from BIT P version 2 at `P+0x28`. The parser validates version, header, count, and length, indexes entries, and may cross-reference external-device information for sensor addressing.

### State and persistence behavior

No persistent state. Power sensor code consumes decoded rail descriptions and owns live readings.

### Dependencies and integration points

Depends on BIT P, external-device types, and BIOS reads. It integrates with power-budget and hwmon/power monitoring paths.

### Risks

Bad resistor/address parsing produces wrong current or power readings. Unsupported versions must fail without enabling bogus sensors.

### Test signals

Source read size: 128 lines, 3551 bytes. Power sensor bring-up, rail reading sanity checks against board specs, VBIOS corpus fixtures for v0x10/v0x20, and absent-table fallback tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/iccsense.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/image.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/image.c

### Purpose

ROM image enumerator for multi-image PCI VBIOS blobs. It validates image signatures, reads PCIR/NPDE metadata, and returns image base, size, type, and last-image status.

### Important APIs, types, and functions

`nvbios_image()` is the public iterator; `nvbios_imagen()` validates one image and fills `struct nvbios_image`.

### Control flow

Enumeration starts at base 0 and repeatedly advances by the previous image size. Valid signatures include 0xaa55, 0xbb77, and `NV`. PCIR provides default size/type/last; NPDE can override size/last for non-type-0x70 images.

### State and persistence behavior

No persistent state, except it temporarily clears/restores `bios->imaged_addr` while enumerating to avoid remap interference.

### Dependencies and integration points

Depends on `pcir.c`, `npde.c`, and BIOS access. `base.c` uses it to identify image-D remapping and shadow validation uses it to score ROM images.

### Risks

Wrong image size or last handling can truncate ROMs or read into adjacent data. Signature rejection affects shadow-source scoring.

### Test signals

Source read size: 83 lines, 2511 bytes. Multi-image ROM fixture tests, image-D remap validation, shadow-source scoring tests, and comparison with PCI ROM parser output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/image.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/init.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/init.c

### Purpose

VBIOS init-script interpreter. It executes NVIDIA BIOS opcodes for early device/display/memory initialization, including MMIO, indexed VGA IO, I2C/AUX, PLL programming, conditions, loops, macros, RAM-restrict groups, GPIO, and nested script calls.

### Important APIs, types, and functions

Public entry points are `nvbios_exec()` and `nvbios_post()`. Internal helpers include execution-state controls, `init_nvreg()`, MMIO/VGA/I2C/AUX wrappers, condition table readers, RAM strap translation, many `init_*` opcode handlers, and the `init_opcode[]` dispatch table.

### Control flow

Posting enumerates init script pointers from BIT `I` or BMP tables and executes each script, then an optional unknown script. `nvbios_exec()` increments nesting, reads the opcode at `init->offset`, dispatches to a handler, and stops when an opcode sets offset to zero. Handlers advance offsets, toggle execute state for conditional blocks, recurse for repeats/subscripts, and only touch hardware when `init_exec()` is true.

### State and persistence behavior

`struct nvbios_init` carries transient interpreter state: offset, nesting, execute mask, repeat bounds, selected output/head/OR/link, cached RAMCFG, and subdevice context. Hardware register writes, PLL changes, GPIO updates, and I2C/AUX side effects persist after execution.

### Dependencies and integration points

Depends on BIOS BIT/BMP/DCB/connector/DP/GPIO/RAMCFG parsers, devinit MMIO/PLL helpers, I2C/AUX, VGA IO, and NVKM logging. Device init and display init code provide context such as output/head/OR.

### Risks

This is high risk: malformed scripts, unknown opcodes, bad register mangling, or wrong execute-state nesting can program unsafe MMIO. Output/head/OR context is mandatory for many display opcodes. Delays and polling affect boot reliability.

### Test signals

Source read size: 2347 lines, 56328 bytes. Trace-mode script replay, boot/post tests across old BMP and modern BIT VBIOS, suspend/resume script execution, display mode-set init paths, I2C/AUX failure injection, unknown-opcode handling, and comparison with known-good register traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/mxm.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/mxm.c

### Purpose

Parser for MXM board information and SOR mapping. It handles explicit MXM SOR map tables and chipset-specific fallback maps for older MXM VBIOS layouts.

### Important APIs, types, and functions

`mxm_table()` locates BIT `x`; `mxm_sor_map()` maps MXM digital connector ids to SOR/link values using table data or hard-coded G84/G92/G94/G98 maps.

### Control flow

The parser requires BIT `x` version 1 with at least three bytes. If a SOR map pointer exists and has version 0x10/0x11, it indexes the table by connector id; otherwise it falls back by VBIOS chip version.

### State and persistence behavior

No persistent state. Returned SOR map bytes guide display routing decisions.

### Dependencies and integration points

Depends on BIT parsing and BIOS version fields. Display output code uses the map for MXM modules whose DCB data needs connector-to-SOR translation.

### Risks

Fallback maps are heuristic and chipset-limited. Missing or wrong maps can route display outputs to the wrong SOR/link.

### Test signals

Source read size: 137 lines, 3861 bytes. MXM board display tests, VBIOS fixtures with explicit SOR maps, fallback map validation on G84/G92/G94/G98, and warnings for unknown chips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/mxm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/npde.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/npde.c

### Purpose

Parser for NPDE metadata that can follow PCIR in newer ROM images. It refines image size and last-image status.

### Important APIs, types, and functions

`nvbios_npdeTe()` locates and validates the NPDE signature; `nvbios_npdeTp()` fills `struct nvbios_npdeT` with image size and last flag.

### Control flow

The code first parses PCIR, aligns the post-PCIR offset to 16 bytes, checks for the `NPDE` signature, and decodes size in 512-byte units plus the high last-image bit.

### State and persistence behavior

No persistent state; returned metadata is used immediately by image enumeration.

### Dependencies and integration points

Depends on `pcir.c` and generic BIOS reads. `image.c` consumes NPDE for image sizing.

### Risks

If alignment or signature handling is wrong, multi-image ROM traversal can stop early or overrun into unrelated image data.

### Test signals

Source read size: 59 lines, 2024 bytes. ROM image fixture tests with and without NPDE, multi-image enumeration, and shadow-source validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/npde.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/pcir.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/pcir.c

### Purpose

Parser for PCI ROM PCIR-compatible headers. It extracts vendor/device/class, image size/type/revision, and last-image markers.

### Important APIs, types, and functions

`nvbios_pcirTe()` validates PCIR/RGIS/NPDS signatures and returns version/header length; `nvbios_pcirTp()` decodes `struct nvbios_pcirT`.

### Control flow

The parser reads the header pointer at image base + 0x18, adds the image base, validates one of the accepted signatures, then reads fixed fields including size in 512-byte units and the last-image bit.

### State and persistence behavior

No mutable state. Decoded PCIR information is caller-owned.

### Dependencies and integration points

Depends on generic BIOS reads. `image.c`, `npde.c`, and shadow validation use PCIR metadata.

### Risks

Bad PCIR parsing affects image enumeration and ROM validation. Accepting alternate signatures is intentional but must remain precise.

### Test signals

Source read size: 69 lines, 2490 bytes. PCI ROM corpus tests, vendor/device/type comparison with lspci/ROM tools, and multi-image traversal tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/pcir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/perf.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/perf.c

### Purpose

Parser for performance/pstate tables under BIT `P`. It describes performance levels, domains, clock/memory entries, and voltage indexes used for reclocking.

### Important APIs, types, and functions

`nvbios_perf_table()`, `nvbios_perf_entry()`, `nvbios_perfEp()`, domain/subentry parsers, and matching helpers decode pstate records and nested per-domain records.

### Control flow

The table pointer is selected from BIT P, with special cases for older PCI/subsystem layouts. Supported versions expose header/count/entry/subentry sizing; entry parsing decodes pstate id, core/memory/shader domains, voltage, and flags according to version.

### State and persistence behavior

No stored state. Parsed performance records are transient inputs to clock, memory, and voltage code.

### Dependencies and integration points

Depends on BIT P, PCI subdevice data, RAM map helpers, and generic BIOS access. Clock and voltage subdevices consume this to build pstate tables.

### Risks

Pstate parsing is hardware-sensitive. Wrong units or domain indexes can over/underclock the GPU or choose an invalid voltage.

### Test signals

Source read size: 216 lines, 6073 bytes. Reclocking tests, pstate table dumps, VBIOS corpus comparison, voltage/frequency sanity checks, and absent/legacy table fallbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/perf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/pll.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/pll.c

### Purpose

Parser for PLL limit tables and legacy PLL register mappings. It translates PLL type or register into frequency, divider, input, and post-divider constraints.

### Important APIs, types, and functions

`nvbios_pll_parse()` is the public API. Internal helpers include `pll_limits_table()`, legacy mapping arrays for NV04/NV40/NV50/G84, `pll_map_reg()`, and `pll_map_type()`.

### Control flow

The parser first locates BIT `C` PLL limits or BMP fallback data, then either matches by register or logical PLL type. Versions 0x10 through newer layouts decode VCO min/max, input limits, M/N bounds, post-divider limits, bias, and reference clocks with version-specific offsets.

### State and persistence behavior

No persistent state. Returned `struct nvbios_pll` constrains later PLL programming but the file itself only reads firmware data.

### Dependencies and integration points

Depends on BIT/BMP helpers, device card type/chipset, VGA/devinit PLL programming consumers, and generic BIOS reads.

### Risks

Incorrect limits can produce invalid PLL programming and display/core/memory instability. Legacy fallback maps are chipset-specific and easy to regress.

### Test signals

Source read size: 440 lines, 12113 bytes. PLL parser fixtures, clock programming tests, display pixel-clock tests, reclocking under load, and comparison against known PLL limits from VBIOS dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/pmu.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/pmu.c

### Purpose

Parser for PMU firmware/script metadata in the VBIOS. It exposes PMU table headers and per-entry data to the PMU subdevice.

### Important APIs, types, and functions

`nvbios_pmuTe/Tp()` and entry parse helpers decode table version/header/count/length and PMU-specific fields declared in `pmu.h`.

### Control flow

The table is located through BIT metadata, validated by version, and indexed using standard header plus entry length arithmetic. Decoded records tell PMU code where firmware or init data is located.

### State and persistence behavior

No persistent state. PMU subdevice owns firmware/runtime state after consuming decoded metadata.

### Dependencies and integration points

Depends on BIT parsing and generic BIOS readers. It integrates with the NVKM PMU loader and power-management firmware setup.

### Risks

Unsupported table versions or bad offsets can prevent PMU firmware load or cause use of wrong firmware data.

### Test signals

Source read size: 102 lines, 3350 bytes. PMU firmware load tests, VBIOS parser fixtures, power-management init on supported GPUs, and missing-table fallback tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/power_budget.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/power_budget.c

### Purpose

Parser for VBIOS power-budget tables referenced from BIT `P`. It provides board power limits and related policy values to power-management code.

### Important APIs, types, and functions

`nvbios_power_budget_header()`, entry accessors, and parse helpers decode versioned power-budget records into structures declared in `power_budget.h`.

### Control flow

The parser reads the BIT P power-budget pointer, validates supported versions, derives header/count/length fields, and indexes records to extract power limit values and policy flags.

### State and persistence behavior

No runtime state. Parsed power limits are caller-owned snapshots of firmware policy.

### Dependencies and integration points

Depends on BIT P and BIOS reads. It integrates with power cap, hwmon, and boost/pstate management.

### Risks

Bad units or version offsets can expose wrong power caps, affecting throttling or boost decisions. Missing tables must be tolerated on older boards.

### Test signals

Source read size: 125 lines, 3422 bytes. Power cap sanity checks, VBIOS fixture parsing, hwmon/power-limit display tests, and stress tests that trigger power throttling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/power_budget.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/priv.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/priv.h

### Purpose

Private header for the NVKM BIOS implementation. It defines the shadow-source abstraction and declares internal shadowing helpers/backends.

### Important APIs, types, and functions

`struct nvbios_source` contains backend name, init/fini/read/size callbacks, and policy flags for read-write support, checksum handling, PCIR bypass, and required checksums. It also declares `nvbios_extend()`, `nvbios_shadow()`, and built-in source objects.

### Control flow

No executable control flow. `shadow.c` iterates these backends and calls their callbacks to read candidate ROM images.

### State and persistence behavior

No state by itself, but the flags define how shadow-source state is scored and validated.

### Dependencies and integration points

Depends on `subdev/bios.h`. Included by base and shadow backend files.

### Risks

Changing callback semantics or flags affects all BIOS source selection. `no_pcir`, checksum, and read-write flags directly influence whether a ROM image is accepted.

### Test signals

Source read size: 29 lines, 910 bytes. Build coverage and BIOS shadow-source tests for PROM, RAMIN, ACPI, PCIROM, platform, OF, and firmware sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/ramcfg.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/ramcfg.c

### Purpose

RAM configuration selector. It reads hardware strap bits and translates them into the logical RAM configuration index used by memory init tables.

### Important APIs, types, and functions

`nvbios_ramcfg_count()` returns the number of RAM configurations; `nvbios_ramcfg_index()` returns the selected config; `nvbios_ramcfg_strap()` reads strap bits from register `0x101000`.

### Control flow

The count comes from BIT M version 1 or 2 fields. The selected index starts with strap bits, then uses M0203 RAMCFG translation when available on BIT M v2, otherwise uses an xlat table pointer from BIT M.

### State and persistence behavior

No persistent state here. `init.c` caches the selected RAMCFG in `struct nvbios_init` on newer VBIOSes to avoid repeated strap reads.

### Dependencies and integration points

Depends on BIT M, M0203 parser, generic BIOS access, and MMIO reads. Memory init, RAM map, and init-script RAM restrict opcodes depend on it.

### Risks

Reading the strap register repeatedly can be unsafe on later chipsets, so callers must respect caching behavior. Wrong translation can select incompatible memory timings.

### Test signals

Source read size: 78 lines, 2502 bytes. Memory init boot tests across strap variants, VBIOS fixtures for BIT M v1/v2, M0203 fallback tests, and register-read tracing during init scripts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/ramcfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/rammap.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/rammap.c

### Purpose

Parser for RAM frequency and RAM configuration maps under BIT `P`. It maps memory frequency ranges to RAM timing/config subentries and includes compatibility helpers for older performance-table embedded RAM data.

### Important APIs, types, and functions

`nvbios_rammapTe/Ee/Ep/Em()`, `nvbios_rammapSe/Sp()`, and `_from_perf` helpers decode table entries, select entries by MHz, and decode per-RAMCFG subrecords.

### Control flow

The table pointer is read from BIT P version 2 at offset +4. Versions 0x10 and 0x11 expose entry and subentry sizes. Match flow chooses the frequency range containing the requested MHz, then callers index subentries for the selected RAM config.

### State and persistence behavior

No durable state. The returned `struct nvbios_ramcfg` carries many bitfields used later by RAM training and timing code.

### Dependencies and integration points

Depends on BIT P, performance parser compatibility, and BIOS readers. Memory clock/reclock paths consume this with `timing.c` and `ramcfg.c`.

### Risks

Large bitfield surface is fragile; wrong offsets can break memory controller programming. Frequency range matching must be deterministic for overlapping or malformed entries.

### Test signals

Source read size: 258 lines, 10098 bytes. Memory reclocking tests, RAM timing dump comparison, VBIOS corpus fixtures for v0x10/v0x11, and malformed range tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/rammap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadow.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadow.c

### Purpose

VBIOS shadow-source orchestrator. It tries multiple ROM sources, validates and scores candidate images, supports a user-specified `NvBios` source or firmware file, and installs the best image into `bios->data`.

### Important APIs, types, and functions

`nvbios_shadow()` is the public entry. Internal helpers include `shadow_fetch()`, `shadow_image()`, `shadow_method()`, firmware read/init/release callbacks, and the `shadow` candidate state.

### Control flow

Each source initializes backend data, fetches enough bytes, validates ROM images through `nvbios_image()`, checks checksum policy for type-0 images, recursively scores multi-image ROMs, then detaches candidate data for comparison. The best score wins; losing buffers are freed.

### State and persistence behavior

`bios->data` and `bios->size` become the selected ROM image for the BIOS subdevice lifetime. Candidate `shadow` structs temporarily own backend data and scores.

### Dependencies and integration points

Depends on `priv.h` source backends, firmware loader, core options, image parsing, checksum, and BIOS buffer extension. `base.c` calls it during BIOS construction.

### Risks

Source selection is foundational. Bad scoring can select a stale or corrupted ROM; checksum policy must balance firmware quirks against safety. User-specified invalid sources must be rejected cleanly.

### Test signals

Source read size: 248 lines, 6259 bytes. Boot tests for every source backend, `NvBios=` override tests, corrupt checksum tests, multi-image ROM validation, and firmware-file override tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowacpi.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowacpi.c

### Purpose

ACPI `_ROM` shadow backends for reading VBIOS from platform firmware. It provides fast and spec-compliant slow variants.

### Important APIs, types, and functions

`nvbios_acpi_fast` and `nvbios_acpi_slow` are `nvbios_source` instances. Helpers evaluate ACPI ROM with offset/length arguments and read chunks into `bios->data`.

### Control flow

The fast reader rounds requests to 4 KiB boundaries and fetches larger blocks for speed; the slow reader follows smaller access expectations. Init locates the ACPI ROM handle, read calls evaluate it, and fini has no complex state.

### State and persistence behavior

Backend state is the ACPI handle. The selected image is later owned by `bios->data` if this source wins.

### Dependencies and integration points

Depends on ACPI and x86 config, Linux ACPI object evaluation, and the shadow-source interface. It is one of the fallback sources used by `shadow.c`.

### Risks

ACPI firmware can reject large reads or return short buffers; fast mode deliberately bends the spec and may fail where slow mode works. Non-ACPI builds return errors.

### Test signals

Source read size: 140 lines, 4001 bytes. Laptop boot tests, fast-vs-slow fallback timing, ACPI failure injection, and validation on systems where PCI ROM is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowacpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowof.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowof.c

### Purpose

Open Firmware/device-tree VBIOS shadow backend. It reads a ROM blob property supplied by firmware on OF platforms.

### Important APIs, types, and functions

`nvbios_of` and `nvbios_platform`-style OF source definitions expose init/fini/read/size callbacks. The private state stores a pointer and size for the firmware-provided ROM data.

### Control flow

Init locates the firmware property, read copies requested ranges into `bios->data`, size reports the blob length, and fini releases any allocated wrapper state.

### State and persistence behavior

Persistent state is only selected if `shadow.c` chooses this backend; otherwise the copied candidate buffer is freed.

### Dependencies and integration points

Depends on OF/device-tree APIs and the generic shadow-source interface. Used mainly on non-PC platforms where PCI ROM access may not be available.

### Risks

Firmware-provided blobs can be missing, truncated, or not PCIR formatted depending on platform. Source flags determine whether PCIR/checksum validation is required.

### Test signals

Source read size: 89 lines, 2391 bytes. OF platform boot tests, VBIOS property fixture validation, short-read tests, and fallback to other sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowof.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowpci.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowpci.c

### Purpose

PCI ROM shadow backend. It maps or enables the PCI expansion ROM and copies VBIOS bytes through the shadow-source interface.

### Important APIs, types, and functions

`nvbios_pcirom` defines init/read/size/fini callbacks. The implementation handles PCI ROM enable/map lifetime and reports available ROM size.

### Control flow

Init obtains access to the PCI ROM resource, read copies offsets into the BIOS buffer, and fini releases/unmaps the PCI ROM. `shadow.c` scores the copied image afterward.

### State and persistence behavior

Backend mapping state is temporary. If selected, only the copied BIOS buffer persists.

### Dependencies and integration points

Depends on Linux PCI ROM helpers and the NVKM device's PCI handle. It is a primary source on discrete PCI/PCIe GPUs.

### Risks

PCI ROM access can be disabled, truncated, or unavailable after firmware handoff. Mapping lifetime and enable/disable ordering must be correct.

### Test signals

Source read size: 134 lines, 3173 bytes. Discrete GPU boot tests, PCI ROM access failure fallback, runtime PM/suspend interactions, and comparison with `/sys/bus/pci/.../rom` dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowpci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowramin.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowramin.c

### Purpose

RAMIN shadow backend. It reads a VBIOS image that firmware or hardware left in GPU instance/RAMIN memory.

### Important APIs, types, and functions

`nvbios_ramin` defines callbacks; internal code reads GPU memory through device MMIO/memory access windows and reports source size.

### Control flow

Init prepares any required private state, read copies aligned ranges from RAMIN into the BIOS buffer, and fini releases wrapper allocations. The generic shadow code validates the result.

### State and persistence behavior

No long-lived state unless this candidate wins; the copied image becomes `bios->data`.

### Dependencies and integration points

Depends on NVKM device memory/MMIO access and the shadow-source interface. It is useful when PROM/PCI ROM are not directly readable.

### Risks

RAMIN contents may be stale, relocated, or partially overwritten. Read alignment and size assumptions must match hardware.

### Test signals

Source read size: 123 lines, 3542 bytes. Boot tests on systems where RAMIN is the selected source, comparison to PROM/PCI ROM images, and corrupt/truncated RAMIN fallback tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowramin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowrom.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowrom.c

### Purpose

PROM/ROM shadow backend. It reads the GPU's on-board VBIOS ROM through device ROM access registers.

### Important APIs, types, and functions

`nvbios_prom` is the exported `nvbios_source`; callbacks read ROM bytes and report size through the NVKM device interface.

### Control flow

The backend opens access to the PROM, reads requested offsets for `shadow_fetch()`, and lets the generic shadow scorer validate image signatures and checksums.

### State and persistence behavior

Backend state is temporary; a selected PROM image persists as the BIOS data buffer.

### Dependencies and integration points

Depends on low-level NVKM device ROM reads and the shadow-source interface. It is one of the first sources tried for a native ROM image.

### Risks

ROM access can fail on some laptops or firmware-managed systems; wrong size reporting causes shadow validation failures.

### Test signals

Source read size: 64 lines, 2035 bytes. PROM boot tests, forced source selection with `NvBios=prom`, checksum failure fallback, and comparison with PCI ROM dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowrom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/therm.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/therm.c

### Purpose

Parser for thermal sensor, threshold, and fan policy records from BIT `P` thermal tables.

### Important APIs, types, and functions

`nvbios_therm_sensor_parse()` decodes core-domain sensor calibration and thresholds; `nvbios_therm_fan_parse()` decodes fan duty limits, trip points, periods, linear mode, and PWM frequency.

### Control flow

The thermal table pointer is read from BIT P version 1 or 2 at different offsets. Entries are type/value pairs; sensor parsing tracks threshold and sensor sections, while fan parsing accumulates trip points and mode from entry ids.

### State and persistence behavior

No persistent state. Thermal subdevices own live sensor/fan state after consuming decoded policy.

### Dependencies and integration points

Depends on BIT P and therm public types. It integrates with thermal monitoring, fan control, and power safety paths.

### Risks

Entry ids are sparse and partially understood. Wrong threshold or fan-duty parsing can cause overheating, noisy fan behavior, or missing shutdown thresholds.

### Test signals

Source read size: 212 lines, 5656 bytes. Thermal sensor calibration checks, fan curve tests, threshold trip tests, VBIOS fixture parsing, and Fermi+ linear-mode fallback validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/therm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/timing.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/timing.c

### Purpose

Parser for memory timing tables under BIT `P`. It decodes per-index timing records used with RAM map/config selection.

### Important APIs, types, and functions

`nvbios_timingTe()`, `nvbios_timingEe()`, and `nvbios_timingEp()` locate the table, address entries, and fill `struct nvbios_ramcfg` timing fields.

### Control flow

The table pointer is found through BIT P. Supported versions provide header/count/entry size; the parser indexes a timing entry and decodes many memory timing bytes/bitfields by version.

### State and persistence behavior

No state. Parsed timing fields are transient inputs to memory controller programming.

### Dependencies and integration points

Depends on BIT P, `ramcfg` structures, and generic BIOS reads. Memory init/reclock code combines this with RAMCFG/RAMMAP data.

### Risks

Timing bitfields are hardware-critical. Off-by-one timing index or version mismatch can prevent memory training or cause data corruption.

### Test signals

Source read size: 173 lines, 5665 bytes. Memory init/reclock tests, timing table dump comparison, VBIOS fixtures for supported versions, and stress tests after reclocking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/timing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/vmap.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/vmap.c

### Purpose

Parser for voltage-map tables. It maps voltage ids or VID indexes to actual microvolt values and policy fields.

### Important APIs, types, and functions

`nvbios_vmapTe/Ee/Ep()` parse table headers and entries; match helpers locate records by voltage id or index depending on table version.

### Control flow

The table pointer is read from BIT P metadata. Supported versions expose header/count/entry size, and entry parsing extracts voltage ids, min/max or mapped voltage values, and version-specific flags.

### State and persistence behavior

No persistent state. Voltage subdevices consume decoded maps to build runtime voltage tables.

### Dependencies and integration points

Depends on BIT P, generic reads, and voltage parser users such as `volt.c` and pstate/reclock code.

### Risks

Wrong units or id matching can choose unsafe voltages. Unsupported versions need graceful failure to keep conservative defaults.

### Test signals

Source read size: 121 lines, 3618 bytes. Voltage table dump comparison, reclocking voltage transitions, VBIOS fixtures, and power/thermal stress after voltage changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/vmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/volt.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/volt.c

### Purpose

Parser for primary voltage tables under BIT `P`. It decodes voltage table metadata, entries, GPIO/VID relationships, and voltage ranges.

### Important APIs, types, and functions

`nvbios_voltTe/Tp()`, `nvbios_voltEe/Ep()`, and matching helpers expose table and entry parsing for `struct nvbios_volt*` consumers.

### Control flow

The parser locates the voltage table pointer from BIT P, accepts supported versions, reads header/count/entry sizes, then decodes VID, voltage in microvolts, and min/max or PWM/GPIO-related fields by version.

### State and persistence behavior

No state. The voltage subdevice owns any live voltage rails or regulator objects created from decoded data.

### Dependencies and integration points

Depends on BIT P, VBIOS reads, and vmap/perf/pstate code. Reclocking and power management use these limits.

### Risks

Voltage parsing mistakes are high risk because they can overvolt or undervolt hardware. Missing tables must leave conservative behavior.

### Test signals

Source read size: 160 lines, 4808 bytes. Voltage table fixtures, regulator programming tests, pstate transition tests, and hardware telemetry comparison where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/volt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/vpstate.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/vpstate.c

### Purpose

Parser for voltage-pstate mapping tables. It links performance states to voltage or boost policy records.

### Important APIs, types, and functions

`nvbios_vpstateTe/Ee/Ep()` and match helpers parse table headers and entries into structures declared in `vpstate.h`.

### Control flow

The table is reached through BIT P, validated by version, then indexed with header/count/length fields. Entries expose pstate indexes and voltage-related values for caller matching.

### State and persistence behavior

No persistent state. Parsed records are consumed by clock/voltage management.

### Dependencies and integration points

Depends on BIT P, VBIOS readers, and pstate/voltage users.

### Risks

Mismatched pstate indexes can select wrong voltage limits for a performance state. Unsupported tables must not produce partial bogus records.

### Test signals

Source read size: 88 lines, 2642 bytes. Pstate/voltage transition tests, VBIOS fixture parsing, and comparison of decoded maps with vendor tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/vpstate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/xpio.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/xpio.c

### Purpose

Parser for external GPIO provider tables. It complements DCB GPIO parsing when GPIO functions live behind external devices.

### Important APIs, types, and functions

`dcb_xpio_table()`, entry accessors, parse/match helpers decode XPIO records and provider metadata from DCB-related tables.

### Control flow

The parser locates XPIO table pointers from modern DCB data, validates version/header/count/length, and decodes external GPIO line, function, and provider identifiers.

### State and persistence behavior

No state. The GPIO subsystem owns live external GPIO objects after consuming decoded records.

### Dependencies and integration points

Depends on DCB, GPIO table parsing, and generic BIOS reads. It integrates with display hotplug, fan, and board-control GPIO logic.

### Risks

Wrong provider/line parsing can toggle external devices incorrectly or miss GPIO-backed signals.

### Test signals

Source read size: 74 lines, 2521 bytes. External GPIO board tests, hotplug/fan GPIO validation, VBIOS fixture parsing, and absent-XPIO fallback tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/xpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/Kbuild -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/Kbuild

### Purpose

Build manifest for NVKM bus subdevice support.

### Important APIs, types, and functions

Adds `base.o`, `hwsq.o`, and bus implementations for `nv04`, `nv31`, `nv50`, `g94`, and `gf100` to `nvkm-y`.

### Control flow

No runtime flow; Kbuild aggregates the bus core, hardware sequencer, and generation-specific interrupt/init handlers.

### State and persistence behavior

No runtime state. Build composition determines which `*_bus_new()` constructors and HWSQ helpers are available.

### Dependencies and integration points

Depends on parent Nouveau Kbuild. Device chipset selection code links against the constructors listed here.

### Risks

Missing objects cause unresolved constructors or missing interrupt support for a GPU generation.

### Test signals

Source read size: 8 lines, 262 bytes. Nouveau build, allmodconfig, and link checks for bus constructors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/base.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/base.c

### Purpose

Generic NVKM bus subdevice wrapper. It adapts generation-specific bus functions to the NVKM subdevice lifecycle.

### Important APIs, types, and functions

`nvkm_bus_new_()` allocates and constructs a bus object; `nvkm_bus_init()` and `nvkm_bus_intr()` dispatch to `bus->func`; `nvkm_bus_dtor()` returns the object for freeing.

### Control flow

Construction installs the common `nvkm_subdev_func` table and the generation-specific `nvkm_bus_func`. Init and interrupt callbacks are thin dispatchers.

### State and persistence behavior

`struct nvkm_bus` persists as the device bus subdevice and stores only the function table plus embedded subdev.

### Dependencies and integration points

Depends on `priv.h`, NVKM allocation helpers, and subdevice lifecycle. Generation files call `nvkm_bus_new_()`.

### Risks

No null checks around required callbacks, so generation function tables must provide valid init/intr methods when used.

### Test signals

Source read size: 64 lines, 1984 bytes. Build/link tests and boot-time init/interrupt dispatch on each bus generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/g94.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/g94.c

### Purpose

G94-generation bus implementation. It extends NV50-style bus support with a larger HWSQ program capacity and generation-specific interrupt behavior.

### Important APIs, types, and functions

`g94_bus_new()` constructs the bus; the `g94_bus` function table provides init/intr methods inherited from NV50 helpers plus HWSQ execution sizing/support.

### Control flow

Creation calls `nvkm_bus_new_()`. Runtime init and interrupt handling follow NV50 paths, while HWSQ users can emit sequences up to this generation's supported size.

### State and persistence behavior

Persistent state is the generic `struct nvkm_bus`; hardware interrupt masks and HWSQ engine state live in registers.

### Dependencies and integration points

Depends on `nv50_bus_init/intr`, HWSQ support, and the bus private interface. Display/memory code can use bus HWSQ execution on supported GPUs.

### Risks

Incorrect HWSQ size or inherited interrupt masks can break display/memory script execution or leave interrupts unhandled.

### Test signals

Source read size: 65 lines, 2148 bytes. Boot on G94-class hardware, HWSQ execution tests, interrupt storm/fault tests, and display init sequences using HWSQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/g94.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/gf100.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/gf100.c

### Purpose

GF100/Fermi bus implementation. It provides Fermi-era interrupt initialization and HWSQ execution support.

### Important APIs, types, and functions

`gf100_bus_new()` and the `gf100_bus` function table bind generation-specific init, intr, HWSQ exec, and HWSQ size values.

### Control flow

Init clears/enables bus interrupt registers for Fermi layout. Interrupt handling reads status/mask registers, logs or dispatches known faults/subdevice interrupts, acknowledges handled bits, and masks unknown bits.

### State and persistence behavior

State persists in bus hardware masks/status and the generic bus object. HWSQ state is transient during execution.

### Dependencies and integration points

Depends on timer/MMIO helpers, therm/gpio subdevices where relevant, and HWSQ interface. Used by Fermi+ chipset constructors.

### Risks

Interrupt status definitions must match hardware; masking unknown bits can hide future events. HWSQ timeout handling must avoid leaving sequencer active.

### Test signals

Source read size: 81 lines, 2650 bytes. Fermi boot, MMIO fault interrupt tests, thermal/GPIO interrupt propagation, and HWSQ sequence execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/gf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/hwsq.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/hwsq.c

### Purpose

Assembler/emitter for NVKM bus hardware sequencer microcode. It builds compact command streams for register writes, flag waits, vblank waits, and delays, then optionally executes them through the bus backend.

### Important APIs, types, and functions

`nvkm_hwsq_init()`, `nvkm_hwsq_fini()`, `nvkm_hwsq_wr32()`, `nvkm_hwsq_setf()`, `nvkm_hwsq_wait()`, `nvkm_hwsq_wait_vblank()`, and `nvkm_hwsq_nsec()` are the public helpers.

### Control flow

Init allocates a 512-byte command buffer. Emitters append bytecode while caching high 16 bits of address/data to reduce stream size. Fini pads to dwords, verifies against `bus->func->hwsq_size`, optionally calls `hwsq_exec`, logs failures and bytecode, then frees the object.

### State and persistence behavior

Sequencer builder state is transient: cached address/data and command buffer size. Executed bytecode has hardware side effects through the bus sequencer.

### Dependencies and integration points

Depends on bus function table, NVKM MMIO reads for vblank selection, timer/backend execution, and display head registers. Used by low-level init paths that need ordered register programming.

### Risks

Buffer overflow is guarded only by final size check against the backend, while byte appends assume the 512-byte local buffer is sufficient. Vblank head selection is heuristic.

### Test signals

Source read size: 177 lines, 4562 bytes. HWSQ size boundary tests, execution timeout/failure logs, display vblank wait tests, and register trace comparison for generated bytecode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/hwsq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/hwsq.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/hwsq.h

### Purpose

Header-only helper API for a newer structured hardware-sequencer builder. It defines register descriptors and inline operations for composing register reads, writes, masks, waits, and delays.

### Important APIs, types, and functions

Defines `struct hwsq`, `struct hwsq_reg`, `hwsq_reg()`, `hwsq_stride()`, `hwsq_reg2()`, and inline helpers for register write/mask/read-style operations over an abstract `struct hwsq` backend.

### Control flow

There is no standalone runtime flow. Callers construct `hwsq_reg` descriptors and invoke inlines that delegate to function pointers in `struct hwsq` or apply register address arithmetic.

### State and persistence behavior

No storage is allocated by the header. It describes transient command-building state owned by the caller/backend.

### Dependencies and integration points

Depends on basic kernel integer types. It integrates with bus/display code that wants a typed HWSQ abstraction rather than the older bytecode emitter API.

### Risks

Inline address arithmetic must preserve stride/index semantics. Because this is a header, API mistakes propagate at compile time across all users.

### Test signals

Source read size: 148 lines, 2601 bytes. Compile coverage for all HWSQ users, generated command trace comparison, and tests for stride/indexed register helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/hwsq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/nv04.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/nv04.c

### Purpose

NV04-era bus implementation. It handles basic bus errors and GPIO interrupt forwarding for early GPUs.

### Important APIs, types, and functions

`nv04_bus_new()`, `nv04_bus_init()`, and `nv04_bus_intr()` implement the generation function table.

### Control flow

Init acknowledges all pending status and enables bus/GPIO-related masks. Interrupt handling reads `0x001100 & 0x001140`, reports bus errors, forwards GPIO-related bits to the GPIO subdevice, acknowledges handled bits, and masks unknown interrupts.

### State and persistence behavior

Persistent state is hardware interrupt masks/status and the generic bus object. No heap state beyond `struct nvkm_bus`.

### Dependencies and integration points

Depends on GPIO subdevice dispatch and MMIO helpers. It is selected for NV04-class devices.

### Risks

Incorrect masks can miss GPIO events or leave interrupt storms. Early hardware has sparse diagnostics, so unknown interrupt logging is important.

### Test signals

Source read size: 75 lines, 2347 bytes. Boot on NV04/NV1x hardware, GPIO interrupt tests, forced bus-error logging, and interrupt mask verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/nv04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/nv31.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/nv31.c

### Purpose

NV31/NV4x-era bus implementation. It handles GPIO, MMIO fault, and thermal interrupt routing.

### Important APIs, types, and functions

`nv31_bus_new()`, `nv31_bus_init()`, and `nv31_bus_intr()` implement the bus function table.

### Control flow

Interrupt handling reads bus and GPIO status/mask pairs, forwards GPIO interrupts, logs MMIO read/write faults from `0x009084/0x009088`, forwards thermal bits, acknowledges known bits, and masks unknown status. Init enables MMIO fault and thermal masks.

### State and persistence behavior

Persistent state is in hardware interrupt masks/status. The generic bus object has only function-table state.

### Dependencies and integration points

Depends on GPIO and thermal subdevices plus MMIO helpers. Used on NV31/NV4x-class devices.

### Risks

MMIO fault decoding must not flood logs, so ratelimited logging matters. Wrong masks can break thermal safety or GPIO hotplug.

### Test signals

Source read size: 89 lines, 2775 bytes. NV31/NV4x boot, MMIO fault injection, thermal interrupt tests, GPIO interrupt propagation, and interrupt storm handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/nv31.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/nv50.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/nv50.c

### Purpose

NV50-generation bus implementation with HWSQ execution and interrupt routing for thermal/fault events.

### Important APIs, types, and functions

`nv50_bus_new()`, `nv50_bus_hwsq_exec()`, `nv50_bus_init()`, and exported `nv50_bus_intr()` provide the base for NV50/G9x derivatives.

### Control flow

HWSQ exec writes dwords to sequencer RAM at `0x001400`, starts execution via control registers, and polls completion with a 2s timeout. Interrupt handling reads bus status/masks, routes thermal events, logs known/unknown faults, acknowledges handled bits, and masks unknown bits.

### State and persistence behavior

HWSQ command memory and interrupt masks are hardware state. The software bus object persists as generic subdevice state.

### Dependencies and integration points

Depends on timer polling, therm subdevice, MMIO helpers, and bus HWSQ interface. G94 and later files reuse parts of this implementation.

### Risks

Sequencer timeout leaves init sequences failed. Interrupt mask mistakes can hide thermal events or produce repeated unknown interrupts.

### Test signals

Source read size: 106 lines, 3154 bytes. NV50 boot, HWSQ execution tests, thermal interrupt tests, timeout injection, and register trace validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/nv50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/priv.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/priv.h

### Purpose

Private bus subdevice header. It defines the generation-specific bus callback contract and shared constructor prototype.

### Important APIs, types, and functions

`struct nvkm_bus_func` contains `init`, `intr`, optional `hwsq_exec`, and `hwsq_size`. It declares `nvkm_bus_new_()`, `nv50_bus_init()`, and `nv50_bus_intr()`.

### Control flow

No runtime control flow. Generation files populate this table, and `base.c` dispatches through it.

### State and persistence behavior

No state by itself. The callback table controls persistent behavior of each bus object.

### Dependencies and integration points

Depends on `subdev/bus.h` and NVKM device/subdev types. Included by all bus implementation files.

### Risks

Changing the callback contract affects every generation. Missing required callbacks lead to null dispatch at runtime.

### Test signals

Source read size: 19 lines, 549 bytes. Compile coverage and boot/init/interrupt tests for every bus generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/Kbuild -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/Kbuild

### Purpose

Build manifest for NVKM clock subdevice implementations and PLL helpers.

### Important APIs, types, and functions

Adds clock core and generation files (`base`, `nv04`, `nv40`, `nv50`, `g84`, `gt215`, `mcp77`, `gf100`, `gk104`, `gk20a`, `gm20b`, `gp10b`), optional `gk20a_devfreq.o`, and PLL helper objects `pllnv04.o` and `pllgt215.o`.

### Control flow

No runtime flow; Kbuild composes the clock subsystem objects selected by config.

### State and persistence behavior

No runtime state. Build composition determines which chipset clock constructors and PLL helpers are linked.

### Dependencies and integration points

Depends on parent Nouveau Kbuild and `CONFIG_PM_DEVFREQ` for Tegra GK20A devfreq support. Clock device-selection code relies on these objects.

### Risks

Missing entries break chipset support or optional devfreq integration. Stale entries cause build failures.

### Test signals

Source read size: 17 lines, 568 bytes. Nouveau build, allmodconfig with and without `CONFIG_PM_DEVFREQ`, and link checks for clock constructors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/Kbuild -->
