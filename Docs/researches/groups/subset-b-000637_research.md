# Research: subset-b-000637

Grouped source research for subset B work item `subset-b-000637`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6ul-pinfunc.h -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6ul-pinfunc.h

## Purpose
This header is the Devicetree pin-function catalog for the NXP/Freescale i.MX6UL IOMUX controller. It exposes `MX6UL_PAD_*__*` C preprocessor macros that expand to the five-cell `PIN_FUNC_ID` tuple used inside board DTS `fsl,pins` properties, followed by a separate pad configuration cell supplied by the board file. The header is included by `imx6ul.dtsi` and indirectly by i.MX6UL board DTS files, giving those DTS files symbolic names for mux registers, pad configuration registers, input select registers, mux modes, and input daisy values.

The file contains 943 pin-function macros across 124 physical pad names. It covers boot mode pins, SNVS tamper pins, JTAG, GPIO1, UART, ENET, LCD, NAND, SD, and CSI pad banks. The largest pad families are LCD, ENET, UART, NAND, CSI, GPIO, SD, JTAG, SNVS, and BOOT. Function coverage includes EIM, CSI, USDHC, LCDIF, ENET, GPIO, SRC, UART, I2C, ECSPI, SAI, PWM, GPT, SDMA, USB, watchdog, and clock output routes.

## Important APIs, Types, and Functions
The public API is the macro namespace, not callable C code. Each macro has the form `MX6UL_PAD_<pad>__<signal>` and expands as:

```text
<mux_reg conf_reg input_reg mux_mode input_val>
```

Board DTS entries use it as `<PIN_FUNC_ID CONFIG>`, so one pin consumes six `u32` cells in `fsl,pins`. The first five cells come from this header, and the last cell is the pad control value from the board DTS. This contract is documented by `Documentation/devicetree/bindings/pinctrl/fsl,imx-pinctrl.txt` and the i.MX35/i.MX5x/i.MX6 pinctrl YAML, which lists `fsl,imx6ul-iomuxc` as a compatible.

Important macro semantics:
- `mux_reg` and `conf_reg` are offsets within the i.MX6UL IOMUXC register window.
- `input_reg` is the select-input/daisy register offset, or `0x0000` when no daisy register is needed.
- `mux_mode` is the ALT mode value written to the mux register; this file uses modes 0 through 8.
- `input_val` is the value written to the select-input register when `input_reg` is nonzero.
- GPIO mappings are consistently exposed as alternate functions such as `GPIO1_IOxx`, `GPIO2_IOxx`, through `GPIO5_IOxx`.

The header has 317 macros with nonzero input select registers and 626 macros with no select-input register. Input-select-bearing functions include I2C, UART RX/RTS/DTE routes, ENET reference/MDIO/RGMII-adjacent routes, CSI data routes, SDHC card-detect/write-protect/data routes, SAI, ECSPI, SDMA, GPT, and USB over-current/ID paths. These nonzero input registers are high-risk because the macro does not just select a mux mode; it also programs the SoC daisy chain.

## Control Flow
There is no runtime control flow in the header itself. The control flow is:
1. The C preprocessor expands a board DTS `fsl,pins` entry such as `MX6UL_PAD_UART1_RX_DATA__UART1_DCE_RX 0x1b0b1` into six integer cells.
2. `dtc` compiles those integers into the DTB under an i.MX6UL pinctrl group node.
3. During boot, the `fsl,imx6ul-iomuxc` platform device matches `drivers/pinctrl/freescale/pinctrl-imx6ul.c`, which uses the generic `pinctrl-imx.c` parser.
4. `imx_pinctrl_parse_groups()` validates that each `fsl,pins` group size is a multiple of `FSL_PIN_SIZE` (24 bytes, six `u32`s).
5. `imx_pinctrl_parse_pin_mmio()` reads `mux_reg`, `conf_reg`, `input_reg`, `mux_mode`, `input_val`, and `config`, derives a pin id from the register offset, stores mux/config/input metadata, and moves the common `SION` bit from config into the mux mode.
6. When a client selects a pinctrl state, `imx_pmx_set_one_pin_mmio()` writes the mux register, writes the input-select register when present, and the pinconf path writes pad configuration.

Thus an edit to any numeric cell in this header changes eventual MMIO writes at boot or when device pinctrl states are selected.

## State and Persistence Behavior
The header stores no mutable runtime state and has no persistence behavior by itself. Its persistent effect is ABI-like source stability: DTS files store macro names and pad config constants in source, and compiled DTBs store the resulting integer tuples. The Linux pinctrl driver then materializes state in IOMUXC registers, select-input registers, and pad control registers during boot and device state changes.

Because DTBs can be shipped independently of the kernel source, macro values must remain consistent with the i.MX6UL reference manual and the driver parser. Changing a macro's tuple changes the ABI visible to board DTS users and can silently alter boot-time hardware routing even if the source still compiles.

## Dependencies and Integration Points
Direct integration points:
- Included by `arch/arm/boot/dts/nxp/imx/imx6ul.dtsi`.
- Reused by `imx6ull-pinfunc.h`, which includes this file and overrides a small set of shared UART5-related macros before adding i.MX6ULL-only routes.
- Consumed by many i.MX6UL/i.MX6ULL board DTS and DTSI files through `fsl,pins` pinctrl groups.
- Interpreted by `drivers/pinctrl/freescale/pinctrl-imx.c` and matched through `drivers/pinctrl/freescale/pinctrl-imx6ul.c`.
- Validated structurally by `Documentation/devicetree/bindings/pinctrl/fsl,imx35-pinctrl.yaml` and the common `fsl,imx-pinctrl.txt` binding.

The header sits at the boundary between SoC datasheet register assignments and board-level hardware descriptions. It integrates with peripheral drivers only indirectly: UART, I2C, SDHC, ENET, LCDIF, NAND, CSI, SPI, SAI, PWM, and USB drivers depend on board pinctrl states using the correct symbolic route for their pins.

## Risks
The main risk is numeric tuple drift. Wrong `mux_reg` or `conf_reg` offsets can write the wrong IOMUXC register; wrong `mux_mode` can route a pad to the wrong peripheral; wrong `input_reg` or `input_val` can break input daisy chains while output direction still appears configured; wrong SNVS/boot/JTAG mappings can affect early boot, debug, wake, or security-sensitive pads.

Other risks include:
- Reusing an i.MX6ULL-specific route on pure i.MX6UL hardware or vice versa.
- Confusing DCE/DTE UART variants, where TX/RX/CTS/RTS directions intentionally share mux modes but differ in input select behavior.
- Treating `0x0000` input registers as meaningful daisy registers; the driver treats zero as no regular input select for these non-SNVS i.MX6UL entries.
- Incorrect board config cells for voltage, pull, speed, drive strength, open-drain, or SION. The header does not protect against electrically invalid pad settings.
- Macro rename/removal breaking DTS source builds even when the underlying tuple could still be valid.

## Test Signals
Useful validation signals include:
- Build i.MX6UL and i.MX6ULL DTBs that include this header with `make ARCH=arm dtbs`.
- Run `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/fsl,imx35-pinctrl.yaml` for boards using `fsl,imx6ul-iomuxc` or `fsl,imx6ull-iomuxc-snvs`.
- Use `dtc` warnings and schema errors to catch malformed `fsl,pins` cell counts.
- Boot-test representative boards and inspect pinctrl debugfs entries, UART/I2C/SDHC/ENET/LCD/NAND probe logs, GPIO line behavior, and input routes such as card-detect, write-protect, RX, CTS/RTS, MDIO, and USB over-current.
- For macro edits, compare generated DTB integer tuples before and after the change and cross-check affected offsets against the i.MX6UL reference manual.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6ul-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6ull-pinfunc-snvs.h -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6ull-pinfunc-snvs.h

## Purpose
This header is the i.MX6ULL SNVS-domain pin-function catalog. It defines the symbolic `MX6ULL_PAD_*__GPIO5_IO*` macros for the SNVS IOMUXC instance used by boot mode and tamper pads. It is included by `imx6ull.dtsi` alongside `imx6ull-pinfunc.h` so i.MX6ULL board DTS files can configure the low-power/SNVS pin controller at `fsl,imx6ull-iomuxc-snvs`.

The file is intentionally small: 12 macros over 12 pads. It covers `BOOT_MODE0`, `BOOT_MODE1`, and `SNVS_TAMPER0` through `SNVS_TAMPER9`, all exposed as GPIO5 lines.

## Important APIs, Types, and Functions
The public API is the macro namespace:

```text
MX6ULL_PAD_BOOT_MODE0__GPIO5_IO10
MX6ULL_PAD_BOOT_MODE1__GPIO5_IO11
MX6ULL_PAD_SNVS_TAMPER<n>__GPIO5_IO0<n>
```

Each macro expands to the standard five-cell i.MX pin-function tuple:

```text
<mux_reg conf_reg input_reg mux_mode input_val>
```

Board DTS `fsl,pins` entries append the sixth `CONFIG` cell. All macros use `mux_mode` `0x5`, `input_reg` `0x0000`, and `input_val` `0x0`, because these entries route SNVS pads to GPIO and do not require daisy-chain input select programming. Register offsets start at zero for `BOOT_MODE0` and increase in four-byte steps for both mux and configuration registers within the SNVS IOMUXC register window.

This header uses an i.MX6ULL-specific macro prefix rather than the base `MX6UL_PAD_*` names because the SNVS IOMUXC has its own register offsets. Although the pad names overlap conceptually with the base i.MX6UL header, these tuples are for a different controller node and should not be mixed with main IOMUXC groups.

## Control Flow
The header has no executable control flow. Runtime behavior follows the standard i.MX pinctrl path:
1. `imx6ull.dtsi` includes the header and declares the SNVS pinctrl node with compatible `fsl,imx6ull-iomuxc-snvs`.
2. Board DTS files place these macros in SNVS pinctrl group `fsl,pins` properties with a pad control value.
3. `dtc` emits six cells per pin in the DTB.
4. `drivers/pinctrl/freescale/pinctrl-imx6ul.c` matches `fsl,imx6ull-iomuxc-snvs` to `imx6ull_snvs_pinctrl_info`.
5. The generic `pinctrl-imx.c` parser reads the five macro cells plus config. The SNVS SoC info sets `ZERO_OFFSET_VALID`, so `mux_reg = 0x0000` for `BOOT_MODE0` is a real register offset rather than the generic "no mux register" sentinel.
6. Pinctrl state selection writes the SNVS mux and pad configuration registers. No input-select register is written because all tuples have zero `input_reg`.

## State and Persistence Behavior
The file stores no state. Its persistent effect is that compiled DTBs encode SNVS pad MMIO offsets and GPIO mux selections. At runtime, the pinctrl driver writes those values into SNVS IOMUXC registers, affecting GPIO5 boot/tamper pad behavior and low-power-domain pad configuration.

Because `ZERO_OFFSET_VALID` is required for this header's first macro, the header and the matching driver data are tightly coupled. If the compatible were matched to a generic non-SNVS i.MX6UL pinctrl data set, `mux_reg = 0` could be misinterpreted and the first pad would not be configured correctly.

## Dependencies and Integration Points
Direct integration points:
- Included by `arch/arm/boot/dts/nxp/imx/imx6ull.dtsi`.
- Used under the `iomuxc_snvs: pinctrl@2290000` node, compatible `fsl,imx6ull-iomuxc-snvs`.
- Parsed by the generic i.MX pinctrl driver through `drivers/pinctrl/freescale/pinctrl-imx6ul.c`.
- Described by `Documentation/devicetree/bindings/pinctrl/fsl,imx35-pinctrl.yaml`, which includes `fsl,imx6ull-iomuxc-snvs`.

Integration with other kernel subsystems is through GPIO and wake/security-oriented board wiring. Board files may use these pads for wake inputs, tamper-related GPIOs, boot strapping observation, USB detect lines, buttons, or low-power control signals.

## Risks
The highest-risk detail is the separate SNVS register space. Main IOMUXC macros from `imx6ul-pinfunc.h` and SNVS macros from this file are not interchangeable even when the pad labels are similar. A wrong offset can configure the wrong SNVS pad, and a missing `ZERO_OFFSET_VALID` match would break the zero-offset `BOOT_MODE0` entry.

Other risks include:
- Electrical misconfiguration through the appended pad config cell, especially for low-power or wake pins.
- Board DTS files using these macros under the main `iomuxc` node instead of `iomuxc_snvs`.
- Incorrectly changing these GPIO-only definitions to add input select fields; this controller's listed routes do not use daisy registers.
- Boot-mode and tamper pads may have board-level strap or security implications, so muxing them as GPIO can conflict with hardware design assumptions.

## Test Signals
Build i.MX6ULL DTBs with `make ARCH=arm dtbs` and run `dtbs_check` against `Documentation/devicetree/bindings/pinctrl/fsl,imx35-pinctrl.yaml`. Confirm SNVS pinctrl groups have six cells per pin and are children of the `fsl,imx6ull-iomuxc-snvs` node. Runtime test signals include GPIO5 line enumeration, wake/tamper/button behavior if wired, and pinctrl debugfs showing the expected SNVS pad names. For changes to the zero-offset macro, boot-test specifically because schema validation cannot prove the driver wrote the intended SNVS MMIO register.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6ull-pinfunc-snvs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6ull-pinfunc.h -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6ull-pinfunc.h

## Purpose
This header extends the i.MX6UL pin-function catalog for i.MX6ULL. It includes `imx6ul-pinfunc.h`, fixes a small set of shared i.MX6UL/i.MX6ULL signal definitions with `#undef` plus replacement `#define`, and then adds i.MX6ULL-only alternate routes. It is included by `imx6ull.dtsi` together with `imx6ull-pinfunc-snvs.h`.

The file contains 64 macro definitions: five replacement `MX6UL_PAD_*` macros for shared signals whose input select values differ for i.MX6ULL, and 59 `MX6ULL_PAD_*` macros for i.MX6ULL-only routes. The added route families are dominated by EPDC display/power/control signals and ESAI audio signals, plus UART5 mux alternatives on UART1 pads.

## Important APIs, Types, and Functions
The API is a layered preprocessor contract:
- `#include "imx6ul-pinfunc.h"` imports the base i.MX6UL macro set.
- Five `#undef` statements remove inherited UART5-related macros.
- Replacement `#define` statements reuse the `MX6UL_PAD_*` names with i.MX6ULL-correct tuple values.
- New `MX6ULL_PAD_*__*` macros expose i.MX6ULL-only ALT9 routes.

All macros use the standard five-cell tuple:

```text
<mux_reg conf_reg input_reg mux_mode input_val>
```

The replacement macros are important because they change daisy select values for UART5 TX/RX/RTS paths while retaining the base macro names used by board files shared between i.MX6UL and i.MX6ULL. The i.MX6ULL-only additions mostly use `mux_mode` `0x9`; examples include EPDC routes on UART4/5, ENET, LCD, and CSI pads, and ESAI routes on CSI pads. Nine definitions have nonzero input select registers; the rest are output-only or no-daisy routes.

## Control Flow
There is no executable control flow, but the include/override order is a critical compile-time control path:
1. `imx6ull.dtsi` includes `imx6ul.dtsi`, which has already included `imx6ul-pinfunc.h`.
2. `imx6ull.dtsi` then includes this header.
3. This header includes `imx6ul-pinfunc.h` again, protected by the base header guard, then applies `#undef`/replacement definitions in this translation unit.
4. Board DTS files compiled through the i.MX6ULL include graph see the i.MX6ULL-correct replacement macro values and the additional `MX6ULL_PAD_*` names.
5. The compiled `fsl,pins` data is parsed by the same generic i.MX pinctrl driver path as i.MX6UL, using `FSL_PIN_SIZE` entries of five macro cells plus one config cell.

The runtime MMIO application is the same as i.MX6UL: parse tuple, store mux/config/input metadata, write mux register, optionally write input select, and apply pad control.

## State and Persistence Behavior
The header stores no runtime state. Its persistent behavior is that i.MX6ULL DTBs encode a combined macro universe: base i.MX6UL routes, corrected shared routes, and i.MX6ULL-only routes. The override pattern means the same symbolic `MX6UL_PAD_*` macro can expand differently depending on whether the DTS include graph is i.MX6UL or i.MX6ULL.

That include-order behavior is intentional but subtle. It preserves shared DTS source compatibility while producing SoC-specific daisy values in the compiled DTB. Changes to override names or order can therefore create silent differences in board DTBs.

## Dependencies and Integration Points
Direct integration points:
- Includes and depends on `imx6ul-pinfunc.h`.
- Included by `imx6ull.dtsi`.
- Consumed by i.MX6ULL board DTS and shared i.MX6UL/i.MX6ULL DTSI files.
- Parsed by `drivers/pinctrl/freescale/pinctrl-imx.c` and matched through `drivers/pinctrl/freescale/pinctrl-imx6ul.c`.
- Structurally described by `Documentation/devicetree/bindings/pinctrl/fsl,imx35-pinctrl.yaml`.

Peripheral integration is primarily EPDC and ESAI additions, plus corrected UART5 DCE/DTE paths. EPDC routes span LCD, ENET, UART, and CSI-origin pads; ESAI routes occupy CSI-origin pads. Those routes are selected only when board pinctrl groups use the new `MX6ULL_PAD_*` names.

## Risks
The main risks are include-order and SoC-variant drift. Removing or renaming a replacement macro can make shared i.MX6ULL board files inherit the i.MX6UL value, which may still compile but program the wrong UART5 daisy chain. Conversely, using `MX6ULL_PAD_*` macros on an i.MX6UL board source would compile only if this header is included, but the hardware route would not exist on pure i.MX6UL.

Other risks include:
- EPDC ALT9 routes are numerous and spread across unrelated pad banks, so board pinctrl groups can accidentally conflict with Ethernet, LCD, UART, or CSI functions.
- Most i.MX6ULL-only macros have no input select register; mistakes may only appear as dead outputs or visually incorrect display/audio behavior rather than schema failures.
- The five `#undef` replacements are easy to miss in review because the macro names retain the `MX6UL_` prefix.
- Pad control values remain board-specific; this header cannot validate display timing, audio signal integrity, drive strength, or voltage assumptions.

## Test Signals
Build representative i.MX6ULL DTBs with `make ARCH=arm dtbs` and inspect the expanded tuples for the five replacement UART5 macros. Run `dtbs_check` against `Documentation/devicetree/bindings/pinctrl/fsl,imx35-pinctrl.yaml` to catch cell-count and node-layout errors. Runtime signals include UART5 DCE/DTE loopback or console tests, EPDC display bring-up, ESAI audio capture/playback if wired, and pinctrl debugfs confirmation that selected groups map to expected pads. For edits to replacements, compare generated DTBs for shared i.MX6UL/i.MX6ULL DTSI users before and after the change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6ull-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx7d-pinfunc.h -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx7d-pinfunc.h

## Purpose
This header is the Devicetree pin-function catalog for the NXP/Freescale i.MX7D and i.MX7S IOMUX controllers. It defines `MX7D_PAD_*__*` macros that expand to the five-cell i.MX `PIN_FUNC_ID` tuple used by board DTS `fsl,pins` properties. It is included by `imx7s.dtsi`, which is the common base for i.MX7 system descriptions.

The file contains 1,139 pin-function macros over 158 physical pad names. It covers both LPSR pads (`MX7D_PAD_LPSR_GPIO1_IO00` through `IO07`) and the main IOMUXC pad set spanning GPIO1, EPDC, LCD, SD/MMC, SAI, ECSPI, UART, ENET/RGMII, QSPI, EIM, CSI, KPP, CCM, USB, watchdog, SDMA, and security/debug observation routes. The largest pad families are EPDC, SD, LCD, ENET, SAI, GPIO, UART, I2C-labeled pads, ECSPI, and LPSR.

## Important APIs, Types, and Functions
The public API is the macro set:

```text
MX7D_PAD_<pad>__<signal>  <mux_reg conf_reg input_reg mux_mode input_val>
```

Board DTS entries append one pad setting cell, producing the six-cell `fsl,pins` entry consumed by the generic i.MX pinctrl driver. The i.MX7D binding `Documentation/devicetree/bindings/pinctrl/fsl,imx7d-pinctrl.yaml` documents the same cell order and supports both `fsl,imx7d-iomuxc` and `fsl,imx7d-iomuxc-lpsr`.

Important API details:
- Main-controller macros and LPSR-controller macros live in the same header but are consumed by different compatible nodes.
- LPSR entries begin at zero offsets and depend on the `ZERO_OFFSET_VALID` flag in the `fsl,imx7d-iomuxc-lpsr` driver match data.
- Some LPSR input select writes use an `fsl,input-sel` phandle to the main IOMUXC controller because the LPSR instance shares daisy-chain registers with the main controller.
- The file uses mux modes 0 through 8.
- 425 macros have nonzero input select registers; 714 do not.

## Control Flow
The header itself has no executable control flow. Runtime flow is:
1. `imx7s.dtsi` includes the header and declares main and LPSR IOMUXC nodes.
2. Board DTS files use `MX7D_PAD_*__*` macros plus a pad config value inside pinctrl group `fsl,pins`.
3. `dtc` compiles each pin to six integer cells.
4. `drivers/pinctrl/freescale/pinctrl-imx7d.c` matches `fsl,imx7d-iomuxc` or `fsl,imx7d-iomuxc-lpsr` to the appropriate pad table and flags.
5. `pinctrl-imx.c` validates the group byte size against `FSL_PIN_SIZE`, parses each tuple, maps offsets to pin ids, handles SION in config, and stores the input-select metadata.
6. State selection writes mux and pad-control registers. If an input register is present, the generic code writes `input_val` either relative to the current IOMUXC base or to `input_sel_base` supplied through the LPSR `fsl,input-sel` relationship.

This control path makes the LPSR split more complex than a plain macro catalog: the same tuple layout can write through a different base for select-input registers depending on the matched controller instance.

## State and Persistence Behavior
The header stores no mutable state. It persists hardware routing data through DTS source and compiled DTBs. Runtime state is created when Linux writes main IOMUXC, LPSR IOMUXC, input select, and pad configuration registers.

The macro values are effectively part of the board-description ABI. Existing DTBs encode the numeric tuples, not the macro names, so edits only affect rebuilt DTBs. Source-level macro renames or removals affect DTS compilation, while numeric changes affect runtime pin routing.

## Dependencies and Integration Points
Direct integration points:
- Included by `arch/arm/boot/dts/nxp/imx/imx7s.dtsi`.
- Used by i.MX7D/i.MX7S board DTS files under `fsl,imx7d-iomuxc` and `fsl,imx7d-iomuxc-lpsr` pinctrl nodes.
- Parsed by `drivers/pinctrl/freescale/pinctrl-imx.c`.
- Matched by `drivers/pinctrl/freescale/pinctrl-imx7d.c`, including separate main and LPSR pad tables.
- Described by `Documentation/devicetree/bindings/pinctrl/fsl,imx7d-pinctrl.yaml`.

Peripheral integration spans display (`EPDC`, `LCD`), storage (`SD1`, `SD2`, `SD3`, QSPI), networking (`ENET1`, `ENET2`, RGMII), serial (`UART`, `I2C`, `ECSPI`, `SAI`), keypad, CAN, USB, watchdog, clock outputs, SDMA, and security/debug signals. Board-level drivers observe the result through their pinctrl state selection rather than by directly referencing this header.

## Risks
The main risks are wrong register offsets, wrong select-input values, and cross-controller misuse. A main-IOMUXC macro used under an LPSR node, or an LPSR macro used under the main node, can produce valid-looking `fsl,pins` data that writes the wrong register space. LPSR offset zero must remain valid through the correct driver match data.

Other risks include:
- Large EPDC/LCD/ENET/SD pad families have many alternate routes, making copy-paste mistakes plausible.
- Daisy-chain errors can break input-only aspects such as UART RX, CTS/RTS, I2C, card-detect/write-protect, MDIO, CAN RX, and clock inputs while mux output configuration appears correct.
- The `fsl,input-sel` requirement for LPSR nodes is structural; omitting it can direct select-input writes incorrectly or fail schema validation.
- Pad config cells are outside this header and can still create electrical failures through bad pull, drive, speed, hysteresis, or SION settings.
- Macro changes can break source compatibility for many board files because the i.MX7D header is a shared base include.

## Test Signals
Build i.MX7 DTBs with `make ARCH=arm dtbs` and run `dtbs_check` for `Documentation/devicetree/bindings/pinctrl/fsl,imx7d-pinctrl.yaml`. Include both main and LPSR pinctrl examples or boards; the LPSR path should require `fsl,input-sel`. Runtime validation should cover UART/I2C/SPI/CAN receive paths, SD card-detect/write-protect, Ethernet MDIO/RGMII, display pins, and low-power LPSR GPIO behavior. For header edits, compare DTB tuple output and boot logs, and inspect pinctrl debugfs for expected groups, mux modes, and selected pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx7d-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx7ulp-pinfunc.h -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx7ulp-pinfunc.h

## Purpose
This header is the Devicetree pin-function catalog for the NXP/Freescale i.MX7ULP A7-domain IOMUXC1 controller. It defines `IMX7ULP_PAD_*__*` macros for pads PTC, PTD, PTE, and PTF. The macros are consumed by `fsl,imx7ulp-iomuxc1` pinctrl groups in `imx7ulp.dtsi` and board DTS files.

Unlike i.MX6UL and i.MX7D, i.MX7ULP uses a shared mux/config register layout. Each macro expands to a four-cell tuple, not five cells:

```text
<mux_conf_reg input_reg mux_mode input_val>
```

The board DTS appends the fifth `CONFIG` cell. The file contains 462 macros over 68 pads. Pad families are PTC, PTD, PTE, and PTF, with function coverage led by FlexBus (`FB`), `FXIO1`, `VIU`, trace, TPM timers, LPSPI, SDHC, USB ULPI/ID/OC/PWR, LPUART, and LPI2C routes.

## Important APIs, Types, and Functions
The public API is the macro namespace:

```text
IMX7ULP_PAD_PTC<n>__<signal>
IMX7ULP_PAD_PTD<n>__<signal>
IMX7ULP_PAD_PTE<n>__<signal>
IMX7ULP_PAD_PTF<n>__<signal>
```

Each macro contributes four cells to `fsl,pins`; the i.MX7ULP binding documents each full entry as five cells after the board config is appended. This matches `pinctrl-imx.c` support for `SHARE_MUX_CONF_REG`, where `FSL_PIN_SHARE_SIZE` is 20 bytes per pin instead of the normal 24 bytes.

Important semantics:
- `mux_conf_reg` is the offset of a combined mux/config register.
- `input_reg` is the select-input register offset or zero when no daisy-chain write is required.
- `mux_mode` is inserted into the mux bitfield of the shared register. The i.MX7ULP driver uses mask `0xf00` and shift `8`.
- `input_val` selects the daisy-chain input when `input_reg` is nonzero.
- 218 macros have nonzero input select registers; 244 do not.
- Modes range through `0xc`, covering GPIO-like port functions, FXIO, LPSPI, LPUART, LPI2C, TPM, SDHC, FlexBus, trace, USB, and VIU alternatives.

## Control Flow
The header has no executable code. Runtime control flow is:
1. `imx7ulp.dtsi` includes this header and declares the i.MX7ULP IOMUXC1 controller.
2. Board DTS files place `IMX7ULP_PAD_*__*` macros plus config values inside group nodes ending in `grp`.
3. `dtc` compiles each entry to five cells.
4. `drivers/pinctrl/freescale/pinctrl-imx7ulp.c` matches `fsl,imx7ulp-iomuxc1` and calls the generic i.MX pinctrl probe with flags `ZERO_OFFSET_VALID | SHARE_MUX_CONF_REG`.
5. `imx_pinctrl_parse_groups()` uses `FSL_PIN_SHARE_SIZE`; `imx_pinctrl_parse_pin_mmio()` reads `mux_conf_reg`, treats it as both mux and config register, reads `input_reg`, `mux_mode`, `input_val`, and config, then derives the pin id from the register offset.
6. On state selection, `imx_pmx_set_one_pin_mmio()` read-modify-writes only the mux bitfield of the shared register, then select-input registers when present. Pad config is handled by the pinconf path using the same shared register.
7. GPIO direction changes use the i.MX7ULP-specific `gpio_set_direction` hook to toggle output-buffer-enable and input-buffer-enable bits in the shared register.

## State and Persistence Behavior
The header stores no runtime state. Its persistent output is the numeric pin-function tuple embedded into DTBs. Runtime state lives in IOMUXC1 mux/config registers, input-select registers, and the GPIO direction-related OBE/IBE bits controlled by the i.MX7ULP pinctrl driver.

Because the mux and configuration fields share a register, ordering and masking are important. The generic mux setter read-modify-writes the mux bits, and the pinconf path must preserve unrelated bits. A macro offset error can therefore affect both mux and pad configuration for a pin.

## Dependencies and Integration Points
Direct integration points:
- Included by `arch/arm/boot/dts/nxp/imx/imx7ulp.dtsi`.
- Consumed by i.MX7ULP board DTS pinctrl groups under compatible `fsl,imx7ulp-iomuxc1`.
- Parsed by `drivers/pinctrl/freescale/pinctrl-imx.c` with `SHARE_MUX_CONF_REG`.
- Matched and specialized by `drivers/pinctrl/freescale/pinctrl-imx7ulp.c`.
- Described by `Documentation/devicetree/bindings/pinctrl/fsl,imx7ulp-iomuxc1.yaml`.

Peripheral integration is through A7-domain board pinctrl states for LPUART4-7, LPI2C4-7, LPSPI2-3, TPM timers, SDHC0/1, FXIO, FlexBus, VIU, trace, USB0/USB1 ULPI and ID/OC/PWR signals, and GPIO ports PTC/PTD/PTE/PTF.

## Risks
The largest risk is using the wrong tuple width. Treating these macros like normal five-cell i.MX macros before config would produce malformed `fsl,pins` data and incorrect driver parsing. Conversely, using normal i.MX macros under `fsl,imx7ulp-iomuxc1` would fail size validation or misalign cells.

Other risks include:
- Combined mux/config registers make offset mistakes more damaging, because mux and electrical settings share the same register.
- `mux_mode` values must be masked and shifted by the driver; macro values are unshifted modes, not full register images.
- GPIO direction depends on OBE/IBE bits in the same register, so pad config changes can interfere with direction behavior if masks are wrong.
- Nonzero input select values are common for serial, SPI, I2C, timer, USB, and VIU paths; daisy errors can leave input paths dead while output muxing appears correct.
- The header covers only IOMUXC1 A7-domain pads; it does not describe M4-domain IOMUXC0 or DDR IOMUXC pads.

## Test Signals
Build i.MX7ULP DTBs with `make ARCH=arm dtbs` and run `dtbs_check` for `Documentation/devicetree/bindings/pinctrl/fsl,imx7ulp-iomuxc1.yaml`. Validation should confirm five cells per full `fsl,pins` entry and group node names matching the schema pattern. Runtime tests should cover LPUART RX/TX, LPI2C, LPSPI, SDHC, USB ID/OC/ULPI where wired, GPIO input/output direction changes, and pinctrl debugfs group mappings. For macro edits, compare generated DTB cells and verify that mux/config register read-modify-write behavior preserves non-mux bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx7ulp-pinfunc.h -->
