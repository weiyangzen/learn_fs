# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8516.h

## Purpose
This header defines the MT8516 pin table for the legacy MediaTek pinctrl common driver. It includes `pinctrl-mtk-common.h` and declares `static const struct mtk_desc_pin mtk_pins_mt8516[]`, a 125-pin table. The first pins are named `EINT0` through `EINT19`, later entries use functional pad names such as MSDC0 lines, and the table ends with GPIO121 through GPIO124.

## Important APIs, Types, And Data
The file uses legacy `struct mtk_desc_pin` and the macros `MTK_PIN`, `PINCTRL_PIN`, `MTK_EINT_FUNCTION`, and `MTK_FUNCTION`. It is not compatible with Paris `struct mtk_pin_desc` without translation. Each pin lists one or more mux values, with function zero normally being GPIO mode. Important function families include PWM, I2S/I2S3/TDM, external bus/control signals, CONN MCU/debug signals, SQI/SPI, USB, PWRAP, MSDC0/MSDC1/MSDC2, PCM/MRG, SPDIF, antenna control, and debug monitor outputs.

## Control Flow And Integration
This file contributes static data to the MT8516 platform pinctrl driver. The legacy common driver registers these pins with Linux pinctrl, maps pinmux states from devicetree to per-pin functions, and performs register writes through companion MT8516 register/drive/EINT data. There is no local function control flow in this header.

## State And Persistence
All state in the file is immutable kernel data. Runtime mux and pin configuration state is stored in hardware registers and the common driver's private structures. No values are persisted to disk or NVRAM by this code.

## Dependencies
The table depends on old MediaTek common-driver definitions and companion MT8516 register metadata. The EINT naming of early pins must match both hardware interrupt numbering and board devicetree usage. Function names and mux values must match binding headers and datasheet definitions for multimedia, storage, connectivity, and external bus functions.

## Risks
The main risk is mux-value mismatch on shared pins. MT8516 uses many function names that encode bus lanes or debug monitor bits; a wrong value can partially break a bus while still allowing the pinctrl state to apply. Early `EINT*` pad names can confuse code or tests that assume names are `GPIO*`. Tail pins with only function zero should be treated as limited GPIO-only pads. Schema mismatch with Paris/common-v2 is also a maintenance risk.

## Test Signals
Test with MT8516 driver compilation, devicetree pin state parsing, GPIO request and direction tests across EINT-named and GPIO-named pads, EINT interrupt tests for early pins, and peripheral smoke tests for PWM, audio, SPI/SQI, USB, PWRAP, MSDC, and external interface pins. Static review should preserve 125 contiguous entries.
