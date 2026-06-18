# subset-b-005060 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt6878.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt6878.h

Purpose: Defines the MT6878 SoC pin descriptor table for the newer MediaTek Paris pinctrl driver. The header is data, not executable logic: it enumerates 216 GPIO-numbered pins, each pin's external-interrupt selector, its drive-strength group (`DRV_GRP4` throughout), and the mux functions that Linux exposes through pinctrl and device-tree pin configuration. It also defines a separate `eint_pins_mt6878` table that maps selected GPIO numbers to EINT controller instances, indices, and debounce capability.

Important APIs, types, and data: The exported local symbols are `static const struct mtk_pin_desc mtk_pins_mt6878[]` and `static struct mtk_eint_pin eint_pins_mt6878[]`. Each `MTK_PIN(...)` macro comes from `pinctrl-paris.h` and expands to an `mtk_pin_desc` with `.number`, `.name`, `.eint`, `.drv_n`, and a sentinel-terminated `struct mtk_func_desc` array. `MTK_EINT_FUNCTION(...)` records the mux value and interrupt number; `NO_EINT_SUPPORT` marks pins that cannot act as EINT sources. `MTK_FUNCTION(...)` maps mux values to signal names such as touchscreen GPIOs, JTAG, SPI, I2C, antenna select, modem, audio, UFS, and debug-monitor outputs. The tail of the pin array contains GPIO-only or placeholder entries with `MTK_FUNCTION(0, NULL)`, so consumers must tolerate a missing function name for those pins.

Control flow and integration: The header is included by `pinctrl-mt6878.c`; that file passes `mtk_pins_mt6878`, `ARRAY_SIZE(mtk_pins_mt6878)`, and `eint_pins_mt6878` into `struct mtk_pin_soc mt6878_data`. Probe is driven by the `mediatek,mt6878-pinctrl` OF match entry and `mtk_paris_pinctrl_probe()`. Runtime pin operations do not branch through this header directly; the shared Paris code uses the descriptor table to enumerate pin groups/functions, validate mux requests, and resolve EINT metadata, while the `.c` file supplies register-field ranges for mode, direction, input/output, pull, drive, RSEL, SMT, IES, and the MT6878 IO base-name list.

State and persistence behavior: The arrays are compile-time static data with no mutation or persistence. Runtime state lives in the pinctrl core, EINT core, and MMIO registers selected by the companion `.c` register maps. The only stateful-looking table here is `eint_pins_mt6878`, but it is a static mapping that tells the EINT subsystem how hardware instances and debounce bits correspond to GPIO numbers.

Dependencies: Depends on `pinctrl-paris.h`, which in turn depends on `pinctrl-mtk-common-v2.h` for `struct mtk_pin_desc`, `struct mtk_pin_soc`, `struct mtk_eint_desc`, and function descriptor types. It must stay consistent with `pinctrl-mt6878.c`, MT6878 device-tree bindings, and board DTS files that request mux names and GPIO numbers.

Risks: The main risk is table drift: a wrong pin number, mux value, EINT number, or EINT instance silently routes board pins to the wrong peripheral or interrupt. The separate `eint_pins_mt6878` mapping is especially sensitive because it overrides simple one-to-one assumptions. Placeholder `NULL` function names require downstream code to handle absent names safely. Since every pin uses `DRV_GRP4`, drive-strength behavior depends on the companion register range tables being correct for all pads.

Test signals: Build coverage for `pinctrl-mt6878.c` should catch macro/type regressions. Runtime signals include successful probe of `mediatek,mt6878-pinctrl`, correct `/sys/kernel/debug/pinctrl` pin/function enumeration, GPIO direction/read/write smoke tests, EINT trigger/debounce tests for pins listed in `eint_pins_mt6878`, and board-level tests for SPI/I2C/UART/MSDC/UFS/audio/debug muxes that appear in DTS pin groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt6878.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt6893.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt6893.h

Purpose: Defines the MT6893 pin descriptor table for the Paris generation of the MediaTek pinctrl driver. It enumerates 227 GPIO pins (`GPIO0` through `GPIO226`) and their muxable signal names, EINT metadata, and drive-strength group. The table is the SoC-specific pin inventory consumed by the MT6893 driver during probe.

Important APIs, types, and data: The local export is `static const struct mtk_pin_desc mtk_pins_mt6893[]`. Each entry uses `MTK_PIN(number, name, eint, drv_n, functions...)`, `MTK_EINT_FUNCTION(eintmux, eintnum)`, and one or more `MTK_FUNCTION(muxval, name)` descriptors. Most pins use GPIO mode 0 plus alternate modes for SPI, I2S, PWM, MSDC, display, modem interrupts, clock monitor, antenna select, SCP I2C, UFS, audio, and debug-monitor functions. Some pins use `NO_EINT_SUPPORT`, and the final GPIO220-GPIO226 range has EINT entries but only `MTK_FUNCTION(0, NULL)`, acting as reserved or unnamed GPIO descriptors rather than normal named mux functions.

Control flow and integration: `pinctrl-mt6893.c` includes this header and installs `mtk_pins_mt6893` into `struct mtk_pin_soc mt6893_data` with `.npins` and `.ngrps` both set from `ARRAY_SIZE(mtk_pins_mt6893)`. The driver matches `mediatek,mt6893-pinctrl` and calls `mtk_paris_pinctrl_probe()`. The pin table feeds group/function enumeration, mux selection, and EINT lookup; the companion `.c` file supplies the hardware register layouts for mode, direction, DI/DO, SMT, IES, pull-up, pull-down, PUPD, R0/R1, drive, advanced drive, RSEL, base names, and EINT hardware parameters.

State and persistence behavior: This header contributes immutable descriptor data only. No state is allocated, cached, or persisted here. Runtime state is held by the generic pinctrl framework and by MMIO register values programmed through MT6893 register-calculation tables. Because `.ngrps` equals the pin count, the Paris core treats each pin as its own group unless additional group metadata is supplied elsewhere.

Dependencies: Depends on `pinctrl-paris.h` and the v2 MediaTek pinctrl common definitions. It is tightly coupled to the MT6893 `.c` register maps and to the `mediatek,mt6893-pinctrl.yaml` binding, whose DTS examples and allowed pin configuration properties assume these pin numbers and function names.

Risks: The risk surface is almost entirely declarative correctness. A mux-name typo can break device-tree lookup; a wrong mux value can select an unintended hardware function; an incorrect EINT mapping can produce missing or spurious interrupts. The unnamed tail entries with `NULL` function names are a compatibility risk for diagnostics or code paths that expect mode 0 to have a printable name. Table changes also need review against the many IO configuration bases in the `.c` file because pin numbers must align with register-field ranges.

Test signals: Useful checks include allmodconfig or targeted build of `pinctrl-mt6893.c`, DT schema validation for MT6893 pinctrl nodes, debugfs enumeration of all 227 pins, mux smoke tests for high-use buses such as SPI/I2C/I2S/MSDC/UFS/display, GPIO fallback tests for reserved tail pins, and EINT tests on both supported and `NO_EINT_SUPPORT` pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt6893.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8127.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8127.h

Purpose: Defines the MT8127 pin inventory for the older MediaTek pinctrl common driver. It enumerates 143 pins (`PINCTRL_PIN(0, ...)` through `PINCTRL_PIN(142, ...)`) with package pad names, chip tag `"mt8127"`, EINT metadata, and mux functions. Unlike the newer Paris headers, this table uses `struct mtk_desc_pin` and carries package-ball style pad identifiers such as `P22`, `M22`, and `AE21`.

Important APIs, types, and data: The local export is `static const struct mtk_desc_pin mtk_pins_mt8127[]`. `MTK_PIN(PINCTRL_PIN(...), pad, chip, eint, functions...)` expands through `pinctrl-mtk-common.h` into a `pinctrl_pin_desc`, `struct mtk_desc_eint`, and sentinel-terminated `struct mtk_desc_function` list. The table covers PWRAP SPI pins, audio pins, RTC/watchdog/SRCLK pins, UARTs, PCM/I2S, EINT-labelled pins, keypad rows/columns, display DPI, cameras, MSDC0/MSDC1/MSDC2, HDMI/CEC/hotplug pins, NAND-style alternate signals, debug monitor outputs, and antenna-select lines. Several late HDMI/MSDC pins deliberately use `NO_EINT_SUPPORT`.

Control flow and integration: `pinctrl-mt8127.c` includes this header and installs `mtk_pins_mt8127` into `struct mtk_pinctrl_devdata mt8127_pinctrl_data`. The platform driver matches `mediatek,mt8127-pinctrl` and uses `mtk_pctrl_common_probe()`. The `.c` file provides the behavior around this table: drive-strength groups, per-pin drive register mappings, special PUPD/R0/R1 pull settings, IES/SMT ranges, mode/direction/data offsets, EINT offsets, and GPIO mode selection. The core uses the header table to enumerate pins/functions and to map requested mux values to pin names.

State and persistence behavior: This header is immutable descriptor data. It has no dynamic state and no persistence beyond compiled kernel text/data. Hardware state is represented by register values configured through the common pinctrl driver using `mt8127_pinctrl_data`, not by this table.

Dependencies: Depends on `<linux/pinctrl/pinctrl.h>` for `PINCTRL_PIN()` and on `pinctrl-mtk-common.h` for `struct mtk_desc_pin`, `MTK_PIN`, `MTK_EINT_FUNCTION`, and `MTK_FUNCTION`. It is coupled to `pinctrl-mt8127.c`, the legacy `mediatek,mt65xx-pinctrl.yaml` binding, and any MT8127 DTS pin groups that refer to these numeric pins and function names.

Risks: The older common-driver format has more independent tables in the `.c` file, so the pin count and pin numbers here must remain aligned with drive, pull, IES, SMT, and EINT maps. Package pad labels are documentation-like but valuable for board bring-up; wrong labels can mislead debugging even if the driver still builds. Function-name drift can break DTS references, while incorrect EINT numbers on EINT-labelled pins can make GPIO interrupt users fail only at runtime.

Test signals: Build `pinctrl-mt8127.c`, validate MT8127 pinctrl device-tree nodes against the legacy binding, inspect debugfs pin/function output for all 143 pins, exercise GPIO and EINT lines including `NO_EINT_SUPPORT` pins, and run board-level checks for PWRAP, UART, PCM/I2S, keypad, display DPI, camera, MSDC, HDMI/CEC, and NAND alternate-function groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8127.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8135.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8135.h

Purpose: Defines the MT8135 pin descriptor table for the older MediaTek common pinctrl driver. It enumerates 203 pins (`0..202`) with `PINCTRL_PIN()` names, package pad identifiers, chip tag `"mt8135"`, EINT mappings, and alternate mux names. The table is broad because MT8135 exposes storage, NAND, display, camera, audio, modem/debug, keypad, I2C, PWM, and test functions through the same pinmux model.

Important APIs, types, and data: The header exports `static const struct mtk_desc_pin mtk_pins_mt8135[]`. Every entry is an `MTK_PIN()` macro containing a Linux pinctrl descriptor, a package pad string, an EINT descriptor, and a sentinel-terminated list of `MTK_FUNCTION()` values. Pins 0-9 start with MSDC0 data/cmd/clock signals, early pins also expose NAND and audio alternatives, middle ranges cover EINT, keypad, UART, SPI, camera, DPI, LCD/NAND, and debug outputs, and the tail includes I2C (`SDA*`/`SCL*`) and MSDC3 pins. Many entries expose explicit `"EINTnn"` mux names in addition to `MTK_EINT_FUNCTION(...)`, reflecting the legacy hardware mux representation.

Control flow and integration: `pinctrl-mt8135.c` includes this header and places `mtk_pins_mt8135` in `struct mtk_pinctrl_devdata mt8135_pinctrl_data`. Probe uses the `mediatek,mt8135-pinctrl` match entry and `mtk_pctrl_common_probe()`. The companion `.c` file provides drive group definitions, per-pin drive register mappings, special pull handling through a local `struct mtk_spec_pull_set`, fixed IES/SMT offsets, register stride/port alignment, and EINT register offsets. This header supplies the pin/function namespace that those register operations act on.

State and persistence behavior: The table is static read-only configuration. It does not allocate or update runtime state. Pin mux, pull, drive, input-enable, and Schmitt-trigger values persist in hardware registers after the common driver programs them; this header only tells the driver which logical pin and function names are valid.

Dependencies: Depends on `<linux/pinctrl/pinctrl.h>` and `pinctrl-mtk-common.h`. It must stay aligned with `pinctrl-mt8135.c`, the legacy MediaTek pinctrl binding, and the MT8135 DTS file that instantiates `mediatek,mt8135-pinctrl`.

Risks: The table is dense and manually structured, making off-by-one pin numbers, swapped package balls, incorrect EINT muxes, or wrong alternate-function values plausible regressions. Because MT8135 has custom pull handling in the `.c` file, storage and keypad pins that need special PUPD/R0/R1 behavior require cross-checking between this header and `spec_pupd`. Function names containing brackets or numbered debug/test outputs must remain exact for diagnostic and DTS compatibility.

Test signals: Build coverage for the MT8135 pinctrl driver, DT validation and boot of MT8135 pinctrl nodes, debugfs enumeration of all 203 pins, EINT tests across the exposed EINT mux ranges, storage tests for MSDC0/MSDC3, display DPI tests, I2C/PWM/keypad/UART/SPI mux smoke tests, and pull/drive validation on pins covered by the special pull table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8135.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8167.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8167.h

Purpose: Defines the MT8167 pin descriptor table for the legacy MediaTek common pinctrl driver. It enumerates 125 pins (`0..124`) using `struct mtk_desc_pin`, with pinctrl names, a mostly `NULL` package-pad field, chip tag `"mt8167"`, EINT metadata, and mux-function lists. The table covers the logical pin/function namespace used by MT8167 device-tree pin groups.

Important APIs, types, and data: The local export is `static const struct mtk_desc_pin mtk_pins_mt8167[]`. Entries use the older `MTK_PIN(PINCTRL_PIN(...), pad, chip, eint, functions...)` form from `pinctrl-mtk-common.h`. The pin set starts with EINT pins, then covers keypad, UART, SPI, I2S/PCM, PWM, I2C, camera/display-related pins, CMDAT pins, storage pins, CEC/hotplug/HDMI clock/data pins, and NAND-style alternate names such as `NALE`, `NWEB`, `NLD*`, and `WATCHDOG`. In this file every pin has an `MTK_EINT_FUNCTION(0, pin_number)` style mapping; there are no `NO_EINT_SUPPORT` markers in the source.

Control flow and integration: `pinctrl-mt8167.c` includes this header and passes `mtk_pins_mt8167` into `struct mtk_pinctrl_devdata mt8167_pinctrl_data`. The platform driver matches `mediatek,mt8167-pinctrl` and probes through `mtk_pctrl_common_probe()`. The `.c` file supplies the operational maps: drive groups, per-pin drive-register fields, special PUPD/R0/R1 settings, IES/SMT ranges, register offsets, EINT offsets, and GPIO mode. The header provides the descriptor array consumed by the generic common-driver enumeration and mux lookup code.

State and persistence behavior: No mutable state lives in the header. It is compile-time descriptor data. Persistent effects of pin configuration are hardware register values written by the common driver through the data tables in `pinctrl-mt8167.c`.

Dependencies: Depends on `<linux/pinctrl/pinctrl.h>` and `pinctrl-mtk-common.h`. It must remain consistent with MT8167 register tables in `pinctrl-mt8167.c`, the `mediatek,mt65xx-pinctrl.yaml` compatible list, and MT8167 DTS pinctrl nodes.

Risks: Because the package-pad field is `NULL`, board-level debugging relies heavily on the logical pin names and DTS references. A wrong mux value or signal string can break peripheral bring-up without any compile-time failure. Since every pin has an EINT descriptor, interrupt-capability assumptions should be verified against actual silicon and the EINT hardware map. The table also needs careful alignment with special pull and drive maps for storage and keypad-style pins.

Test signals: Targeted build of `pinctrl-mt8167.c`, DT schema validation for MT8167 pinctrl nodes, boot-time probe of `mediatek,mt8167-pinctrl`, debugfs inspection for all 125 pins, GPIO/EINT tests across representative pins, storage tests for MSDC0-related pins, HDMI/CEC hotplug checks, and mux smoke tests for I2C/SPI/UART/I2S/PWM/keypad functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8167.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8173.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8173.h

Purpose: Defines the MT8173 pin descriptor table for the legacy MediaTek common pinctrl driver. It enumerates 135 pins (`0..134`) with `PINCTRL_PIN()` names, a `NULL` package-pad field, chip tag `"mt8173"`, EINT metadata, and mux-function alternatives. The file provides the per-pin namespace used by MT8173 pinctrl probe, DTS pin groups, GPIO users, and mux selection.

Important APIs, types, and data: The local export is `static const struct mtk_desc_pin mtk_pins_mt8173[]`. Entries expand through `MTK_PIN`, `MTK_EINT_FUNCTION`, and `MTK_FUNCTION` from `pinctrl-mtk-common.h`. The table starts with EINT-labelled pins, includes SPI, UART, I2S/PCM, HDMI/DP-style signals, MSDC0/MSDC1/MSDC2/MSDC3, camera/display signals, keypad rows/columns, I2C pins, `LCM_RST`, and debug-monitor alternatives. Each entry has an EINT function mapping, generally `MTK_EINT_FUNCTION(0, gpio_number)`, and one or more mux values including GPIO mode 0.

Control flow and integration: `pinctrl-mt8173.c` includes this header, passes `mtk_pins_mt8173` and its size into `struct mtk_pinctrl_devdata mt8173_pinctrl_data`, and uses a small `mt8173_pinctrl_probe()` wrapper around `mtk_pctrl_init()`. The OF match compatible is `mediatek,mt8173-pinctrl`. The companion `.c` file provides MT8173-specific special-pull mappings, IES/SMT tables, drive group tables, per-pin drive fields, register offsets, and EINT offsets. This header supplies the logical descriptors consumed by those shared operations.

State and persistence behavior: The header is static descriptor data only. It does not own locks, memory, or mutable state. Runtime pinctrl state is maintained by the common driver and the kernel pinctrl core, while configured electrical state persists in hardware registers.

Dependencies: Depends on `<linux/pinctrl/pinctrl.h>` and `pinctrl-mtk-common.h`. It integrates with `pinctrl-mt8173.c`, the legacy MediaTek pinctrl binding, and MT8173 DTS nodes under `arch/arm64/boot/dts/mediatek/mt8173.dtsi`.

Risks: The high-value risks are declarative mismatches: incorrect mux values, names that diverge from DTS expectations, EINT numbers that do not match hardware, or pin numbers that no longer align with drive/pull/IES/SMT tables. Storage pins have special pull and drive handling in the `.c` file, so MSDC-related descriptors should be reviewed with those tables. Because package pads are absent, wrong logical names are harder to diagnose during board bring-up.

Test signals: Build the MT8173 pinctrl driver, validate and boot MT8173 DTS pinctrl nodes, inspect debugfs for all 135 pins and functions, exercise GPIO and EINT behavior, test MSDC0-3 storage pins including special pulls, and run mux smoke tests for I2C, SPI, UART, I2S/PCM, display, keypad, and camera-related functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8173.h -->
