# sources/distributed-fs/ceph-client/include/linux/mfd/mt6397/registers.h

## Purpose

This header is the legacy MT6397 PMIC register map. It covers top-level clock/reset/status, interrupt control/status, EFUSE, buck regulators, LDO regulators, speaker, audio DAC/buffer/ADC, zero-cross detection, and related analog/audio blocks.

## Important APIs, Types, and Functions

The exported API is the `MT6397_*` register macro namespace. Key definitions include `MT6397_CID`, `MT6397_TOP_CKPDN*`, `MT6397_TOP_RST_*`, `MT6397_INT_CON0`, `MT6397_INT_CON1`, `MT6397_INT_STATUS0`, `MT6397_INT_STATUS1`, EFUSE data registers, buck register blocks such as `MT6397_VCA15_CON*`, `MT6397_VCORE_CON*`, and `MT6397_VGPU_CON*`, LDO blocks such as `MT6397_ANALDO_CON*` and `MT6397_DIGLDO_CON*`, speaker registers, and audio registers such as `MT6397_AUDDAC_CON0`, `MT6397_AUDADC_CON*`, and `MT6397_ZCD_CON*`.

## Control Flow

No executable flow is defined. `mt6397-core.c` reads chip ID and instantiates children with resources. `mt6397-irq.c` uses interrupt control/status registers for the legacy IRQ controller. `mt6397-regulator.c` maps regulator descriptors to buck/LDO addresses and selects voltage registers at probe time. PMIC key and audio consumers use the same address contract for event and codec handling.

## State and Persistence Behavior

The header maps PMIC hardware state. Interrupt masks/latches, EFUSE values, regulator voltages/enables, audio analog settings, and clock/reset controls are hardware state; some are volatile, while EFUSE and certain retention/power-domain registers are persistent or reset-domain-dependent. The header itself stores nothing.

## Dependencies and Integration Points

It is paired with `mt6397/core.h` and consumed by MFD, IRQ, regulator, key, pinctrl, LED, RTC resource, and codec paths. Macro names are embedded in regulator descriptor tables, so address names and chip revision quirks must stay aligned with `drivers/regulator/mt6397-regulator.c`.

## Risks and Edge Cases

MT6397 uses a different RTC base/resource style than MT6357/6358/6359, so mixing register maps across chips is unsafe. Regulator descriptors rely on control register offsets and bit positions outside this file; address drift creates hard-to-diagnose voltage behavior. Interrupt status/control registers are only two primary groups for this legacy chip, unlike newer top-group PMIC IRQ maps.

## Test Signals

Build and boot MT6397 MFD and regulator drivers; read `MT6397_CID`; verify regulator registration and voltage control for buck and LDO rails; exercise PMIC key and RTC resources; check IRQ mask/status behavior with `/proc/interrupts`; and validate audio codec paths when MT6397 audio is enabled.
