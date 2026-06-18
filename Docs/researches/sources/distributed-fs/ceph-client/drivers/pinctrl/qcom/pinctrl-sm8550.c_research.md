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
