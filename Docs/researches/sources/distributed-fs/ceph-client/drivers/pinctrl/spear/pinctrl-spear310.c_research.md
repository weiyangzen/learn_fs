<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear310.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear310.c

## Purpose
This file is the SPEAr310-specific overlay for the common SPEAr3xx pinmux definitions. It adds extra UART, EMI, FSMC, RS485, and TDM functions, initializes common mux register placeholders to the SPEAr310 register offset, and registers `st,spear310-pinmux`.

## Important APIs, Types, And Data
- `PMX_CONFIG_REG` is `0x08`.
- SPEAr310-specific groups include `emi_cs_0_to_5`, `uart1` through `uart5`, `fsmc`, `rs485_0`, `rs485_1`, and `tdm`.
- `spear310_pingroups[]` prepends `SPEAR3XX_COMMON_PINGROUPS` and then adds SPEAr310-specific groups.
- `spear310_functions[]` similarly combines common functions and SPEAr310-specific functions.
- Probe uses `pmx_init_addr()` and `pmx_init_gpio_pingroup_addr()` to retarget common SPEAr3xx mux register placeholders to `PMX_CONFIG_REG`.

## Control Flow And Integration
The platform driver matches `st,spear310-pinmux`. Probe mutates the shared `spear3xx_machdata` by assigning SPEAr310 groups/functions, initializing mux register addresses, enabling common GPIO pingroup register addresses, setting `modes_supported = false`, and calling `spear_pinctrl_probe()`.

SPEAr310 has no separate mode table. Alternate functions are selected directly by clearing bits in `PMX_CONFIG_REG`: UART1 clears FIRDA, UART2 clears timer 0/1, UART3-5 share UART0 modem bits, FSMC clears SSP chip select bits, RS485/TDM clear MII bits, and EMI chip selects clear timer mux bits.

## State And Persistence
The file stores only static tables and modifies the process-global `spear3xx_machdata` during probe. Hardware state persists in `PMX_CONFIG_REG`. Common GPIO fallback behavior is enabled for the inherited SPEAr3xx groups after their register addresses are initialized.

## Dependencies
It depends on `pinctrl-spear3xx.h` and the common SPEAr pinctrl core. Because it edits shared `spear3xx_machdata`, it assumes each SPEAr3xx SoC driver is instantiated in a way that does not require multiple variants to coexist with independent machdata.

## Risks And Review Notes
- `rs485_0_grps[]` contains `"rs485_0"` while the declared group is `"rs485_0_grp"`; `rs485_1` has the same suffix mismatch. This can prevent those functions from resolving their groups.
- Multiple UART functions share the same `PMX_UART0_MODEM_MASK`; selecting one can exclude the others.
- This driver mutates shared common machdata at probe time. Cross-SoC coexistence is unlikely in real hardware, but it is a test isolation concern.
- No mode gating means invalid DT combinations rely entirely on pinctrl state selection and shared mask conflicts.

## Test Signals
Build and boot with `st,spear310-pinmux`. Confirm common and SPEAr310-specific functions appear in pinctrl debugfs. Apply DT states for UART1-5, EMI, FSMC, RS485, and TDM, and verify `PMX_CONFIG_REG` readback. Specifically test RS485 group lookup because the function group strings appear inconsistent with pingroup names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear310.c -->
