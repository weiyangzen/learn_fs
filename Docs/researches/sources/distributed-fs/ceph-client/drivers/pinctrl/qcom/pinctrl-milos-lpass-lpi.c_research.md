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
