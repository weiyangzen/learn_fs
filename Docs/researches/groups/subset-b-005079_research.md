# subset-b-005079 Research

Grouped research for the listed Qualcomm pinctrl files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-mdm9607.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-mdm9607.c

## Purpose
Defines the Qualcomm MDM9607 TLMM pin controller variant. It is a SoC description file for the shared `pinctrl-msm` core: it enumerates 80 GPIO-capable TLMM pins plus SDC/QDSD pseudo-groups, names the alternate functions exposed to device tree pinctrl states, maps each GPIO group to TLMM register offsets and mux selectors, and registers a platform driver for `qcom,mdm9607-tlmm`.

## Important APIs, Types, And Data
The file depends on `struct msm_pinctrl_soc_data`, `struct msm_pingroup`, and `MSM_PIN_FUNCTION` / `MSM_GPIO_PIN_FUNCTION` from `pinctrl-msm.h`. `PINGROUP()` creates normal GPIO groups with 0x1000-byte register spacing, mux at bit 2, pull bits at 0, drive bits at 6, output enable at 9, I/O value bits 0/1, and two-bit interrupt detection. `SDC_PINGROUP()` creates non-GPIO storage-card groups with only pull and drive fields valid and interrupt/mux fields set unusable. The function enum and `mdm9607_functions[]` cover BLSP UART/SPI/I2C/UIM, QDSS trace/CTI, audio, UIM, Ethernet reset/IRQ/MDIO, sensors, power indication, analog-test, and modem/navigation timing functions.

## Control Flow
Initialization is data-driven. `arch_initcall(mdm9607_pinctrl_init)` registers `mdm9607_pinctrl_driver`; OF matching on `qcom,mdm9607-tlmm` calls `mdm9607_pinctrl_probe()`, which delegates to `msm_pinctrl_probe(pdev, &mdm9607_pinctrl)`. From there the shared core maps MMIO, registers pinctrl functions, creates the gpiochip, and wires the interrupt domain. Runtime mux, GPIO, pinconf, and IRQ operations all flow through the common core using this file's table offsets and bit positions.

## State And Persistence
This file owns static const topology only. Persistent runtime state lives in `struct msm_pinctrl` in the shared core: MMIO base, enabled IRQ bitmaps, disabled-for-mux state, GPIO validity, and pinctrl state selection. Hardware state is persisted in TLMM registers programmed by the core. There is no file-local mutable state and no storage beyond hardware registers and kernel-managed driver objects.

## Dependencies And Integration Points
Integrates with Linux platform-driver and OF matching, the generic pinctrl and pinmux frameworks, gpiolib, and the MSM TLMM core. Device tree consumers reference function names and group names such as `gpioN`, `sdc1_*`, and `qdsd_*`. The `.ngpios = 80` boundary means only GPIO groups 0-79 are exposed through gpiolib; later SDC/QDSD groups are pinconf-only style groups for storage pads.

## Risks
The largest risk is table drift: a wrong register offset, mux selector ordering, or group/function name silently programs the wrong TLMM bits. Because `PINGROUP()` always declares ten function slots, placeholder `_` entries still consume mux indices and must match hardware encoding. SDC/QDSD groups deliberately have invalid IRQ and mux fields; if they were ever exposed as GPIOs, the shared core would read nonsensical bit positions. There is no wakeirq map, so suspend wake behavior relies on the TLMM summary path rather than a PDC/MPM parent mapping.

## Test Signals
Useful signals are boot probe success for `qcom,mdm9607-tlmm`, debugfs pinctrl/gpio state showing expected mux and pull/drive values, GPIO direction/value tests for lines 0-79, interrupt tests for edge and level GPIO IRQs, and board-level validation of BLSP, QDSS, UIM, Ethernet, SDC, and QDSD pin states declared in device tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-mdm9607.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-mdm9615.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-mdm9615.c

## Purpose
Provides the TLMM pin controller description for Qualcomm MDM9615. It exposes 88 GPIO groups to the shared `pinctrl-msm` driver and describes a relatively small set of alternate functions: GSBI buses, SDC2, EBI2 LCD, primary/secondary audio, codec MCLK, and `ps_hold`.

## Important APIs, Types, And Data
The file builds `mdm9615_pins[]`, `mdm9615_functions[]`, `mdm9615_groups[]`, and `mdm9615_pinctrl`. `PINGROUP()` is the key macro: each GPIO gets control, I/O, interrupt config, interrupt status, and a separate interrupt target register at `0x400 + 0x4 * id`. It marks `intr_ack_high = 1`, uses `intr_raw_status_bit = 3`, and only one interrupt detection bit, so the common core may emulate both-edge interrupts in software. `MSM_GPIO_PIN_FUNCTION(gpio)` marks the GPIO function for the generic pinmux core. The `ps_hold_groups[]` entry places `ps_hold` on gpio83.

## Control Flow
`arch_initcall(mdm9615_pinctrl_init)` registers the platform driver early. The driver matches `qcom,mdm9615-pinctrl`; probe calls `msm_pinctrl_probe()` with the MDM9615 data. The shared core then registers pin groups/functions, installs pinconf and pinmux callbacks, adds a gpiochip with 88 GPIOs, and configures the summary interrupt handler. Presence of the `ps_hold` function lets `msm_pinctrl_setup_pm_reset()` install restart and poweroff handling through the PS_HOLD register path.

## State And Persistence
The file is static data only. Runtime state is maintained by `pinctrl-msm.c` in MMIO register values and in `struct msm_pinctrl` bitmaps for enabled IRQs, software dual-edge IRQs, mux-disabled IRQs, and first-GPIO glitch avoidance. The `ps_hold` integration creates system-off behavior through core-managed global hooks, but the SoC file itself does not mutate state.

## Dependencies And Integration Points
Depends on the generic MSM pinctrl core, Linux OF platform matching, pinctrl/pinmux APIs, and gpiolib. Device tree states select groups like `gpio4`/`gpio5` for `gsbi2_i2c`, gpio83 for `ps_hold`, or GPIO groups 25-30 for `sdc2`. Older register layout details are captured here through separate interrupt target registers and high-ack interrupt status semantics.

## Risks
The main behavior risk is the one-bit interrupt detection configuration: both-edge GPIO IRQs require the common software polarity-flip loop, making edge loss possible if a line toggles too quickly. `ps_hold` has system-wide reset/poweroff impact, so a wrong group/function association can break restart or poweroff. Many groups are `NA` only; clients expecting undocumented alternate functions will fail until the table is expanded. Interrupt target and ack-high fields must remain aligned with this older TLMM generation.

## Test Signals
Probe logs and `/sys/kernel/debug/pinctrl` should show 88 GPIO groups and the expected function names. Practical tests include GSBI I2C/UART/SPI pin states, audio pins, GPIO IRQ edge/level tests with attention to both-edge behavior, and restart/poweroff validation through `ps_hold`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-mdm9615.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-milos-lpass-lpi.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-milos-lpass-lpi.c

## Purpose
Defines the Milos LPASS LPI pin controller variant, separate from the main TLMM controller. It describes 23 low-power audio pins used for SoundWire, I2S, DMIC, Slimbus, QCA SWR, WSA SWR, external MCLK, and GPIO mode, then binds them to the generic Qualcomm LPASS-LPI pinctrl driver.

## Important APIs, Types, And Data
This file uses `pinctrl-lpass-lpi.h`, not `pinctrl-msm.h`. `enum lpass_lpi_functions` defines LPI mux IDs, `milos_lpi_pins[]` defines gpio0-gpio22, group arrays map functions to pin names, `milos_groups[]` uses `LPI_PINGROUP()` to assign each pin a mux list and optional SoundWire slew offset, and `milos_functions[]` uses `LPI_FUNCTION()`. `milos_lpi_data` is a `struct lpi_pinctrl_variant_data` consumed directly by `lpi_pinctrl_probe()`.

## Control Flow
The `module_platform_driver(lpi_pinctrl_driver)` macro registers a platform driver named `qcom-milos-lpass-lpi-pinctrl`. OF match `qcom,milos-lpass-lpi-pinctrl` supplies `.data = &milos_lpi_data`; probe and remove are delegated to the shared LPI implementation. Runtime control of mux, bias, drive, GPIO value, and slew handling is implemented by the LPI core using the variant data in this file.

## State And Persistence
The file has no mutable state. Hardware state persists in LPASS LPI TLMM registers programmed by the LPI core. The only durable topology decisions here are the pin count, function-to-group membership, per-pin mux choices, and which pins have `LPI_NO_SLEW` versus concrete slew offsets. The comment notes that gpio15-gpio18 do not really exist, but dummy groups are still present to keep numbering stable.

## Dependencies And Integration Points
Integrates with the platform bus, OF matching, gpiolib-facing LPI core, and audio subsystem device-tree pinctrl consumers. The relevant register layout and config masks are abstracted by `pinctrl-lpass-lpi.h`. This file is intended to coexist with `pinctrl-milos.c`: main application TLMM pins are handled there, while always-on/low-power audio pins are handled here.

## Risks
The main risks are numbering and mux-table mistakes. LPASS audio links are sensitive to exact pin/function pairing, and dummy nonexistent GPIOs 15-18 can confuse consumers if a device tree requests them. Incorrect slew offsets can break SoundWire signal quality or produce hard-to-debug audio transport failures. Because this uses a different core from TLMM, fixes in `pinctrl-msm.c` do not affect this path.

## Test Signals
Probe should bind against `qcom,milos-lpass-lpi-pinctrl` and expose 23 pins. Board tests should exercise I2S, SoundWire RX/TX/WSA/QCA, DMIC, Slimbus, external MCLK, GPIO fallback mode, and suspend/resume audio use cases. Debugfs pinctrl output should confirm expected function/group ownership and avoid use of nonexistent gpio15-gpio18.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-milos-lpass-lpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-milos.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-milos.c

## Purpose
Defines the main TLMM pin controller for Qualcomm Milos. It describes a modern 168-GPIO controller plus UFS reset and SDC2 groups, large QUP/CCI/UIM/QDSS/audio/navigation/WCN/PCIe function coverage, PDC wake interrupt mappings, and eGPIO ownership handoff support.

## Important APIs, Types, And Data
The file uses `pinctrl-msm.h` and the shared MSM TLMM core. `PINGROUP()` creates 12-function GPIO groups with 0x1000 register spacing, two-bit interrupt detection, I2C strong-pull support at bit 13, eGPIO present/enable bits at 11/12, wakeup present/enable bits, and KPSS target value 3 at target bit 8. `SDC_QDSD_PINGROUP()` describes storage-card pads, while `UFS_RESET()` describes a non-GPIO UFS reset group with an output bit. `milos_pdc_map[]` maps many GPIOs to PDC wake IRQs. `milos_tlmm` sets `.ngpios = 168`, attaches the wake map, and sets `.egpio_func = 11`.

## Control Flow
`arch_initcall(milos_tlmm_init)` registers the `milos-tlmm` platform driver. OF match `qcom,milos-tlmm` calls `milos_tlmm_probe()`, which delegates to `msm_pinctrl_probe()`. The common core registers pinctrl/pinmux/pinconf functions, creates a gpiochip for GPIOs 0-167, installs the TLMM summary IRQ handler, and, if a `wakeup-parent` domain exists, maps listed GPIOs to PDC parent IRQs. eGPIO mux selections are interpreted by the shared core as a request to release TLMM ownership rather than simply writing a normal mux field.

## State And Persistence
This file is static topology. Runtime state includes TLMM registers, IRQ routing, PDC parent IRQ mappings, and the shared core's bitmaps. eGPIO behavior persists in hardware ownership bits: selecting the eGPIO mux clears TLMM ownership when the present bit says the pin supports it, while selecting normal functions reclaims ownership. I2C strong pull-up is encoded through a wider pull mask in the common pinconf conversion.

## Dependencies And Integration Points
Integrates with device tree via `qcom,milos-tlmm`, generic pinctrl state consumers, gpiolib, irqdomain wake-parent plumbing, PDC wake IRQ handling, and the shared MSM core. It complements `pinctrl-milos-lpass-lpi.c`, which owns low-power audio pins. Device-tree consumers depend on group names `gpio0` through `gpio166`, `ufs_reset`, and `sdc2_*`, and on function names such as `qup*_se*`, `cci_i2c_*`, `uim*`, `qdss_*`, `pcie*_clk_req_n`, `egpio`, and `sdc*`.

## Risks
Milos has a broad blast radius because the table controls many shared SoC interfaces. eGPIO support is especially sensitive: a wrong `.egpio_func`, mux slot, or present/enable bit can leave pins owned by the wrong block. Wake IRQ map mistakes can break suspend wake or route interrupts to the wrong PDC line. Dummy groups preserve index alignment, so removing or reordering them would corrupt pin numbering. UFS reset and SDC groups have invalid normal IRQ fields and must stay outside `.ngpios`.

## Test Signals
Good signals include successful probe, correct 168-line gpiochip registration, PDC wake testing for mapped GPIOs, eGPIO handoff tests on supported high-numbered pins, QUP/CCI/UIM/WCN/PCIe/QDSS pinmux validation, UFS reset behavior, SDC2 card operation, I2C strong pull-up pinconf checks, and debugfs confirmation that dummy/non-GPIO groups are not exposed as GPIO lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-milos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm.c

## Purpose
Implements the shared Qualcomm MSM/TLMM pinctrl, pinmux, pinconf, GPIO, IRQ, suspend/resume, and PS_HOLD reset/poweroff logic used by many SoC-specific table files. SoC files provide `struct msm_pinctrl_soc_data`; this core turns those tables into Linux pinctrl functions, a gpiochip, and an IRQ domain backed by TLMM registers.

## Important APIs, Types, And Functions
`struct msm_pinctrl` is the runtime device state: device handles, pinctrl descriptor, gpiochip, parent IRQ, SCM-routing flag, raw spinlock, IRQ state bitmaps, SoC data pointer, MMIO bases, and physical base addresses. `msm_pinctrl_probe()` is the exported entry point for SoC drivers. Pinctrl ops include group count/name/pins and generic DT mapping. Pinmux ops include strict muxing, GPIO request validation, mux programming, eGPIO handling, glitch avoidance when first returning an output pin to GPIO, and IRQ masking while muxed away. Pinconf ops translate generic bias, drive, open-drain, input/output enable, and output level settings into TLMM bitfields.

GPIO functions implement direction, get, set, and debugfs display. IRQ functions implement mask/unmask, enable/disable, ack/eoi, type programming, software dual-edge handling, wake setup, resource locking, affinity forwarding for wake parents, chained summary interrupt dispatch, and wake-parent child-to-parent mapping. PM helpers force sleep/default pinctrl states. PS_HOLD helpers register restart and poweroff when a SoC exposes a `ps_hold` function.

## Control Flow
Probe allocates `msm_pinctrl`, maps one or more MMIO tiles, detects the special IPQ8064 SCM interrupt-target path, registers restart/poweroff if `ps_hold` exists, gets the parent IRQ, registers the pinctrl device, adds all generic pinfunctions, and initializes the gpiochip/IRQ domain. Runtime pinctrl requests from device tree flow through generic maps into `msm_pinmux_set_mux()` and `msm_config_group_set()`. GPIO API calls go through gpiolib callbacks. GPIO IRQs arrive on the TLMM summary interrupt and `msm_gpio_irq_handler()` scans enabled GPIOs for status bits, except wake-parent lines can be handled through a PDC/MPM parent domain.

## State And Persistence
Driver state is in `struct msm_pinctrl` and hardware registers. The raw spinlock protects register read-modify-write sequences. Bitmaps track enabled IRQs, software dual-edge lines, wake-parent-skipped lines, IRQs disabled because mux moved away from GPIO, and pins that have already had first-GPIO output glitch avoidance. GPIO validity can come from SoC `reserved_gpios` or ACPI `gpios`. Suspend/resume does not save TLMM registers directly; it asks pinctrl to select sleep/default states.

## Dependencies And Integration Points
Depends on Linux pinctrl, pinmux, pinconf, gpiolib, irqchip/irqdomain, OF/platform resources, Qualcomm SCM for secure interrupt target writes on IPQ8064, Qualcomm IRQ wake-parent helpers, sys-off registration, and PM core. SoC-specific files must provide accurate group register offsets, bit positions, function arrays, GPIO counts, optional tile names, reserved GPIOs, wakeirq maps, and eGPIO metadata.

## Risks
This is high-impact shared code. Incorrect bit arithmetic can affect every Qualcomm TLMM user. IRQ handling is subtle: raw status handling differs for level versus edge interrupts, some hardware needs software both-edge emulation, and wake-parent lines bypass local TLMM handling. Muxing away from GPIO while an IRQ is configured requires disable/ack/reenable coordination to avoid spurious interrupts. `PIN_CONFIG_INPUT_ENABLE` intentionally preserves historical output-disable behavior despite generic pinconf documentation. PS_HOLD poweroff uses global `pm_power_off`, so multi-controller systems must not register conflicting handlers casually.

## Test Signals
Core test signals include probe/remove through representative SoC drivers, pinctrl state application from device tree, GPIO direction/value tests, pinconf readback for pull/drive/open-drain/output-level, edge/level/both-edge IRQ tests, mux-away-while-IRQ-active tests, wake-parent suspend/resume wake tests, debugfs state inspection, sleep/default state transitions, and restart/poweroff behavior on SoCs with `ps_hold`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm.h

## Purpose
Defines the shared data contract between Qualcomm TLMM SoC description files and `pinctrl-msm.c`. It provides function declaration macros, pin group/register metadata structures, wake IRQ mapping types, SoC-level configuration, PM ops export, and the `msm_pinctrl_probe()` API.

## Important APIs, Types, And Data
Function macros such as `MSM_PIN_FUNCTION()`, `MSM_GPIO_PIN_FUNCTION()`, `APQ_PIN_FUNCTION()`, `IPQ_PIN_FUNCTION()`, and `QCA_PIN_FUNCTION()` build `struct pinfunction` entries from enum naming conventions and `<function>_groups` arrays. `struct msm_pingroup` embeds `struct pingroup`, lists mux function IDs, and describes register offsets plus bit positions for mux, pull, drive, I2C pull, open drain, eGPIO ownership, output enable, input/output values, interrupt enable/status/target/wakeup/raw/polarity/detection, and interrupt ack semantics. `struct msm_gpio_wakeirq_map` maps a GPIO to a wake-controller IRQ. `struct msm_pinctrl_soc_data` packages pins, functions, groups, GPIO count, pull behavior, tiles, reserved GPIOs, wake maps, dual-edge wake errata, GPIO function index, and eGPIO function index.

## Control Flow
There is no runtime control flow in the header. Its declarations shape how SoC files compile their static tables and how `pinctrl-msm.c` interprets them during probe and runtime operations. `msm_pinctrl_probe()` is the handoff point used by each TLMM platform driver's probe function. `msm_pinctrl_dev_pm_ops` lets SoC platform drivers attach the common sleep/default pinctrl PM behavior.

## State And Persistence
The header defines metadata, not state. Persistence emerges when these fields are instantiated in SoC files and consumed by the core to program TLMM registers. The bitfield layout in `struct msm_pingroup` constrains valid values; many fields are five-bit bit positions and must represent hardware bit indices correctly.

## Dependencies And Integration Points
Includes Linux PM/types and pinctrl definitions, forward-declares platform and pin descriptor types, and is included by Qualcomm TLMM variant drivers. It is the compatibility boundary for adding new SoCs: any new hardware capability needs a field here and corresponding support in the shared core.

## Risks
Because this header is a cross-driver ABI inside the kernel tree, semantic changes can break many SoC tables. Bitfield widths can truncate invalid large bit positions. The fallback rule for `intr_target_reg` means zero has special meaning, so SoCs with a real target register at offset zero would need careful handling. `gpio_func` and `egpio_func` are indices into each group's mux list, so mismatches between enum order, function arrays, and group mux arrays lead to wrong hardware programming.

## Test Signals
Build coverage across Qualcomm pinctrl drivers is the first signal. Runtime signals come from representative SoCs using optional features: separate interrupt target registers, wakeirq maps, no-keeper pulls, reserved GPIO masks, multi-tile mappings, and eGPIO. Static review should verify group arrays, enum values, and function macros remain aligned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8226.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8226.c

## Purpose
Describes the Qualcomm MSM8226 TLMM pin controller. It exposes 117 GPIOs plus SDC1/SDC2 storage groups, declares a focused function set for BLSP, camera clocks, CCI I2C, audio PCM, GP clocks, SDC3, and WLAN, and provides an MPM wake IRQ map for selected GPIOs.

## Important APIs, Types, And Data
`PINGROUP()` creates eight-slot GPIO mux groups using the older compact TLMM layout at `0x1000 + 0x10 * id`, two-bit interrupt detection, target bit 5, KPSS target value 4, and standard pull/drive/OE/value bits. `SDC_PINGROUP()` defines storage pad groups with only pull and drive valid. `msm8226_functions[]` is marked by a TODO that not all possible hardware functions are represented. `msm8226_mpm_map[]` maps wake-capable GPIOs to MPM interrupt numbers. `msm8226_pinctrl` sets `.ngpios = NUM_GPIO_PINGROUPS` and attaches the wake map.

## Control Flow
The `msm8226-pinctrl` platform driver is registered from `arch_initcall`. OF match `qcom,msm8226-pinctrl` calls `msm8226_pinctrl_probe()`, which delegates to `msm_pinctrl_probe()`. The common core registers the pinctrl device, adds the declared pinfunctions, exposes GPIOs 0-116, and uses the MPM wake map if a `wakeup-parent` is supplied by firmware.

## State And Persistence
The file contains no mutable state. It defines static pin/function/group topology and wake mapping. Hardware register state, IRQ masks, software dual-edge state, and mux-disable bookkeeping live in `pinctrl-msm.c`. The SDC groups are beyond `.ngpios`, preventing normal gpiolib access.

## Dependencies And Integration Points
Integrates with the shared MSM TLMM core, OF platform matching, gpiolib, pinctrl consumers, and MPM wake-parent irqdomain support. Device trees depend on group names `gpio0` through `gpio116`, `sdc1_*`, `sdc2_*`, and functions such as `blsp_uart*`, `blsp_spi*`, `blsp_i2c*`, `audio_pcm`, `cam_mclk*`, `cci_i2c0`, `sdc3`, and `wlan`.

## Risks
The explicit TODO means the mux table may be incomplete relative to hardware, so unsupported alternate functions may require future additions. Large ranges of groups are placeholders with `NA`, and incorrect assumptions by board files can cause failed pinctrl state selection. Wake map mistakes break suspend wake. SDC groups have invalid IRQ/mux fields and must not be counted as GPIOs. A wrong function order inside `PINGROUP()` changes the hardware mux selector written by the core.

## Test Signals
Test signals include probe success, 117 GPIO lines exposed, BLSP and camera/CCI pinctrl states applying correctly, WLAN/SDC3 mux validation, GPIO IRQ edge/level testing, MPM wake testing for mapped GPIOs, and storage-card pull/drive validation for SDC1/SDC2 groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8226.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8660.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8660.c

## Purpose
Provides the TLMM pin controller table for Qualcomm MSM8660. It covers 173 GPIO groups and additional SDC3/SDC4 pad groups, with functions for display, DSUB, GPS, GP clocks, GSBI buses, HDMI, I2S/MI2S/PCM, PS_HOLD, SD controllers, TSIF, USB FS, VFE, voltage-sense alarm, and EBI2.

## Important APIs, Types, And Data
`PINGROUP()` describes older TLMM GPIO registers at `0x1000 + 0x10 * id`, with separate interrupt target registers at `0x400 + 0x4 * id`, high-ack interrupt status, one-bit interrupt detection, and KPSS target value 4. That one-bit detection means both-edge interrupts rely on common software emulation. `SDC_PINGROUP()` describes SDC3/SDC4 drive/pull groups. `ps_hold_groups[]` maps PS_HOLD to gpio92, enabling common reset/poweroff registration. EBI2 and EBI2 chip-select group arrays cover many high-numbered pins and are called out separately in the function list.

## Control Flow
`arch_initcall(msm8660_pinctrl_init)` registers the platform driver. Matching `qcom,msm8660-pinctrl` invokes `msm8660_pinctrl_probe()`, which calls `msm_pinctrl_probe()`. The shared core maps resources, registers pinctrl and gpiochip state, and scans the functions for `ps_hold` to install restart/poweroff handling. Runtime mux and pinconf operations are entirely table-driven by this file's offsets, function lists, and bit definitions.

## State And Persistence
All file data is static. Runtime state resides in the shared MSM core and TLMM hardware registers. Because `.ngpios = 173`, GPIO lines stop before the SDC3/SDC4 pseudo-groups. PS_HOLD affects persistent platform behavior by registering system-off callbacks, but that is driven by the common core after seeing the function name.

## Dependencies And Integration Points
Depends on `pinctrl-msm.h`, Linux OF/platform driver infrastructure, generic pinctrl consumers, gpiolib, and IRQ handling in `pinctrl-msm.c`. Device trees rely on broad group names for GSBI, LCDC/DSUB, HDMI, SD, TSIF, USB, VFE, EBI2, and PS_HOLD. The separate interrupt target register layout is an important integration detail with older TLMM hardware.

## Risks
MSM8660 uses one-bit interrupt detection, so fast both-edge GPIO IRQs can be lossy under software emulation. The EBI2 and display functions span large pin ranges; table mistakes can break memory/display buses. Several SPI chip-select group arrays are empty, which may surprise clients expecting those named functions to have selectable pins. `ps_hold` misconfiguration can break restart/poweroff. SDC pull values include `-1` for some clock pull fields, which relies on the shared core never applying unsupported configs blindly to those pseudo-groups.

## Test Signals
Signals include probe and gpiochip registration, debugfs showing 173 GPIO groups plus SDC pseudo-groups, GSBI/I2C/SPI/UART pinmux tests, LCDC/HDMI/display pin states, EBI2 bus validation, GPIO IRQ tests emphasizing both-edge behavior, SDC3/SDC4 pull/drive checks, and restart/poweroff tests through PS_HOLD.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8660.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8909.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8909.c

## Purpose
Defines the Qualcomm MSM8909 TLMM variant. It exposes 113 GPIOs and SDC/QDSD storage groups, declares a wide set of BLSP, QDSS, camera, audio, UIM, WCSS, analog-test, power/modem/navigation, and miscellaneous functions, and maps wake-capable GPIOs to MPM interrupts.

## Important APIs, Types, And Data
`PINGROUP()` uses modern 0x1000-per-GPIO register spacing, ten mux slots, standard pull/drive/OE/value bits, KPSS target bit 5/value 4, and two-bit interrupt detection. `SDC_QDSD_PINGROUP()` provides storage pad groups with only pull/drive fields. `msm8909_functions[]` is built from `MSM_PIN_FUNCTION()` and `MSM_GPIO_PIN_FUNCTION(gpio)`. `msm8909_mpm_map[]` maps selected GPIOs to MPM wake IRQs. `msm8909_pinctrl` binds pins/functions/groups with `.ngpios = 113` so SDC/QDSD groups remain outside gpiolib.

## Control Flow
The platform driver registers at `arch_initcall`. OF match `qcom,msm8909-tlmm` calls `msm8909_pinctrl_probe()`, which delegates to `msm_pinctrl_probe()`. The shared core registers the pinctrl device and gpiochip, installs the TLMM IRQ handler, and uses the wake map when a wake-parent domain is present. Runtime behavior is completely table-driven by group mux arrays and register offsets in this file.

## State And Persistence
There is no local mutable state. Persistent hardware state is TLMM register configuration for mux, pull, drive, GPIO direction/value, and interrupts. The common core owns IRQ bookkeeping and wake-parent skip state. The wake map statically determines which GPIOs may be translated to MPM wake IRQs.

## Dependencies And Integration Points
Integrates with `pinctrl-msm.c`, OF platform matching, gpiolib, generic pinctrl clients, TLMM interrupt handling, and MPM wake-parent irqdomain support. Consumers reference groups `gpio0` through `gpio112`, `sdc1_*`, `sdc2_*`, and `qdsd_*`; functions include BLSP instances, WCSS BT/FM/WLAN, QDSS trace/CTI, CCI/camera, CDC/MI2S/DMIC, UIM, SSBI, and power/modem/navigation indicators.

## Risks
MSM8909 has many overlapping mux choices, so incorrect function ordering in a `PINGROUP()` entry can silently select the wrong hardware function. Wake map errors affect suspend wake. Some groups contain duplicate or unusual entries, such as repeated `gpio24` in `ebi2_lcd_groups`, which may be intentional hardware aliasing but deserves caution during edits. SDC/QDSD groups have invalid mux/IRQ fields and rely on `.ngpios` excluding them. Board files requesting unsupported placeholder `_` functions will fail.

## Test Signals
Test by probing `qcom,msm8909-tlmm`, checking 113 GPIO lines, applying BLSP/CCI/WCSS/audio/UIM/QDSS pinctrl states, verifying GPIO direction/value and IRQ edge/level operation, validating MPM wake from mapped GPIOs, and confirming SDC1/SDC2/QDSD pull-drive settings on real storage interfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8909.c -->
