# subset-b-005052 Intel pinctrl research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-denverton.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-denverton.c

## Purpose

`pinctrl-denverton.c` supplies the static Intel Denverton SoC pin controller description consumed by the shared Intel pinctrl/GPIO core in `pinctrl-intel.c`. It maps Denverton pads 0-153 into named pins, muxable pin groups for UART0, UART1, UART2, and eMMC, two register communities, and ACPI/platform identifiers.

## Important APIs, Types, And Functions

The file is almost entirely declarative. It uses `PINCTRL_PIN()` for the pin table, `PIN_GROUP()` and `FUNCTION()` for mux exposure, `INTEL_GPP()` for pad-group metadata, and `INTEL_COMMUNITY_GPPS()` through `DNV_COMMUNITY()` to bind Denverton register offsets to each community. `dnv_soc_data` is the key exported payload, although it is static and reaches the core only through ACPI or platform match driver data. The driver entry points are `dnv_pinctrl_init()`, `dnv_pinctrl_exit()`, and the `platform_driver` with `.probe = intel_pinctrl_probe_by_hid`.

## Control Flow

During subsystem init, `platform_driver_register()` registers `denverton-pinctrl`. ACPI ID `INTC3000` or platform ID `denverton-pinctrl` carries `&dnv_soc_data`. Probe calls `intel_pinctrl_probe_by_hid()`, which fetches match data and calls the shared core. The core then maps community BARs, reads pad register bases and hardware capabilities, registers pinctrl and GPIO chips, and installs PM handling.

## State And Persistence

This file owns no mutable runtime state. Its static tables define North pins 0-40 and South pins 41-153, with pad groups split by hardware GPP boundaries. Runtime register state, GPIO ownership, IRQ masks, and suspend/resume pad context are allocated and maintained by `pinctrl-intel.c`. Denverton uses `subsys_initcall`, so registration occurs early enough for dependent devices that need GPIO/pinmux during boot.

## Dependencies And Integration Points

The driver depends on Linux platform, ACPI/module, PM, and pinctrl headers, and imports the `PINCTRL_INTEL` namespace. Integration is through the common Intel core's `intel_pinctrl_probe_by_hid()` and `intel_pinctrl_pm_ops`. The Denverton-specific register offsets are `DNV_PAD_OWN`, `DNV_PADCFGLOCK`, `DNV_HOSTSW_OWN`, `DNV_GPI_IS`, and `DNV_GPI_IE`.

## Risks

The main risk is table accuracy. A wrong pin number, mode array, pad-group range, GPIO base, or ACPI/platform ID would cause muxing, GPIO numbering, ownership checks, or interrupts to address the wrong pad. UART0 and UART2 use per-pin mode arrays, so array ordering must match the pin arrays exactly. Community boundaries also affect MMIO BAR selection and interrupt register indexing.

## Test Signals

Useful signals are successful probe on `INTC3000`, visible pin names and groups in pinctrl debugfs, UART/eMMC mux selection through pinctrl consumers, GPIO line enumeration across the expected ranges, and working shared IRQ delivery for Denverton GPPs. Suspend/resume should preserve active kernel-owned GPIO and mux state through the common PM callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-denverton.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-elkhartlake.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-elkhartlake.c

## Purpose

`pinctrl-elkhartlake.c` describes the Intel Elkhart Lake PCH GPIO/pinctrl topology. Unlike single-descriptor devices, it exposes six ACPI `_UID`-selected community devices, each with its own pin table, pad groups, and `intel_pinctrl_soc_data`.

## Important APIs, Types, And Functions

The file defines `EHL_COMMUNITY()` from the Elkhart Lake register offsets and uses `PINCTRL_PIN()`, `INTEL_GPP()`, and `INTEL_COMMUNITY_GPPS()` to build six SoC-data records. `ehl_soc_data_array` is a NULL-terminated table passed as ACPI match data for `INTC1020`. The platform driver uses `.probe = intel_pinctrl_probe_by_uid`, so the shared helper chooses the table entry whose `.uid` matches ACPI `_UID`.

## Control Flow

`module_platform_driver()` registers `elkhartlake-pinctrl`. On `INTC1020`, `intel_pinctrl_probe_by_uid()` calls `intel_pinctrl_get_soc_data()`, iterates `ehl_soc_data_array`, compares `_UID` against `"0"` through `"5"`, and then invokes `intel_pinctrl_probe()`. The common core performs MMIO mapping, pad-group normalization, pinctrl registration, GPIO chip registration, IRQ setup, and PM context allocation for that UID's community.

## State And Persistence

The static data separates community0 GPP_B/T/G, community1 GPP_V/H/D/U/vGPIO, community2 DSW, community3 CPU/GPP_S/GPP_A/vGPIO_3, community4 GPP_C/F/HVCMOS/GPP_E, and community5 GPP_R. Runtime state is not stored here; the common core owns register locks, GPIO chip state, interrupt masks, and suspend/resume snapshots.

## Dependencies And Integration Points

The driver depends on ACPI `_UID` correctness. It integrates with the common Intel core through `PINCTRL_INTEL`, `intel_pinctrl_probe_by_uid()`, and `intel_pinctrl_pm_ops`. The exposed hardware areas include embedded controller/eSPI, RGMII, SD/eMMC, I2C/UART/SPI/I2S, vGPIO, DSW, CPU, HVCMOS, and HDA pins.

## Risks

UID mismatches are the highest risk because a valid ACPI HID can still select no SoC data or the wrong community. GPIO base values are set to match pin bases in each UID-local controller, so consumers must not assume a global SoC-wide pin number across separate platform devices. Register offsets and GPP ranges must match hardware documentation or IRQ/status and ownership operations will be displaced.

## Test Signals

Probe should instantiate separate devices for `_UID` values 0-5. Debugfs should show only the pins for the matched UID. GPIO line counts should match each community's highest mapped GPP range. Regression tests should cover GPIO input/output, interrupt setup on non-ACPI-owned pads, and suspend/resume on DSW or wake-capable pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-elkhartlake.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-emmitsburg.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-emmitsburg.c

## Purpose

`pinctrl-emmitsburg.c` provides the Emmitsburg PCH pin map for the shared Intel pinctrl/GPIO core. It covers 262 pins across server-oriented eSPI, SPI, SMBus, SATA, JTAG, GBE/NCSI, CPU/platform management, and NAC groups.

## Important APIs, Types, And Functions

The important payload is `ebg_soc_data`, containing `ebg_pins` and five community descriptors. `EBG_COMMUNITY()` binds Emmitsburg-specific register offsets into `struct intel_community`. The driver table matches ACPI HID `INTC1071`, and the platform driver calls `intel_pinctrl_probe_by_hid()`.

## Control Flow

`module_platform_driver()` registers `emmitsburg-pinctrl`. ACPI matching supplies `&ebg_soc_data`. The common Intel probe copies the community templates, maps one BAR per community, discovers optional capabilities from hardware, creates pad groups from the provided `INTEL_GPP()` entries, registers pinctrl and GPIO, and wires the shared interrupt handler.

## State And Persistence

The file has no writable state after module load. It declares GPP ranges and GPIO bases: communities cover pins 0-65, 66-111, 112-145, 146-183, and 184-261. Suspend/resume state for active pads, interrupt masks, and host ownership registers is held in the core driver's `intel_pinctrl_context`.

## Dependencies And Integration Points

Emmitsburg depends on `pinctrl-intel.h` macros and the `PINCTRL_INTEL` namespace. Its ACPI integration is HID-based, not UID-based. Hardware integration points include server PCH GPIO ownership, eSPI/SPI, GBE, NCSI, SMBus, SATA sideband, and CPU error/reset signaling.

## Risks

This is a large server pin table where an off-by-one range can affect many GPIO numbers. The community names in comments are not executed, so correctness depends on the numeric `INTEL_GPP()` ranges and GPIO bases. Missing function/group tables mean this driver exposes GPIO/pad data but not named alternate-function mux groups through the generic pinmux function list.

## Test Signals

Probe on `INTC1071` should produce a gpiochip with ranges aligned to GPP_A/B/S, GPP_C/D, GPP_E/JTAG, GPP_H/J, and GPP_I/L/M/N. GPIO IRQ tests should confirm `EBG_GPI_IS`/`EBG_GPI_IE` offsets. Debugfs should show the expected pin names, ownership state, lock state, and ACPI mode flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-emmitsburg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-geminilake.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-geminilake.c

## Purpose

`pinctrl-geminilake.c` describes Intel Gemini Lake GPIO/pinctrl blocks split by ACPI `_UID`: northwest, north, audio, and SCC. It supplies both GPIO pad topology and mux groups for UART, PWM, I2C, SPI, SD card, SDIO, and eMMC functions.

## Important APIs, Types, And Functions

The file uses `GLK_COMMUNITY()` with `INTEL_COMMUNITY_SIZE()`, meaning pad groups are generated by size instead of explicit `INTEL_GPP()` tables. Each community uses a group size of 32 and four PAD_OWN registers per generated group. `glk_pinctrl_soc_data` is a NULL-terminated UID table for ACPI HID `INT3453`, selected by `intel_pinctrl_probe_by_uid()`.

## Control Flow

The driver registers at subsystem init. Probe selects one of four `intel_pinctrl_soc_data` structures by `_UID` values `"1"`, `"2"`, `"3"`, or `"4"`. The common probe maps the selected controller and calls `intel_pinctrl_add_padgroups_by_size()` because `.gpps` is NULL; generated groups then feed GPIO range creation, interrupt scanning, and pin-to-GPIO translation.

## State And Persistence

All SoC topology is static. Runtime state is allocated by the common core. Because generated pad groups use fixed 32-pad blocks, persistence behavior follows the core's generated `intel_padgroup` layout, including `padown_num` increments by `gpp_num_padown_regs`.

## Dependencies And Integration Points

The file depends on the common Intel pinctrl core, ACPI UID matching, and PM callbacks. It exposes several mux groups to consumers; northwest includes UART/I2C/PWM groups, north includes SPI/I2C/UART groups, and SCC includes SD, SDIO, UART, I2C, and eMMC groups. The audio UID only provides GPIO/pin descriptors without named mux groups.

## Risks

The functions for PWM are named `"pmw0"` through `"pmw3"` while the group arrays are `pwm*`, so consumers expecting `"pwm*"` names may not bind unless that spelling is intentional ABI. Generated group sizing must match the hardware register layout; if Gemini Lake has non-32-sized status/enable groups, interrupts and ownership would be wrong.

## Test Signals

Boot logs should show one controller per ACPI UID. Pinmux tests should request UART, I2C, SPI, SDIO, and eMMC groups and verify PADCFG0 mode changes. GPIO IRQ tests should cover boundaries at 31/32/63/64. Debugfs pin names should reflect the UID-local pin tables rather than a single merged SoC table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-geminilake.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-icelake.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-icelake.c

## Purpose

`pinctrl-icelake.c` supports Intel Ice Lake-LP and Ice Lake-N PCH GPIO/pinctrl controllers. It maps two hardware variants behind different ACPI IDs and provides rich LP mux groups for SPI, I2C, and UART functions.

## Important APIs, Types, And Functions

The file defines separate register offset families, `ICL_LP_*` and `ICL_N_*`, and community macros `ICL_LP_COMMUNITY()` and `ICL_N_COMMUNITY()`. `icllp_soc_data` includes pin groups/functions; `icln_soc_data` is mostly pin and community topology. ACPI IDs `INT3455` and `INT34C3` select LP and N data respectively. Several pad groups use `INTEL_GPIO_BASE_NOMAP` or `INTEL_GPIO_BASE_ZERO`, exercising the common core's special GPIO base handling.

## Control Flow

`module_platform_driver()` registers `icelake-pinctrl`. `intel_pinctrl_probe_by_hid()` passes the matched variant data to `intel_pinctrl_probe()`. The core copies communities, maps BARs, normalizes explicit pad groups via `intel_pinctrl_add_padgroups_by_gpps()`, registers mux/group callbacks, and creates GPIO ranges only for mapped pad groups.

## State And Persistence

Static state covers Ice Lake-LP pins 0-240 and Ice Lake-N pins 0-212. Runtime state lives in `struct intel_pinctrl`, including MMIO register pointers and suspend/resume contexts. NOMAP groups such as HVCMOS, JTAG, and SPI pads intentionally do not become GPIO lines.

## Dependencies And Integration Points

The driver integrates with ACPI, the common Intel pinctrl core, GPIO/pinctrl frameworks, and PM. LP function groups are consumed by board/device pinctrl states for SPI/I2C/UART. GPIO bases are sparse and hardware-defined; this matters for firmware resources, gpiolib line numbering, and IRQ domains.

## Risks

GPIO base special values create sharp edges: a group marked NOMAP cannot be requested through gpiolib, while `INTEL_GPIO_BASE_ZERO` forces a group to start at GPIO 0. Incorrect use would break existing firmware GPIO resources. LP per-pin SPI mode arrays must stay aligned with pin arrays. Variant mixups between `INT3455` and `INT34C3` would map different pad names and register offsets.

## Test Signals

Probe should distinguish LP and N by ACPI ID. GPIO range enumeration should skip NOMAP groups and correctly map base-zero GPP_G on Ice Lake-N. Pinmux validation should cover LP SPI0/SPI1/SPI2 mode arrays and I2C/UART groups. IRQ tests should include sparse GPIO bases and ACPI-owned pad rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-icelake.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-intel-platform.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-intel-platform.c

## Purpose

`pinctrl-intel-platform.c` is a generic firmware-described Intel PCH pinctrl/GPIO driver for ACPI HID `INTC105F`. Instead of hard-coding pin tables, it builds `struct intel_pinctrl_soc_data` from device properties and child nodes.

## Important APIs, Types, And Functions

`intel_platform_pinctrl_prepare_pins()` allocates pin names and descriptors, replacing `-` with `_` for name normalization. `intel_platform_pinctrl_prepare_group()` reads child properties `intc-gpio-group-name` and `intc-gpio-pad-count`, builds pins, and fills an `intel_padgroup`. `intel_platform_pinctrl_prepare_community()` reads register offsets from device properties, allocates one pad group per child node, and sets common community fields. `intel_platform_pinctrl_prepare_soc_data()` currently creates one community per platform device. `intel_platform_pinctrl_probe()` allocates generated SoC data and calls `intel_pinctrl_probe()`.

## Control Flow

On probe, the driver allocates an empty `intel_pinctrl_soc_data`, reads firmware properties, creates pin descriptors in child-node order, creates pad groups with `INTEL_GPIO_BASE_MATCH`, and then delegates to the shared Intel core. The core treats the generated structures the same way it treats static SoC descriptors.

## State And Persistence

All generated descriptors are device-managed allocations tied to the platform device lifetime. The generated pin table is persistent for the driver's lifetime but not global static data. Runtime GPIO, IRQ, pinmux, and PM state is still owned by `pinctrl-intel.c`.

## Dependencies And Integration Points

This file depends heavily on firmware property correctness: ownership, lock, host software ownership, interrupt status, and interrupt enable offsets all come from device properties. It also depends on child nodes for group names and pad counts. It integrates with `devm_kasprintf_strarray()`, `fwnode` child iteration, ACPI match `INTC105F`, and the common Intel core.

## Risks

Malformed firmware can fail probe or create unusable pin maps. Version 1.0 assumes only one community per device node, so multi-community firmware must be represented as multiple devices or future code changes. `devm_krealloc_array()` grows the pin descriptor array by absolute pin number; unexpected large pad counts can increase memory use. Name normalization changes hyphens to underscores, which is desirable for consistency but is still visible ABI in debug and consumer references.

## Test Signals

Tests should exercise missing properties, zero child nodes, multiple child groups, name normalization, and correct GPIO base matching. On real hardware, the generated line names and line count should match firmware. GPIO input/output and IRQ tests verify that property-provided register offsets are correct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-intel-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-intel.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-intel.c

## Purpose

`pinctrl-intel.c` is the shared runtime implementation for modern Intel GPIO/pinctrl controllers. SoC-specific files provide static or generated pin/group/community data; this file implements pinctrl, pinmux, pinconf, GPIO, IRQ, capability discovery, PWM probing, ACPI data selection, and suspend/resume behavior.

## Important APIs, Types, And Functions

Core exported APIs include `intel_pinctrl_probe()`, `intel_pinctrl_probe_by_hid()`, `intel_pinctrl_probe_by_uid()`, `intel_pinctrl_get_soc_data()`, `intel_get_community()`, `intel_gpio_add_pin_ranges()`, group/function query helpers, and `intel_pinctrl_pm_ops`. Internal helpers translate pins and GPIO offsets (`intel_gpio_to_pin()`, `intel_pin_to_gpio()`), locate pad registers (`intel_get_padcfg()`), check ownership and locks (`intel_pad_owned_by_host()`, `intel_pad_acpi_mode()`, `intel_pad_locked()`), configure muxes (`intel_pinmux_set_mux()`), set pinconf state, and dispatch GPIO IRQs.

## Control Flow

Probe allocates `struct intel_pinctrl`, copies SoC community templates, maps each community BAR, rejects absent devices whose revision reads all ones, discovers capabilities through revision and CAPLIST, computes `pad_regs` from `PADBAR`, normalizes pad groups by explicit GPP tables or fixed group size, probes optional LPSS PWM if advertised, obtains the platform IRQ, initializes PM context, registers pinctrl, registers the GPIO chip, and requests a shared interrupt.

GPIO requests enter through pinctrl/gpiolib callbacks. A GPIO request checks host ownership and pad lock state, preserves firmware GPIO settings when already in GPIO mode, or forces GPIO mode with RX enabled and TX/SCI/SMI/NMI routes disabled. Direction, value, pull bias, high impedance, and debounce operations update PADCFG registers under `raw_spinlock_t`. IRQ setup rejects ACPI-mode pads, puts pads into GPIO mode, programs RX event/inversion bits, masks/unmasks GPI_IE, clears GPI_IS, and dispatches pending enabled bits to the gpiochip IRQ domain.

## State And Persistence

Runtime state is in `struct intel_pinctrl`: device pointer, spinlock, pinctrl descriptor/device, gpiochip, SoC data pointer, copied communities with MMIO pointers, PM context, and parent IRQ. Suspend saves PADCFG0/1/2 only for kernel/userspace-owned pins or direct-IRQ pins, saves interrupt masks and host ownership registers, and masks interrupts on resume before restoring saved state. PADCFG0 restore masks out RX state because it is read-only/live input state.

## Dependencies And Integration Points

The file integrates with Linux pinctrl, pinmux, pinconf, gpiolib, irqchip, ACPI, platform resources, PM, and optional `PWM_LPSS`. SoC data comes from `pinctrl-intel.h` structures. Firmware state is respected through PAD_OWN, HOSTSW_OWN, and ACPI ownership logic. It also contains a direct-IRQ firmware workaround for systems that route GPIO input to IOxAPIC without normal GPIO IRQ ownership.

## Risks

Register programming is hardware-sensitive. Incorrect community data can make every helper operate on the wrong MMIO address. Lock and ownership checks intentionally return busy or unsupported for firmware-owned or locked pads; bypassing them would risk firmware conflicts. IRQ handling uses shared IRQ scanning across all pad groups, so status/enable offset errors can cause missed or spurious interrupts. Suspend/resume restore is selective to avoid clobbering BIOS-managed pins, but that means inactive pins intentionally are not restored.

## Test Signals

Strong signals include successful probe and gpiochip registration, correct debugfs ownership/lock/mode output, pinmux mode changes for SoC group tables, pinconf bias/debounce get/set, GPIO direction/value behavior, IRQ trigger type handling and shared IRQ dispatch, wake enable/disable calls, optional PWM registration when CAPLIST advertises it, and suspend/resume preservation of requested lines, IRQ lines, and direct-IRQ pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-intel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-intel.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-intel.h

## Purpose

`pinctrl-intel.h` defines the data contract between Intel SoC-specific pinctrl drivers and the shared Intel core. It also exposes the core probe, ACPI selection, group/function, GPIO range, community lookup, and PM symbols used by companion drivers.

## Important APIs, Types, And Functions

Key types are `struct intel_pingroup`, `struct intel_function`, `struct intel_padgroup`, `struct intel_community`, `struct intel_pinctrl_soc_data`, `struct intel_pinctrl_context`, and `struct intel_pinctrl`. Key macros are `INTEL_GPP()`, `INTEL_COMMUNITY_GPPS()`, `INTEL_COMMUNITY_SIZE()`, `PIN_GROUP()`, `PIN_GROUP_GPIO()`, and `FUNCTION()`. Special GPIO base values are `INTEL_GPIO_BASE_ZERO`, `INTEL_GPIO_BASE_NOMAP`, and `INTEL_GPIO_BASE_MATCH`. Feature bits include debounce, 1K pull-down support, GPIO hardware info, PWM, blink, EXP, and 3-bit PAD_OWN.

## Control Flow

The header itself has no control flow, but its declarations drive core behavior. SoC files instantiate `intel_pinctrl_soc_data`; probe helpers pass that data to `intel_pinctrl_probe()`. The core then interprets communities, pad groups, pin groups, and functions according to these structure fields and macros.

## State And Persistence

The header separates immutable SoC templates from runtime state. SoC templates are `const` arrays. `struct intel_pinctrl` is mutable runtime state with copied communities, MMIO pointers, gpiochip, pinctrl device, spinlock, PM context, and IRQ. `struct intel_pinctrl_context` is the saved suspend/resume container.

## Dependencies And Integration Points

The header depends on kernel pinctrl, gpio, irq, PM, spinlock, bits, and array-size definitions. It is included by modern Intel SoC drivers and by special cases such as Lynxpoint that reuse common helper APIs. It exports symbols in namespace `PINCTRL_INTEL`, requiring module users to import that namespace.

## Risks

Macro misuse can silently build wrong static tables. `PIN_GROUP()` uses compile-time selection to treat a mode argument as either a scalar or an array; passing an expression with unexpected constant-ness could choose the wrong field. `INTEL_GPP()` sizes are derived from inclusive start/end values, so off-by-one errors are easy. The meaning of special GPIO bases must be preserved because many SoC files depend on NOMAP or forced-zero behavior.

## Test Signals

Compile coverage is important because many table definitions rely on macro typing. Runtime validation comes indirectly from every SoC driver: correct group counts, function names, GPIO ranges, community lookup, PM callbacks, and namespace imports all exercise this header's contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-intel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-jasperlake.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-jasperlake.c

## Purpose

`pinctrl-jasperlake.c` supplies the Jasper Lake PCH pin and community map for the shared Intel pinctrl core. It covers 233 pins across GPP_F, SPI, GPP_B/A/S/R/H/D, vGPIO, GPP_C, HVCMOS, GPP_E, and GPP_G.

## Important APIs, Types, And Functions

The file uses `JSL_COMMUNITY()` with Jasper Lake register offsets and explicit `INTEL_GPP()` pad groups. `jsl_soc_data` contains pins and communities but no named function/group mux tables. ACPI HID `INT34C8` selects the data and the platform driver delegates to `intel_pinctrl_probe_by_hid()`.

## Control Flow

`module_platform_driver()` registers `jasperlake-pinctrl`. Probe retrieves `&jsl_soc_data` from ACPI match data and calls the common probe. The core maps four communities, normalizes explicit GPPs, skips NOMAP groups where configured, and creates GPIO and IRQ infrastructure.

## State And Persistence

Static topology includes GPIO bases such as GPP_F at 320, GPP_B at 32, GPP_A at 64, GPP_S at 96, GPP_R at 128, GPP_H at 160, GPP_D at 192, vGPIO at 224, GPP_C at 256, GPP_E at 288, and GPP_G forced to GPIO base zero. SPI and HVCMOS are NOMAP. Runtime state is held by the common core.

## Dependencies And Integration Points

The file integrates with ACPI `INT34C8`, the Intel core, PM callbacks, and gpiolib/pinctrl via common code. Hardware coverage includes eMMC, SPI flash, eSPI, SoundWire/HDA/I2S, ISH, CNV/vGPIO, display, and SD3 pads.

## Risks

Sparse and non-monotonic GPIO bases are intentional but risky for consumers and table edits. GPP_G uses `INTEL_GPIO_BASE_ZERO`, so it can overlap conceptually with pin numbers unless callers use gpiolib ranges correctly. Since no mux functions are declared, alternate-function selection must rely on firmware or other mechanisms rather than named pinmux functions from this driver.

## Test Signals

Probe on `INT34C8` should register expected sparse GPIO ranges and skip SPI/HVCMOS. GPIO line names should match the table. IRQ tests should cover multiple communities and base-zero GPP_G. Suspend/resume tests should confirm requested lines in sparse ranges restore correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-jasperlake.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-lakefield.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-lakefield.c

## Purpose

`pinctrl-lakefield.c` defines the Intel Lakefield PCH pinctrl/GPIO layout. It maps 267 pins into EAST, NORTHWEST, WEST, and SOUTHEAST communities and delegates all runtime behavior to the common Intel core.

## Important APIs, Types, And Functions

The central data object is `lkf_soc_data`, with `lkf_pins` and four `lkf_communities`. `LKF_COMMUNITY()` binds Lakefield's register offsets. Explicit `INTEL_GPP()` entries describe subgroups and GPIO bases. ACPI HID `INT34C4` selects the driver data for `intel_pinctrl_probe_by_hid()`.

## Control Flow

The platform driver registers through `module_platform_driver()`. Probe is HID-based and calls into `intel_pinctrl_probe()`. The common core maps one BAR per Lakefield community, creates GPIO ranges from the pad groups, registers pinctrl and GPIO, and handles shared IRQs and PM save/restore.

## State And Persistence

Static state defines the hardware topology only. Runtime state such as pad register pointers, requested GPIOs, IRQ enable masks, and saved PM contexts is owned by `pinctrl-intel.c`. Community boundaries map pins 0-59, 60-148, 149-237, and 238-266.

## Dependencies And Integration Points

The driver depends on ACPI `INT34C4`, platform-device probing, the common Intel pinctrl namespace, and PM callbacks. Pin coverage includes touch/display/eSPI/SPI, LPSS I2C/I3C/audio, UART/SSP/UFS/eMMC/PCIe/display sideband, and PMIC/type-C/southeast platform pins.

## Risks

Lakefield has large contiguous ranges split into multiple GPPs. Incorrect base assignment affects both GPIO numbering and IRQ domain hwirq mapping. No explicit mux function tables are provided, so named pinmux selection is not available from this source. Table comments are useful but not authoritative; numeric ranges control behavior.

## Test Signals

Hardware boot should show four mapped communities under `INT34C4`, expected line names, and GPIO ranges starting at 0, 64, 96, 128, 160, 192, 224, and 256. GPIO/IRQ tests across each community boundary and suspend/resume on requested LPSS or PMIC lines provide meaningful coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-lakefield.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-lewisburg.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-lewisburg.c

## Purpose

`pinctrl-lewisburg.c` describes Intel Lewisburg GPIO/pinctrl hardware for the common Intel core. It covers 247 pins across server PCH groups including LPC/eSPI, SATA, SMBus, GBE, fan, GSX, and platform-management signals.

## Important APIs, Types, And Functions

`LBG_COMMUNITY()` uses `INTEL_COMMUNITY_SIZE()` rather than explicit GPP tables, so the core generates pad groups with size 24 and three PAD_OWN registers per group. `lbg_soc_data` is matched by ACPI HID `INT3536` and consumed by `intel_pinctrl_probe_by_hid()`.

## Control Flow

The platform driver registers through `module_platform_driver()`. During probe, the shared core maps communities with BAR numbers 0, 1, 3, 4, and 5, then calls `intel_pinctrl_add_padgroups_by_size()` for each because `.gpps` is NULL. GPIO and IRQ handling proceed through generated groups.

## State And Persistence

This file is static data only. Runtime state and suspend/resume persistence are in the common core. Generated pad groups make GPIO bases match pin bases for each 24-pin group unless the final group is smaller.

## Dependencies And Integration Points

The driver depends on ACPI `INT3536`, Intel common pinctrl APIs, and PM. Lewisburg's server-focused pins integrate with LPC/eSPI, SATA/SSATA, SMBus, GBE, fan PWM/tach, reset/error, and clock request hardware.

## Risks

Using fixed-size generated groups requires the hardware's status, enable, lock, host ownership, and PAD_OWN register packing to match 24-pin groups. Any deviation would break GPIO lookup or IRQ dispatch. Sparse BAR numbering means resource ordering in firmware/platform data must match community `.barno`.

## Test Signals

Probe should map five communities and register GPIO lines through generated 24-pin groups. Tests should cover GPIO and IRQ operation near 24-pin boundaries, especially community transitions and final partial groups. Debugfs should expose pin names and generated GPIO ranges consistent with the table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-lewisburg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-lynxpoint.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-lynxpoint.c

## Purpose

`pinctrl-lynxpoint.c` is a legacy Intel Lynxpoint PCH GPIO/pinctrl driver. It reuses some common data structures and helper exports from `pinctrl-intel.h`, but implements its own IO-port register access, pinctrl ops, pinconf ops, gpiochip, IRQ handling, and resume behavior because Lynxpoint's register layout differs from modern PADCFG-based controllers.

## Important APIs, Types, And Functions

Static topology is `lptlp_pins`, `lptlp_gpps`, `lptlp_communities`, and `lptlp_soc_data`. Register helpers include `lp_gpio_reg()`, `lp_gpio_acpi_use()`, and `lp_gpio_ioxapic_use()`. Runtime operations are implemented by `lp_pinmux_set_mux()`, `lp_gpio_request_enable()`, `lp_gpio_disable_free()`, `lp_gpio_set_direction()`, `lp_pin_config_get()`, `lp_pin_config_set()`, GPIO get/set/direction functions, IRQ functions (`lp_gpio_irq_handler()`, `lp_irq_ack()`, `lp_irq_enable()`, `lp_irq_disable()`, `lp_irq_set_type()`), `lp_gpio_probe()`, and `lp_gpio_resume()`.

## Control Flow

The driver registers at subsystem init under name `lp_gpio` and matches ACPI IDs `INT33C7` and `INT3437`. Probe allocates `struct intel_pinctrl`, registers a pinctrl device, maps an IORESOURCE_IO region through `devm_ioport_map()`, copies the single community template, initializes the gpiochip for 95 GPIOs, optionally wires a parent IRQ with chained handling, and registers the gpiochip. IRQ dispatch scans bitmapped interrupt status/enable registers in 32-bit chunks and forwards pending bits to the gpiochip IRQ domain.

## State And Persistence

Lynxpoint has 95 GPIOs, bitmapped ownership/IRQ/status/enable registers, and per-pin CONFIG1/CONFIG2 registers. Runtime state is stored in `struct intel_pinctrl`, but no common `intel_pinctrl_pm_ops` context is used. Resume only re-enables input sensing for requested GPIOs because some hardware clears that bit across suspend.

## Dependencies And Integration Points

The file integrates with ACPI, platform IO resources, pinctrl, pinmux, pinconf, gpiolib, irqchip, and the common `intel_gpio_add_pin_ranges()`/`intel_get_community()` helpers. It uses firmware ownership bits to reject IRQ use of ACPI-reserved pins. It also handles IOxAPIC redirection constraints for specific GPIO ranges.

## Risks

This path is easy to confuse with the modern Intel core, but it does not use PADCFG register definitions or common probe/PM code. `lp_gpio_request_enable()` appears to write `(value & USE_SEL_MASK) | USE_SEL_GPIO`, preserving only mode bits and potentially dropping unrelated CONFIG1 bits when forcing GPIO mode; that behavior is existing code and should be reviewed carefully before changes. IRQ mask/unmask are empty because enable/disable control the hardware, so irqchip semantics must remain consistent with gpiolib expectations.

## Test Signals

Probe should succeed with an IO port resource and ACPI match. Debugfs should show Lynxpoint CONFIG1/CONFIG2 values and ACPI ownership. GPIO request/free should enable/disable input sensing. IRQ tests should reject ACPI-owned pins, program rising/falling/level trigger bits, and dispatch chained parent interrupts. Resume tests should confirm requested GPIO input sensing is restored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-lynxpoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-merrifield.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-merrifield.c

## Purpose

`pinctrl-merrifield.c` defines Intel Merrifield SoC pinctrl data for the Tangier-family pinctrl core, not the modern `pinctrl-intel.c` core. It maps 233 pins into functional families and exposes mux functions for SDIO, I2S, SPI, UART, and PWM.

## Important APIs, Types, And Functions

The file uses `struct tng_pinctrl`, `struct tng_family`, `TNG_FAMILY()`, `TNG_FAMILY_PROTECTED()`, `PIN_GROUP()`, and `FUNCTION()`. `mrfld_soc_data` is the main descriptor. The driver matches ACPI HID `INTC1002` and probes through `devm_tng_pinctrl_probe()`.

## Control Flow

`subsys_initcall()` registers `pinctrl-merrifield`. ACPI matching passes `&mrfld_soc_data` to the Tangier probe. The Tangier core, defined outside this work item, consumes pins, families, groups, and functions to register pinctrl/GPIO behavior. Module exit unregisters the platform driver.

## State And Persistence

This source is static topology. Families describe contiguous pin ranges; family 7 and family 12 are protected, which likely instructs the Tangier core to restrict access or preserve firmware-controlled regions. Runtime state and persistence are handled by the Tangier core.

## Dependencies And Integration Points

The driver depends on `pinctrl-tangier.h` and imports namespace `PINCTRL_TANGIER`. It also includes `pinctrl-intel.h` for shared Intel pin group/function macros. Integration points include ACPI `INTC1002`, platform driver registration, and Tangier pinctrl consumers.

## Risks

Protected family boundaries are important: moving pins between normal and protected families can expose firmware/PMIC-sensitive pins to kernel consumers. Group/function mode values are all mode 1, so any hardware function needing different per-pin mode values would not be represented. Pin names include legacy GP numbers and functional aliases; consumers may depend on exact names.

## Test Signals

Probe on Merrifield hardware should register Tangier pinctrl data, expose 233 pins, and list SDIO/I2S/SPI/UART/PWM functions. Tests should verify protected families cannot be misused according to Tangier policy and that muxing each declared function selects the expected hardware mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-merrifield.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-meteorlake.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-meteorlake.c

## Purpose

`pinctrl-meteorlake.c` describes Intel Meteor Lake PCH GPIO/pinctrl variants for the shared Intel core. It supports Meteor Lake-P and Meteor Lake-S with distinct pin tables, register offsets, communities, and ACPI IDs.

## Important APIs, Types, And Functions

The file defines `MTL_P_*` and `MTL_S_*` register offsets, community macros `MTL_P_COMMUNITY()` and `MTL_S_COMMUNITY()`, `mtlp_soc_data`, and `mtls_soc_data`. ACPI IDs `INTC105E` and `INTC1083` select Meteor Lake-P data; `INTC1082` selects Meteor Lake-S data. The platform driver delegates to `intel_pinctrl_probe_by_hid()`.

## Control Flow

`module_platform_driver()` registers `meteorlake-pinctrl`. On matching ACPI HID, the common Intel probe maps each community BAR, discovers capabilities, normalizes explicit pad groups, registers pinctrl and GPIO, and installs shared IRQ and PM callbacks. There are no file-local runtime callbacks beyond module registration.

## State And Persistence

Meteor Lake-P statically defines 289 pins across five communities; Meteor Lake-S defines 148 pins across three communities. Runtime state is held by `pinctrl-intel.c`. Sparse GPIO bases extend up to 448 on P and 224 on S, so GPIO offsets are hardware-facing and not simply pin numbers.

## Dependencies And Integration Points

The driver depends on ACPI HID selection, `PINCTRL_INTEL`, and common PM ops. Hardware integration spans CPU/platform pins, vGPIO, eSPI, SPI0, JTAG, HDA, CNV, I3C, THC, UFS, display, and management pins. The P and S variants use different HOSTSW_OWN/PADCFGLOCK offsets, making variant selection critical.

## Risks

This is a large declarative map with sparse GPIO bases; table edits can break firmware GPIO resources or interrupt routing. Variant register offsets differ, so assigning the wrong ACPI ID to the wrong data object would be severe. No mux groups/functions are declared, so consumers cannot request named alternate functions through this driver unless another mechanism configures them.

## Test Signals

Probe should select P or S by ACPI ID and expose the expected pin count. GPIO range tests should cover the high sparse bases and community boundaries. Debugfs should show correct pin names and lock/ownership state. IRQ tests should validate the `GPI_IS`/`GPI_IE` offsets for both P and S variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-meteorlake.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-meteorpoint.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-meteorpoint.c

## Purpose

`pinctrl-meteorpoint.c` provides the Intel Meteor Point-S PCH pin map for the common Intel pinctrl/GPIO driver. It covers 339 pins across GPP_D/R/J, vGPIO, eSPI/DIR_ESPI, GPP_B/C/H/S/E/K/F/I, SPI0, JTAG_CPU, and other platform groups.

## Important APIs, Types, And Functions

The key data is `mtps_soc_data`, built from `mtps_pins` and five explicit community descriptors. `MTP_COMMUNITY()` binds Meteor Point register offsets: PAD_OWN 0x0b0, PADCFGLOCK 0x110, HOSTSW_OWN 0x150, GPI_IS 0x200, and GPI_IE 0x220. ACPI HID `INTC1084` selects the data and probe uses `intel_pinctrl_probe_by_hid()`.

## Control Flow

The platform driver registers via `module_platform_driver()`. Probe is fully delegated to the common Intel core, which maps BARs, copies communities, normalizes pad groups, registers pinctrl/GPIO, requests the shared IRQ, and installs PM callbacks.

## State And Persistence

All state in this file is immutable table data. Runtime state belongs to the common driver. GPIO bases are sparse and range from 0 through 576, with each `INTEL_GPP()` describing the mapping from pin ranges to GPIO offsets.

## Dependencies And Integration Points

The file depends on ACPI `INTC1084`, platform probing, PM, and the `PINCTRL_INTEL` namespace. Hardware integration includes audio, CNV/vGPIO, THC interrupts, eSPI, SPI flash/TPM, USB overcurrent, SATA/PCIe, fuse/sort pins, JTAG, and management/reset pins.

## Risks

Meteor Point's high pin count and sparse GPIO bases make manual table maintenance risky. A wrong GPP range can misroute interrupts or break GPIO descriptor lookup. As with several newer Intel maps, no named function/group mux table is provided, so mux control is limited to generic GPIO and firmware-established pad modes unless future tables are added.

## Test Signals

Probe on `INTC1084` should expose 339 pins and GPIO ranges up to base 576. Tests should cover GPIO and IRQ operations in early, middle, and high-base groups, especially vGPIO and JTAG/GPP_I ranges. Suspend/resume should preserve requested and IRQ lines via the common PM callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-meteorpoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-moorefield.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-moorefield.c

## Purpose

`pinctrl-moorefield.c` defines Intel Moorefield SoC pinctrl topology for the Tangier-family core. It maps 251 pins into contiguous families but does not define explicit function/group mux tables in this file.

## Important APIs, Types, And Functions

The file uses `struct tng_pinctrl`, `TNG_FAMILY()`, `PINCTRL_PIN()`, and `devm_tng_pinctrl_probe()`. `mofld_soc_data` contains the pin descriptors and 15 family ranges. ACPI HID `INTC1003` carries the SoC data to the platform driver.

## Control Flow

`subsys_initcall()` registers `pinctrl-moorefield`. On ACPI match, the platform driver invokes `devm_tng_pinctrl_probe()`, which consumes `mofld_soc_data` and registers Tangier-family pinctrl behavior. Module exit unregisters the driver.

## State And Persistence

This file contains immutable pin and family tables. Runtime state, GPIO registration, mux behavior, and any suspend/resume handling are owned by the Tangier core. Family ranges cover ULPI, eMMC, SDIO, HSI, SSP, I2C, UART, GPIO south/north, camera, clock, PMIC, keyboard, and PTI areas.

## Dependencies And Integration Points

The driver depends on `pinctrl-tangier.h`, ACPI `INTC1003`, platform probing, and namespace `PINCTRL_TANGIER`. It is separate from the modern `PINCTRL_INTEL` core and does not include `pinctrl-intel.h`.

## Risks

Because no named functions are supplied, behavior depends on what the Tangier core can infer from family data or what firmware already configured. Pin names contain repeated GP labels in PTI and GPIO North ranges, so users of names must tolerate aliases that reflect hardware documentation. Family boundary errors can expose or hide broad blocks of pins.

## Test Signals

Probe should expose 251 Moorefield pins and all 15 families. Tangier-core tests should validate GPIO access and any default mux handling across each family boundary. Hardware validation should focus on eMMC/SDIO/UART/I2C and PMIC-sensitive pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-moorefield.c -->
