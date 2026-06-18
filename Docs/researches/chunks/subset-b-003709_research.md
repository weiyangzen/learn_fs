# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atombios.h lines 1-5115

## Chunk Scope

This chunk covers the first 5,115 lines of `sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atombios.h`. The file is a byte-packed ABI header shared between Radeon VBIOS ATOM tables and the kernel driver/parser code. This range contains the global ATOM header constants, ROM/master table layouts, many command-table parameter structures, and the first large group of persisted data-table formats through early Trinity/Fusion integrated-system information.

The code is mostly declarations, constants, packed structs, unions, aliases, and revisioned table shapes. There are no executable C functions in this range; control flow is represented by table lookup offsets, command-table action opcodes, versioned parameter layouts, object-record chains, and BIOS/driver contracts.

## Purpose

The main purpose is to define the binary contract used by the Radeon driver when it reads an ATOM BIOS ROM and when it invokes ATOM command tables. `#pragma pack(1)` is applied because these structs map directly over firmware bytes. Most fields are explicitly sized with `UCHAR`, `USHORT`, and `ULONG`, and many structs begin with `ATOM_COMMON_TABLE_HEADER`, which supplies table size plus format/content revisions.

This chunk establishes:

- How to find the ATOM ROM header and master command/data tables.
- Stable command-table indices for ASIC init, CRTC control, encoder/transmitter control, clocks, I2C/AUX, voltage, power connector detection, spread spectrum, and related services.
- Parameter-space structs used when calling VBIOS command tables.
- Data-table structs for firmware clocks/capabilities, integrated-system information, GPIO/I2C routing, display timings, LCD/panel details, spread spectrum, analog/component TV, VRAM reservation, object topology, voltage controls, ASIC profiling, power source detection, and APU/fusion platform data.
- Compatibility aliases that map old table names to newer master-table slots.

## Important APIs, Types, and Constants

### ROM and Table Discovery

`OFFSET_TO_POINTER_TO_ATOM_ROM_HEADER`, `OFFSET_TO_ATOM_ROM_IMAGE_SIZE`, `OFFSET_TO_ATOMBIOS_ASIC_BUS_MEM_TYPE`, and related string offsets describe fixed locations inside the BIOS image. `ATOM_ROM_HEADER` contains the ATOM signature, legacy BIOS offsets, PCI IDs, I/O base, and the offsets for `ATOM_MASTER_COMMAND_TABLE` and `ATOM_MASTER_DATA_TABLE`.

`ATOM_COMMON_TABLE_HEADER` is the root header for nearly every table. `ATOM_MASTER_LIST_OF_COMMAND_TABLES` and `ATOM_MASTER_LIST_OF_DATA_TABLES` are the primary dispatch/index structures. Their members are `USHORT` offsets, not direct pointers, so consumers must bounds-check and add them to the BIOS image base.

`ATOM_TABLE_ATTRIBUTE`, `ATOM_TABLE_ATTRIBUTE_ACCESS`, and `ATOM_COMMON_ROM_COMMAND_TABLE_HEADER` describe command-table parser metadata such as parameter-space and workspace sizes. Bitfield ordering is guarded by `ATOM_BIG_ENDIAN`, and the header refuses inclusion without an endian decision.

### Command-Table Parameter Families

Clock programming is represented by several revisioned structs:

- `COMPUTE_MEMORY_ENGINE_PLL_PARAMETERS`, `_V2`, `_V3`, `_V4`, `_V5`, plus `COMPUTE_GPU_CLOCK_INPUT_PARAMETERS_V1_6` and `COMPUTE_GPU_CLOCK_OUTPUT_PARAMETERS_V1_6`.
- `SET_ENGINE_CLOCK_PARAMETERS`, `SET_ENGINE_CLOCK_PS_ALLOCATION`, `SET_MEMORY_CLOCK_PARAMETERS`, and `SET_MEMORY_CLOCK_PS_ALLOCATION`.
- `PIXEL_CLOCK_PARAMETERS`, `_V2`, `_V3`, `_V5`, `_V6`, `CRTC_PIXEL_CLOCK_FREQ`, and `ADJUST_DISPLAY_PLL_*`.

The command ABI uses 10 kHz units for most clocks, frequently stores 24-bit clock fields in endian-sensitive bitfields, and carries revision-specific control flags such as `ATOM_PLL_CNTL_FLAG_*`, `PIXEL_CLOCK_MISC_*`, and `PIXEL_CLOCK_V5/V6_MISC_*`.

Display pipe and encoder control appears in:

- `ENABLE_CRTC_PARAMETERS`, `BLANK_CRTC_PARAMETERS`, `SET_CRTC_OVERSCAN_PARAMETERS`, `SET_CRTC_REPLICATION_PARAMETERS`, `SELECT_CRTC_SOURCE_PARAMETERS`, and `_V2`.
- `DAC_LOAD_DETECTION_PARAMETERS`, `DAC_ENCODER_CONTROL_PARAMETERS`, `TV_ENCODER_CONTROL_PARAMETERS`, and output-control aliases for CRT/TV/CV/DFP/LCD/DVO.
- `DIG_ENCODER_CONTROL_PARAMETERS` through `_V4`, with companion bitfield config structs `ATOM_DIG_ENCODER_CONFIG_V2`, `_V3`, and `_V4`.
- `DIG_TRANSMITTER_CONTROL_PARAMETERS` through `_V1_5`, with `ATOM_DIG_TRANSMITTER_CONFIG_V2` through `_V5`.
- `EXTERNAL_ENCODER_CONTROL_PARAMETERS_V3`, `LVDS_ENCODER_CONTROL_PARAMETERS` and `_V2`, DVO encoder parameter structs, and TMDS/LVDS aliases.

The encoder/transmitter families encode DP link training commands (`ATOM_ENCODER_CMD_DP_LINK_TRAINING_*`), link rates, transmitter/link selection, HPD selection, DP lane voltage/pre-emphasis/post-cursor programming, encoder modes, and panel mode setup. Revision differences matter: for example V4 encoder config supports 5.40 GHz and 3.24 GHz link-rate encodings, transmitter V4 adds DCPLL/refclk changes, and transmitter V1.5 switches to explicit PHY IDs and DIG encoder masks.

I2C and platform service commands include `READ_EDID_FROM_HW_I2C_DATA_PARAMETERS`, `WRITE_ONE_BYTE_HW_I2C_DATA_PARAMETERS`, `SET_UP_HW_I2C_DATA_PARAMETERS`, `POWER_CONNECTOR_DETECTION_PARAMETERS`, and `POWER_CONNECTOR_DETECTION_PS_ALLOCATION`. These share status values like `HW_ASSISTED_I2C_STATUS_SUCCESS` and `HW_ASSISTED_I2C_STATUS_FAILURE`.

Voltage and power command structs include `SET_VOLTAGE_PARAMETERS`, `_V2`, `_V1_3`, `SET_VOLTAGE_PS_ALLOCATION`, `GET_VOLTAGE_INFO_INPUT_PARAMETER_V1_1`, `_V1_2`, `GET_VOLTAGE_INFO_OUTPUT_PARAMETER_V1_1`, `GET_LEAKAGE_VOLTAGE_INFO_OUTPUT_PARAMETER_V1_1`, and `GET_EVV_VOLTAGE_INFO_OUTPUT_PARAMETER_V1_2`. The mode constants distinguish setting a voltage, regulator init, phase programming, virtual voltage lookup, leakage IDs, SVID2 information, and EVV voltage lookup.

### Master Data Tables and Persisted BIOS State

`ATOM_MASTER_LIST_OF_DATA_TABLES` indexes persistent ATOM data tables. This chunk defines tables for multimedia capability/config, firmware info, LCD/LVDS info, GPIO/I2C, VRAM usage, GPIO pin LUT, component video, object topology, integrated system info, profiling, voltage objects, and power source information. Backward-compatible aliases map `LVDS_Info` to `LCD_Info`, `DAC_Info` to `PaletteData`, and `TMDS_Info` to `DIGTransmitterInfo`.

Firmware information is revisioned from `ATOM_FIRMWARE_INFO` through `ATOM_FIRMWARE_INFO_V2_2`, with `ATOM_FIRMWARE_INFO_LAST` set to V2.2. These structs persist default engine/memory clocks, PLL limits, pixel-clock limits, firmware capabilities, reference clocks, boot voltages, display-engine clock, memory module ID, and related reserved or repurposed fields. `ATOM_FIRMWARE_CAPABILITY_ACCESS` exposes firmware capability bits such as firmware-posted, dual CRTC, extended desktop, spread spectrum support, backlight controlled by GPU, WMI, HyperMemory, and post-without-mode-set.

Integrated platform data appears in `ATOM_INTEGRATED_SYSTEM_INFO`, `_V2`, `_V5`, `_V6`, and `_V1_7`, with `ATOM_FUSION_SYSTEM_INFO_V1` wrapping V6 plus an embedded PowerPlay table area. These tables persist APU/IGP boot clocks, UMA/SidePort clocks, display vectors, DDI slot configs, CPU and HT/NB details, voltage data, memory latency numbers used for watermarks, PWM/backlight requests, spread-spectrum percentages, SCLK/voltage capabilities, arbitration tables, NCLK and DDR PHY timing, power/boost limits, external display connection info, and LVDS/eDP panel control. `ATOM_TDP_CONFIG` stores cTDP/TDP fields as endian-sensitive bitfields.

Display timing and panel data are defined by `ATOM_MODE_MISC_INFO_ACCESS`, `SET_CRTC_USING_DTD_TIMING_PARAMETERS`, `SET_CRTC_TIMING_PARAMETERS`, `ATOM_MODE_TIMING`, and `ATOM_DTD_FORMAT`. LCD/panel tables include `ATOM_LVDS_INFO`, `ATOM_LVDS_INFO_V12`, and `ATOM_LCD_INFO_V13`, plus patch records such as `ATOM_PATCH_RECORD_MODE`, `ATOM_LCD_RTS_RECORD`, `ATOM_LCD_MODE_CONTROL_CAP`, `ATOM_FAKE_EDID_PATCH_RECORD`, and `ATOM_PANEL_RESOLUTION_PATCH_RECORD`.

Object-topology tables include `ATOM_OBJECT_HEADER`, `ATOM_OBJECT_HEADER_V3`, `ATOM_DISPLAY_OBJECT_PATH`, `ATOM_DISPLAY_OBJECT_PATH_TABLE`, `ATOM_OBJECT`, `ATOM_OBJECT_TABLE`, and `ATOM_SRC_DST_TABLE_FOR_ONE_OBJECT`. Record structures use `ATOM_COMMON_RECORD_HEADER` followed by typed payloads for I2C, HPD, output protection, connector device tags, GPIO control, DVO/connector capabilities, hardcoded DTD, router mux selection, external HPD/AUX LUTs, linked objects, remote capabilities, encoder capabilities, and bracket layout.

Voltage data tables are separate from voltage command parameters. `ATOM_VOLTAGE_INFO`, `ATOM_VOLTAGE_FORMULA`, `ATOM_VOLTAGE_FORMULA_V2`, `ATOM_VOLTAGE_CONTROL`, `ATOM_VOLTAGE_OBJECT`, `_V2`, `ATOM_VOLTAGE_OBJECT_HEADER_V3`, `ATOM_I2C_VOLTAGE_OBJECT_V3`, `ATOM_GPIO_VOLTAGE_OBJECT_V3`, `ATOM_LEAKAGE_VOLTAGE_OBJECT_V3`, `ATOM_SVID2_VOLTAGE_OBJECT_V3`, and `ATOM_VOLTAGE_OBJECT_INFO_V3_1` describe how the driver should translate requested voltages into GPIO, I2C, SVID2, phase, leakage, or regulator-init operations.

### Device, Connector, and Routing Constants

The chunk defines device indices/support bits for CRT, LCD, TV, CV, and DFP1-DFP6. It also defines connector type fields, DAC identity fields, I2C ID/mux/hardware capability fields, encoder IDs, encoder attributes, encoder enumeration bits, HPD/AUX LUT sizes, DP/DVI channel mapping bitfields, GPIO pin control constants, and line/aspect-ratio GPIO semantics for component video.

These constants are central integration points for the DRM connector/encoder setup path. They convert BIOS tables into driver-level connector capabilities, link routing, DDC/AUX selection, HPD detection, and encoder/transmitter programming decisions.

## Control Flow and Data Flow

Although this chunk contains no executable functions, it defines several firmware-driven control flows:

1. ROM parsing begins at fixed offsets, reads `ATOM_ROM_HEADER`, validates the ATOM signature, then follows master command/data table offsets.
2. Command execution selects a slot in `ATOM_MASTER_LIST_OF_COMMAND_TABLES`, reads a command table header and parser attributes, allocates the required parameter/workspace, fills one of the parameter structs from this header, then runs the ATOM interpreter or command service.
3. Display setup uses data tables and object records to discover supported devices, connectors, DDC/AUX lines, HPD GPIOs, encoder paths, and panel/timing data, then calls command tables for clocks, encoder setup, transmitter setup, CRTC timing/source selection, output enable, and backlight.
4. Clock and power setup uses firmware/integrated-system tables for defaults and limits, then command parameters for PLL computation, memory/engine/pixel clock programming, spread spectrum, voltage control, and static/dynamic power management.
5. Panel bring-up sequences combine LCD data-table timing/power-sequence fields with command-table actions such as `ATOM_LCD_BLOFF`, `ATOM_LCD_BLON`, brightness control, DP panel mode setup, and transmitter power actions.
6. Voltage handling uses voltage object tables to translate a driver request into a GPIO/I2C/SVID2/EVV/leakage operation, then command-table parameter structs carry the chosen voltage mode and level.

The table layouts deliberately carry many offsets and flexible-array members. The driver is expected to iterate records by `ucRecordSize`, table sizes, and object counts rather than by C `sizeof` alone.

## State and Persistence Behavior

All data tables in this range represent persistent firmware state baked into the VBIOS image or, for some integrated-system tables, copied/provided by system BIOS before GPU VPOST. Examples include:

- Clock defaults, PLL limits, reference clocks, and boot voltage from firmware info.
- Boot display vectors, DDI lane routing, docking info, CPU/NB/HT details, memory latency, and UMA/SidePort clocks from integrated-system tables.
- LCD timing, panel power sequencing, eDP DPCD capabilities, supported refresh ranges, backlight PWM, and special panel handling caps.
- GPIO/I2C pin assignments, AUX/DDC/HPD LUTs, object records, and connector topology.
- VRAM reservation start/size used by firmware and driver command-table access areas.
- Voltage regulator control mechanisms, voltage lookup/formula data, leakage and profiling tables, power source detection behavior, and available SCLK/voltage lists.

Command parameter structs are transient ABI payloads placed in the ATOM parser parameter space. Some commands return values through the same struct/union fields, for example PLL calculation output, current clock queries, voltage lookup output, link-training status, power connector status, or display PLL status.

The ABI is versioned by each table's format/content revisions rather than by C type names. The driver must select the correct struct interpretation based on table revision and sometimes ASIC family. Several `*_LAST` aliases are only compile-time conveniences and may lag runtime table revisions if not handled carefully.

## Dependencies and Integration Points

The header depends on Radeon/ATOM base integer typedefs (`UCHAR`, `USHORT`, `ULONG`) and an explicit `ATOM_BIG_ENDIAN` setting. Under `_H2INC`, it defines simple versions of those types for a header-to-include generation path. Bitfields have separate big-endian and little-endian layouts, so all consumers must include the header with the same endian contract used by the target parser code.

External integration points include:

- ATOM parser/interpreter code that reads `ATOM_COMMON_ROM_COMMAND_TABLE_HEADER` and executes command tables.
- Radeon display initialization paths that consume object tables, connector records, encoder/transmitter parameters, CRTC timing structs, and panel tables.
- DRM connector/encoder abstractions that map ATOM device-support bits, object IDs, HPD records, DDC/AUX IDs, and routing records to kernel display objects.
- Power management code that consumes firmware info, integrated-system info, PowerPlay data embedded in fusion info, voltage object info, ASIC profiling info, and power-source info.
- I2C/AUX/GPIO helpers that map `ATOM_I2C_ID_CONFIG`, `ATOM_GPIO_I2C_ASSIGMENT`, `ATOM_GPIO_PIN_LUT`, and object GPIO records to hardware access.
- VRAM/memory management code that respects `ATOM_VRAM_USAGE_BY_FIRMWARE` and the fixed ATOM BIOS VRAM reservation layout for EDID, mode tables, hardware icons, DP training, and stack storage.
- Hardware register programming layers that interpret command outputs for PLLs, transmitters, voltage, spread spectrum, and panel/backlight control.

The include path indicates this copy sits under a Ceph client source mirror, but the content is Radeon DRM VBIOS ABI material and integrates with GPU display/power code rather than distributed filesystem logic.

## Risks and Sharp Edges

- Binary layout drift is the largest risk. `#pragma pack(1)`, endian-sensitive bitfields, unions, flexible arrays, and revisioned structs mean any accidental packing or typedef-size change can corrupt BIOS parsing.
- Many fields are offsets into the ROM image or offsets inside variable-sized tables. Missing bounds checks in consumers can cause out-of-bounds reads on malformed or vendor-custom BIOS images.
- Several names are misspelled or historically frozen (`DYNAMICE_*`, `TRASMITTER`, `Reseved`, `Votlage`, `embadded`, etc.). Renaming them would break source compatibility.
- Compatibility aliases can hide semantic changes. For example old LVDS/TMDS/DAC table names alias newer slots, and multiple command slots are renamed for later ASICs.
- `*_LAST` macros may not represent every runtime table version and should not substitute for revision checks.
- Flexible arrays such as object paths, object records, GPIO pins, voltage LUTs, and fake EDID blobs require careful length validation from table headers and record sizes.
- Some bit encodings are reused or corrected across revisions. Pixel-clock V6 HDMI BPP comments explicitly note corrected definitions, and firmware capability bits differ between older and newer revisions for internal versus external spread spectrum.
- Many clock units are 10 kHz, but some fields use MHz, Hz, 10 Hz, 0.01 us, ns, mV, watts, or tens of milliwatts. Mixing units would cause display instability, bad watermarks, or power/thermal errors.
- Some tables are documented as BIOS-only or obsolete, but still occupy stable master-table slots. Removing or reordering fields is unsafe.
- Voltage and power source tables can control real regulators. Invalid parsing or wrong mode selection can under/over-voltage hardware.
- Integrated-system tables include large reserved regions that firmware expects to remain zero or available for future use. Drivers should not assume reserved fields are meaningful unless gated by a known revision/platform.

## Test Signals

Useful validation signals for this chunk are mostly parser and hardware-integration tests rather than unit tests of functions:

- Build tests that include `atombios.h` with the expected endian define and verify no packing/type redefinition regressions.
- Static layout checks for key structs when available, especially `ATOM_COMMON_TABLE_HEADER`, `ATOM_ROM_HEADER`, master table lists, firmware info revisions, object records, and command parameter structs used by active driver code.
- BIOS parser tests with known Radeon VBIOS images across R5xx/R6xx/R7xx/Evergreen/Northern Islands/Southern Islands/Fusion/Trinity-era hardware, confirming table offsets, table sizes, and revision dispatch.
- Fuzz or negative tests for malformed table offsets, bad record sizes, truncated flexible arrays, invalid object counts, bad checksums, and unsupported table revisions.
- Display bring-up tests covering CRT/DVI/HDMI/LVDS/eDP/DP paths, including DDC/AUX, HPD, link training commands, pixel-clock programming, transmitter setup, panel power sequencing, and backlight behavior.
- Power-management tests that compare parsed firmware/integrated-system clocks, voltage IDs, voltage object modes, SCLK voltage lists, and power-source detection against known-good driver logs.
- Resume/suspend and mode-set tests, because BIOS-reserved VRAM, panel sequencing, command-table workspace sizing, and firmware capability bits commonly affect resume paths.
- Big-endian build or cross-compile checks, since this header has many endian-specific bitfield definitions and a hard `#error` if `ATOM_BIG_ENDIAN` is not specified.

## Cross-Chunk Notes

This chunk ends inside the description area for `ATOM_INTEGRATED_SYSTEM_INFO_V1_7`. Later chunks of the same file likely continue Trinity/APU integrated-system documentation and define additional ATOM/PowerPlay tables, object IDs, memory/VRAM tables, or newer ASIC revisions. The final per-file research should reconcile those later declarations with this chunk's command/data ABI foundation and avoid treating this first chunk as complete coverage of all `atombios.h` types.
