# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm4450.c

## Purpose
Defines the SM4450 application-processor TLMM pin controller for the common MSM pinctrl driver. It describes 136 GPIOs, UFS reset, SDC1/SDC2 special pads, mux tables for camera/display/QUP/UIM/USB/PCIe/debug functions, eGPIO bits, and PDC wake routing for `qcom,sm4450-tlmm`.

## Important APIs, Types, And Functions
`PINGROUP()` uses a 0x1000 register stride, standard mux/pull/drive/output/IRQ bit positions, and eGPIO bits 11/12. `SDC_QDSD_PINGROUP()` and `UFS_RESET()` describe special nonstandard pads. `QUP_I3C()` is defined but unused in this file, suggesting a leftover helper or future extension. `sm4450_pins[]`, `DECLARE_MSM_GPIO_PINS()`, `enum sm4450_functions`, function group arrays, `sm4450_functions[]`, and `sm4450_groups[]` provide the actual pinctrl surface. `sm4450_pdc_map[]` supplies GPIO wake routing. `sm4450_tlmm` packages this data with `ngpios = 137`.

## Control Flow
Early platform-driver registration happens through `arch_initcall`. The OF compatible `qcom,sm4450-tlmm` calls `sm4450_tlmm_probe()`, which passes `sm4450_tlmm` to `msm_pinctrl_probe()`. The common driver registers pins, functions, GPIOs, and IRQ support, then programs group registers according to device-tree pinctrl states and GPIO/IRQ clients.

## State And Persistence
The file is static data. Runtime pin state persists in TLMM, UFS reset, and SD pad registers. GPIOs 0-135 plus the UFS reset pseudo-line are gpiolib-visible through `ngpios = 137`; SDC pins 137-143 are special pinctrl-only groups. eGPIO present/enable bits allow the shared driver to account for externally capable GPIO pads.

## Dependencies And Integration Points
Integrates with `pinctrl-msm`, PDC wake IRQ support, UFS, SD/eMMC, QUP/I3C-capable serial engines, camera CCI/MCLK, display vsync, UIM, USB PHY/HS analog controls, PCIe clock request, WLAN coexistence/test signals, QDSS CTI/GPIO, and power/debug/test functions. Device-tree pin state names must match the function and group strings here exactly.

## Risks
The unused `QUP_I3C()` macro is harmless at runtime but can mislead maintainers into thinking I3C mode registers are wired when only mux names are present. Wake map density creates suspend-resume risk if any GPIO/PDC pair is wrong. UFS reset at 0x97000 and SDC offsets at 0x8c000/0x8f000 must match the SoC address map, not the normal GPIO stride. Function alternatives include many `_` placeholders, so selector position is more important than visible function count.

## Test Signals
Probe and debugfs inspection on SM4450 hardware, GPIO/IRQ tests across low and high GPIO numbers, PDC wake from representative mapped pins, UFS reset assertion/deassertion, SD1/SD2 operation, QUP serial/I2C/I3C-mode board tests, camera CCI/MCLK states, display vsync outputs, USB PHY control, and PCIe clock request pin behavior. Source size reviewed: 1010 lines.
