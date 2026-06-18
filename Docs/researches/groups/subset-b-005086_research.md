# Research: subset-b-005086

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8450.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8450.c

## Purpose
This file is the Qualcomm SM8450 TLMM pin controller description. It does not implement the generic pinctrl algorithms itself; instead it supplies SM8450-specific pin, mux-function, pingroup, wake IRQ, eGPIO, UFS reset, and SDC/QDSD register metadata to the shared Qualcomm `pinctrl-msm` driver. The platform driver binds to `qcom,sm8450-tlmm` and registers early through `arch_initcall()` so board pin states are available during early platform bring-up.

## Important APIs, Types, And Functions
The primary exported-to-core data object is `static const struct msm_pinctrl_soc_data sm8450_tlmm`. It references `sm8450_pins`, `sm8450_functions`, `sm8450_groups`, and `sm8450_pdc_map`, sets `ngpios = 211`, and declares `egpio_func = 9`. `PINGROUP()` builds normal GPIO-backed `struct msm_pingroup` entries with a 0x1000 register stride, mux at bit 2, pull at bit 0, drive at bit 6, OE at bit 9, eGPIO presence/enable at bits 11/12, and PDC interrupt fields. `SDC_QDSD_PINGROUP()` describes special SD-card pins without GPIO mux or interrupt capability. `UFS_RESET()` describes the UFS reset pin with output control but no mux or IRQ. `sm8450_tlmm_probe()` delegates to `msm_pinctrl_probe(pdev, &sm8450_tlmm)`.

## Control Flow
Driver registration installs a platform driver named `sm8450-tlmm`. Device-tree matching on `qcom,sm8450-tlmm` calls `sm8450_tlmm_probe()`, which hands the static SoC tables to the shared `msm_pinctrl_probe()` path. From that point, normal pinctrl, pinmux, pinconf, GPIO, and interrupt operations are driven by the common driver using this file's offsets and bit positions. Each GPIO group selects among `msm_mux_gpio` plus nine alternate mux slots; most unused slots are filled with the placeholder `msm_mux__`.

## State And Persistence
The file itself has no mutable runtime state. All arrays are static const except compound-literal function lists embedded in group initializers. Runtime state, locking, IRQ domain setup, GPIO chip state, and register writes are owned by `pinctrl-msm.c`. Hardware state persists in TLMM registers until reset, suspend restore, or later pinctrl changes by consumers. The PDC wake mapping is static metadata translating selected TLMM GPIO numbers to PDC wake interrupt numbers.

## Dependencies And Integration Points
It depends on Linux platform-driver/module/OF APIs and the Qualcomm `pinctrl-msm.h` data contract. Integration points are device-tree pinctrl nodes using the `qcom,sm8450-tlmm` compatible, subsystem consumers naming function/group pairs in pin states, gpiolib users for GPIO 0-210, IRQ consumers routed through TLMM/PDC, and storage controllers using the special UFS reset and SDC2 groups. The function catalogue covers camera clocks and CCI, QUP serial engines, QSPI, UIM, audio I2S/MI2S, display vsync, PCIe clock request, USB PHY, qlink/coexistence, debug/QDSS, DDR/test, and eGPIO pads.

## Risks
The largest risk is table accuracy. A wrong group-to-function slot silently programs the wrong mux value. A wrong register offset or bit assignment can corrupt unrelated TLMM pads because normal GPIO register blocks are stride-derived. `ngpios = 211` intentionally excludes the non-GPIO UFS/SDC groups at array indices 210-213; changing that boundary would expose special pads as normal GPIOs. The wake IRQ map must match PDC hardware, or wake-capable GPIOs may fail suspend/resume testing. eGPIO support depends on the mux slot index matching `egpio_func = 9`.

## Test Signals
Useful signals are probe success for `qcom,sm8450-tlmm`, expected registration of 211 GPIOs, pinctrl state application for representative QUP, camera, audio, UIM, QSPI, PCIe, and display functions, GPIO input/output and interrupt tests across several banks, wake-from-suspend tests for mapped PDC GPIOs, UFS reset toggling, SDC2 pad configuration, and debugfs pinmux/pinconf dumps showing mux, pull, drive, and eGPIO fields at expected register offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8450.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8550-lpass-lpi.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8550-lpass-lpi.c

## Purpose
This file describes the SM8550 LPASS LPI GPIO pin controller, a small audio-subsystem pin controller separate from main TLMM. It binds to `qcom,sm8550-lpass-lpi-pinctrl` and supplies LPASS pin/function/group tables to the shared `pinctrl-lpass-lpi` implementation.

## Important APIs, Types, And Functions
`enum lpass_lpi_functions` defines mux IDs for DMIC, I2S, SoundWire, Slimbus, external MCLK, GPIO, and placeholder functions. `sm8550_lpi_pins` declares 23 pins, `gpio0` through `gpio22`. Per-function group arrays map each audio function to legal pin groups. `sm8550_groups` contains 23 `LPI_PINGROUP()` descriptors; each records the pin number, a SoundWire slew-rate bit offset or `LPI_NO_SLEW`, and up to four alternate functions after GPIO. `sm8550_functions` uses `LPI_FUNCTION()` to expose 39 functions to pinctrl. `sm8550_lpi_data` packages those tables as `struct lpi_pinctrl_variant_data`.

## Control Flow
The module uses `module_platform_driver()`. When OF matching finds `qcom,sm8550-lpass-lpi-pinctrl`, the shared `lpi_pinctrl_probe()` receives `sm8550_lpi_data` through `.data`. The shared driver maps TLMM and, for this variant, a separate slew-rate resource because no `LPI_FLAG_SLEW_RATE_SAME_REG` flag is set. It then registers pinctrl groups, pinmux functions, pinconf handlers, and a gpiochip. Runtime mux changes select the function's index within each group's `funcs` list and write the LPASS GPIO configuration register.

## State And Persistence
This source has only static descriptor state. Runtime mutable state is in `struct lpi_pinctrl` in the shared implementation, including MMIO bases, optional clocks, a mutex, the gpiochip, and an `ever_gpio` bitmap used to avoid output glitches when first muxing a line back to GPIO. Register state is hardware-resident and persists until reset or reconfiguration.

## Dependencies And Integration Points
It depends on `pinctrl-lpass-lpi.h`, the common LPASS LPI pinctrl implementation, platform/OF matching, gpiolib, and optional LPASS clocks/resources consumed by the common probe path. It integrates with audio drivers through pinctrl states for DMIC clocks/data, I2S0-I2S4, SoundWire TX/RX, WSA and WSA2 SoundWire, Slimbus, and five external MCLK1 routes.

## Risks
The SM8550 table uses a separate slew register layout with per-pin offsets such as 0, 2, 4, 8, 10, 12, 16, 18, 20, and 22 for selected SoundWire-capable pins. Incorrect offsets affect slew programming rather than muxing, so failures may appear as signal-integrity issues. Function lists are positional; a wrong order changes mux values written by the shared driver. The file has no wake IRQ map and no main TLMM GPIO semantics, so consumers must use the LPASS compatible and pin names.

## Test Signals
Expected signals include successful probe with 23 GPIOs, pinctrl group creation for all 23 pins, valid muxing of I2S, DMIC, Slimbus, SoundWire, and ext MCLK routes, GPIO direction/value behavior through the common LPASS gpiochip, successful use of the second MMIO resource for slew programming, and debugfs output showing the selected function index, drive strength, and pull state for representative pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8550-lpass-lpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8550.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8550.c

## Purpose
This file is the Qualcomm SM8550 main TLMM pin controller descriptor. It defines the SoC's 214 pin descriptors, 210 normal GPIO pingroups plus UFS reset and SDC2 special groups, mux-function catalogues, PDC wake mapping, and a platform driver for `qcom,sm8550-tlmm`.

## Important APIs, Types, And Functions
The key object is `sm8550_tlmm`, a `struct msm_pinctrl_soc_data` consumed by `msm_pinctrl_probe()`. It sets `ngpios = 211`, points to `sm8550_pins`, `sm8550_functions`, `sm8550_groups`, and `sm8550_pdc_map`, and sets `egpio_func = 9`. `PINGROUP()` uses a 0x1000 GPIO register stride and exposes ten mux choices, with GPIO first. Relative to SM8450, this macro adds `i2c_pull_bit = 13`, allowing the common driver to handle the I2C pull field. `SDC_QDSD_PINGROUP()` and `UFS_RESET()` define nonstandard groups at indices 211-213 and 210 respectively.

## Control Flow
`sm8550_tlmm_init()` registers the platform driver at `arch_initcall()` time. OF matching on `qcom,sm8550-tlmm` invokes `sm8550_tlmm_probe()`, which delegates all runtime setup to the shared MSM pinctrl driver. Thereafter the common driver serves pinctrl and GPIO requests by indexing `sm8550_groups`; each `PINGROUP()` entry provides the function list, register offsets, mux/pull/drive/OE bits, interrupt bits, and eGPIO metadata for that GPIO.

## State And Persistence
There is no file-local mutable state. Static tables encode the hardware contract. Runtime GPIO state, IRQ masks, suspend handling, and register synchronization live in the shared `pinctrl-msm` core. Hardware configuration persists in TLMM registers. The PDC map statically links 93 GPIO lines to wake IRQ numbers for low-power wake routing.

## Dependencies And Integration Points
The descriptor depends on `pinctrl-msm.h` and Linux OF/platform module APIs. It integrates with device-tree pin states for camera CCI/MCLK, i2chub and QUP serial engines, I2S audio, QSPI/SDC4 alternates, UIM, display vsync, PCIe clock request, USB, qlink, coex UART, debug/QDSS, DDR test, and storage reset/pad groups. GPIO consumers see lines 0-210, while UFS and SDC2 groups remain special pinctrl groups.

## Risks
The SM8550 function list is large and highly positional. Adding or renaming enum values without keeping every `msm_mux_*` use and function table aligned will break mux values. PDC map errors break wake interrupts but may not show in normal runtime GPIO tests. The `i2c_pull_bit` field is SoC-specific; omitting it would produce subtly wrong I2C electrical configuration. The eGPIO mux index must remain aligned with slot 9 for groups that expose eGPIO. UFS reset uses offset `0xde000` with `io_reg = offset + 0x4`, so a mismatch would affect storage reset behavior.

## Test Signals
Test evidence should include successful probe and registration of 211 GPIOs, pinctrl apply tests for QUP/i2chub, camera CCI, audio I2S, UIM, QSPI, SDC4, USB, display, and qlink functions, GPIO IRQ and wake tests for mapped PDC entries, I2C pull configuration checks on CCI/QUP groups, UFS reset and SDC2 pad tests, and debugfs inspection of mux slot and eGPIO fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8550.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8650-lpass-lpi.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8650-lpass-lpi.c

## Purpose
This file describes the SM8650 LPASS LPI GPIO pin controller for low-power audio pins. It is a variant table for the shared LPASS LPI pinctrl core and binds to `qcom,sm8650-lpass-lpi-pinctrl`.

## Important APIs, Types, And Functions
`enum lpass_lpi_functions` extends the SM8550 LPASS set with `qca_swr_clk` and `qca_swr_data`. `sm8650_lpi_pins` defines 23 pins, and function group arrays define legal placements for DMIC, I2S, SoundWire TX/RX, WSA SoundWire, QCA SoundWire, Slimbus, ext MCLK1, and GPIO. `sm8650_groups` has 23 `LPI_PINGROUP()` entries; most SoundWire-capable pins use slew offset 11 because this variant stores slew control in the same per-pin configuration register. `sm8650_functions` exposes 41 functions. `sm8650_lpi_data` sets `.flags = LPI_FLAG_SLEW_RATE_SAME_REG`.

## Control Flow
The platform driver is registered with `module_platform_driver()`. OF match data points the common `lpi_pinctrl_probe()` to `sm8650_lpi_data`. Because `LPI_FLAG_SLEW_RATE_SAME_REG` is set, the shared probe does not require a second slew MMIO resource; slew programming writes the per-pin TLMM config register instead. Probe then registers generic pinctrl groups, pinmux, pinconf, and a gpiochip for 23 LPASS pins.

## State And Persistence
This file contains only static SoC data. Runtime state is maintained by the common LPASS driver: MMIO base, clocks named `core` and `audio` when available, mutex-protected register updates, pinctrl descriptor, gpiochip, and the first-GPIO-use glitch-avoidance bitmap. Hardware register contents persist until reset or reconfiguration.

## Dependencies And Integration Points
It integrates with `pinctrl-lpass-lpi.c` through `struct lpi_pinctrl_variant_data`. Audio consumers use these groups for I2S0-I2S4, DMIC1-DMIC4, SoundWire TX/RX, WSA/WSA2 SoundWire, QCA SoundWire on GPIO19/GPIO20, Slimbus on GPIO19/GPIO20, and external MCLK1 routes on GPIO5, GPIO9, GPIO13, GPIO14, and GPIO22. It uses platform/OF matching and gpiolib through the shared driver.

## Risks
The most important SM8650-specific risk is the same-register slew flag. If a board binding or register layout expects a separate slew resource, slew writes would target the wrong place; conversely, without the flag probe would fail or program the wrong register bank. Function ordering remains mux-value-sensitive. GPIO19 and GPIO20 carry both Slimbus and QCA SoundWire functions, so consumer pin states must choose the intended bus explicitly.

## Test Signals
Useful signals include successful probe with only the TLMM MMIO resource, registration of 23 GPIOs, correct muxing of QCA SoundWire on GPIO19/GPIO20, continued Slimbus support on the same pins, slew-rate pinconf writes affecting the per-pin config register, DMIC/I2S/WSA SoundWire route tests, and GPIO get/set/direction checks via the shared LPASS gpiochip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8650-lpass-lpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8650.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8650.c

## Purpose
This file is the Qualcomm SM8650 main TLMM pin controller descriptor. It provides static SoC metadata for 214 pins, 211 GPIO-visible lines, special UFS/SDC2 groups, mux functions, eGPIO support, interrupt bit layout, wake IRQ mapping, and the platform driver for `qcom,sm8650-tlmm`.

## Important APIs, Types, And Functions
`sm8650_tlmm` is the `struct msm_pinctrl_soc_data` passed to `msm_pinctrl_probe()`. It uses `sm8650_pins`, `sm8650_functions`, `sm8650_groups`, and `sm8650_pdc_map`, sets `ngpios = 211`, and uses `egpio_func = 10`. The `PINGROUP()` macro supports eleven mux entries per GPIO. It includes `i2c_pull_bit = 13`, eGPIO fields, interrupt wakeup presence/enable bits at 6 and 7, and an interrupt target bit at 8 rather than the older target bit 5 layout. `UFS_RESET(pg_name, ctl, io)` separates the control and I/O offsets, using `0xde004` and `0xdf000` for the SM8650 UFS reset group.

## Control Flow
The driver registers early with `arch_initcall()`. Matching `qcom,sm8650-tlmm` calls `sm8650_tlmm_probe()`, which delegates initialization to the shared Qualcomm MSM pinctrl core. At runtime, pinctrl selection indexes the SoC-specific function arrays and groups to compute mux values and register offsets. GPIO/IRQ operations similarly use per-group bit metadata and the 93-entry wake IRQ map for PDC integration.

## State And Persistence
All SoC-specific state here is static. Runtime state is held by the shared pinctrl core. TLMM register settings persist in hardware, including mux, pull, drive, output value, interrupt configuration, wake enable, and eGPIO state. The wake IRQ map is fixed metadata and is not modified at runtime.

## Dependencies And Integration Points
The file integrates with `pinctrl-msm`, platform/OF matching, gpiolib, IRQ/PDC wake handling, and device-tree pinctrl consumers. Its function set includes updated SM8650 routes such as GNSS ADC pins, `do_not` reserved mux slots, qlink little/big naming, camera AON MCLK2/MCLK4, i2chub, QUP1/QUP2 serial engines, QSPI/SDC4, audio I2S, UIM, USB, display vsync, CCI, QDSS, and eGPIO groups 165-209.

## Risks
SM8650 changes interrupt field layout and eGPIO mux slot compared with SM8450/SM8550; carrying older values forward would misroute interrupts or eGPIO muxing. The `do_not` mux entries should not be treated as normal consumer-facing functions without hardware validation. UFS reset uses non-contiguous control and I/O offsets, so generic assumptions of `io = ctl + 4` are not valid here. Wake IRQ map errors are suspend/resume failures rather than normal probe failures.

## Test Signals
Test signals include probe on `qcom,sm8650-tlmm`, 211 registered GPIOs, pinctrl state application for camera, CCI, QUP, i2chub, I2S, QSPI/SDC4, UIM, USB, qlink, and GNSS ADC routes, GPIO IRQ tests that validate the target bit 8 layout, wake-from-suspend coverage for mapped PDC lines, eGPIO mux tests using slot 10, and UFS reset/SDC2 pad validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8650.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8750.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8750.c

## Purpose
This file is the Qualcomm SM8750 main TLMM pin controller descriptor. It extends the later SM8x50 TLMM pattern to 219 pin descriptors, 216 GPIO-visible lines, extra eGPIO-only pads, SM8750-specific mux functions, PDC wake mappings, UFS reset, and SDC2 special groups. It binds to `qcom,sm8750-tlmm`.

## Important APIs, Types, And Functions
`sm8750_tlmm` supplies the shared MSM pinctrl driver with `sm8750_pins`, `sm8750_functions`, `sm8750_groups`, `sm8750_pdc_map`, `ngpios = 216`, and `egpio_func = 11`. `PINGROUP()` exposes twelve mux choices per GPIO and explicitly marks the final mux argument as the eGPIO mode slot. Like SM8650, it has interrupt wakeup present/enable bits at 6/7 and target bit 8. `UFS_RESET(pg_name, ctl, io)` uses SM8750 offsets `0xe2004` and `0xe3000`. `SDC_QDSD_PINGROUP()` defines SDC2 clock, command, and data pad control at `0xdb000`.

## Control Flow
`sm8750_tlmm_init()` registers the platform driver at `arch_initcall()` time. OF matching on `qcom,sm8750-tlmm` invokes `sm8750_tlmm_probe()`, which calls `msm_pinctrl_probe(pdev, &sm8750_tlmm)`. Runtime pinctrl, pinmux, pinconf, GPIO, and IRQ paths are all handled by the shared MSM implementation using the static tables from this file. The group table includes GPIO0-GPIO214 plus UFS and SDC2 groups, while `ngpios = 216` exposes GPIO0-GPIO215 to gpiolib.

## State And Persistence
The descriptor is static and immutable. Mutable state is in the common Qualcomm pinctrl core and in TLMM hardware registers. Register programming persists until reset, low-power restore, or a later pinctrl/gpio/irq operation. The PDC map statically maps 93 GPIO lines to wake IRQs.

## Dependencies And Integration Points
The file depends on `pinctrl-msm.h`, Linux platform/OF APIs, and the Qualcomm TLMM binding. It integrates with SM8750 board device trees and peripheral drivers for camera MCLK/CCI, i2chub/QUP serial engines, I2S audio, UIM, QSPI/SDC4, display MDP vsync/eSync, PCIe clock request, USB, qlink, WCN switch signals, GNSS ADC, test/debug functions, UFS reset, and SDC2 pads. It also has many eGPIO-capable groups from GPIO105 onward and GPIO165-GPIO215.

## Risks
This file increases the mux slot count and eGPIO index to 11; older assumptions from SM8650 would select the wrong function. `ngpios = 216` must remain consistent with the group table and special-group boundary so UFS/SDC pads are not exposed as normal GPIOs. SM8750 removes or renames some older routes and adds WCN, MDP eSync, MDP vsync5, and TSENSE PWM4 functions, making cross-SoC copy/paste risky. Wake IRQ numbers and UFS/SDC offsets are hardware-specific and are likely to fail only on targeted suspend or storage tests if wrong.

## Test Signals
Expected signals include successful platform probe, 216 GPIOs registered, working pinctrl states for camera, CCI, i2chub/QUP, I2S, UIM, QSPI/SDC4, USB, display vsync/eSync, qlink, WCN, and GNSS ADC functions, GPIO IRQ tests using the newer interrupt layout, wake-from-suspend tests for the PDC map, eGPIO tests on the final mux slot, UFS reset toggling at the SM8750 offsets, and SDC2 pad configuration at `0xdb000`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8750.c -->
