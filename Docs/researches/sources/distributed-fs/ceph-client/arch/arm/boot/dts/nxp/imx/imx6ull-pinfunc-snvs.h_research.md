# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6ull-pinfunc-snvs.h

## Purpose
This header is the i.MX6ULL SNVS-domain pin-function catalog. It defines symbolic `MX6ULL_PAD_*__GPIO5_IO*` macros for the SNVS IOMUXC instance used by boot mode and tamper pads. It is included by `imx6ull.dtsi` alongside `imx6ull-pinfunc.h` so board DTS files can configure the low-power/SNVS pin controller at `fsl,imx6ull-iomuxc-snvs`.

The file contains 12 macros over 12 pads: `BOOT_MODE0`, `BOOT_MODE1`, and `SNVS_TAMPER0` through `SNVS_TAMPER9`, all exposed as GPIO5 lines.

## Important APIs, Types, and Functions
Each macro expands to the standard five-cell tuple `<mux_reg conf_reg input_reg mux_mode input_val>`, and board DTS entries append the sixth pad `CONFIG` cell. All macros use mux mode `0x5`, input register `0x0000`, and input value `0x0`, because these entries route SNVS pads to GPIO without daisy-chain input select programming.

The header uses an i.MX6ULL-specific `MX6ULL_PAD_*` prefix because these pads live in the SNVS IOMUXC register space. The register offsets start at zero, so they depend on the SNVS driver match data treating offset zero as valid.

## Control Flow
There is no executable control flow in the header. `imx6ull.dtsi` includes it, board pinctrl groups compile the macros into `fsl,pins`, and `drivers/pinctrl/freescale/pinctrl-imx6ul.c` matches `fsl,imx6ull-iomuxc-snvs` to `imx6ull_snvs_pinctrl_info`. The generic i.MX parser reads the five macro cells plus config. The SNVS info sets `ZERO_OFFSET_VALID`, so `mux_reg = 0x0000` for `BOOT_MODE0` is a real register offset rather than a sentinel. State selection writes SNVS mux and pad configuration registers; no input-select register is written.

## State and Persistence Behavior
The file stores no state. Compiled DTBs persist SNVS pad MMIO offsets and GPIO mux selections. Runtime state lives in SNVS IOMUXC mux and pad configuration registers, affecting GPIO5 boot/tamper pad behavior and low-power-domain pad setup.

## Dependencies and Integration Points
It is included by `imx6ull.dtsi`, used under `iomuxc_snvs: pinctrl@2290000`, parsed by the generic i.MX pinctrl driver through `pinctrl-imx6ul.c`, and described by `Documentation/devicetree/bindings/pinctrl/fsl,imx35-pinctrl.yaml`. Board integrations may use these pads for wake inputs, tamper-related GPIOs, boot strap observation, USB detect lines, buttons, or low-power control signals.

## Risks
Main risks are mixing SNVS macros with the main IOMUXC node, losing `ZERO_OFFSET_VALID` behavior for offset-zero pads, and electrically unsafe appended pad config values. Because these are boot/tamper-domain pads, incorrect GPIO muxing can conflict with board strap, wake, or security assumptions. The macros intentionally have no daisy register; adding one would change runtime writes unexpectedly.

## Test Signals
Build i.MX6ULL DTBs and run `dtbs_check` against `fsl,imx35-pinctrl.yaml`. Confirm groups are children of the `fsl,imx6ull-iomuxc-snvs` node and have six cells per pin. Runtime signals include GPIO5 line behavior, wake/tamper/button tests if wired, and pinctrl debugfs showing expected SNVS pads.
