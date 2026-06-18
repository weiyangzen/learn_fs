# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdm660.c

## Purpose

`pinctrl-sdm660.c` is the Qualcomm SDM660/SDM630 TLMM pinctrl data driver for the shared MSM pinctrl core. It describes 114 ordinary GPIOs plus SD-card groups, the three TLMM tiles, alternate functions, and an MPM wake interrupt map. The source is table-oriented with a thin platform driver wrapper.

## Important APIs, Types, and Data

- Includes `pinctrl-msm.h` and provides `sdm660_pinctrl`, a `struct msm_pinctrl_soc_data`.
- `sdm660_tiles[]` names `north`, `center`, and `south`; the enum values are embedded in each `PINGROUP()` row.
- `PINGROUP()` generates standard TLMM groups with ten mux slots, register offsets based on `REG_SIZE * id`, the tile selector, GPIO data bits, and IRQ bit positions.
- `SDC_QDSD_PINGROUP()` defines non-GPIO SD card groups with pull/drive fields and disabled mux/GPIO/IRQ fields.
- `sdm660_pins[]` defines GPIO descriptors for GPIO 0 through 113 and special SD card descriptors for SDC1/SDC2 clock, command, data, and SDC1 return clock.
- `DECLARE_MSM_GPIO_PINS()`, `enum sdm660_functions`, per-function group arrays, `sdm660_functions[]`, and `sdm660_groups[]` describe the multiplexing graph.
- Function coverage includes BLSP/QUP, CCI, camera clocks, MDP vsync, TSIF, MI2S/SLIMbus/LPASS audio, UIM, WLAN/ADC/test signals, QDSS, USB, PCIe, SD write protect, and debug/test hooks.
- `sdm660_mpm_map[]` maps GPIOs to MPM wake interrupt numbers.
- `sdm660_pinctrl` sets pins, functions, groups, `.ngpios = 114`, tiles, and the MPM wake map.
- OF matching supports both `qcom,sdm660-pinctrl` and `qcom,sdm630-pinctrl`.

## Control Flow

`sdm660_pinctrl_init()` registers the platform driver at `arch_initcall()`. OF match creates the platform device for either SDM660 or SDM630 compatible strings. Probe calls `msm_pinctrl_probe(pdev, &sdm660_pinctrl)`, after which the shared MSM core performs resource mapping, pinctrl/gpio registration, and IRQ setup using this file's static data. Exit unregisters the platform driver.

## State and Persistence

The source contains no driver-local mutable state. Static tables define the SoC contract. Runtime state is created by the MSM core and hardware state persists in TLMM registers. Wake state uses MPM mapping data supplied here and is managed by the core and interrupt subsystem.

## Dependencies and Integration Points

The file depends on the Linux OF/platform/module stack and the common MSM pinctrl core. It integrates with SDM660 and SDM630 device trees, gpiolib, pinctrl consumers for camera/display/audio/serial/storage/debug peripherals, and MPM wake interrupt routing. Tile names must match memory resource names in the platform description.

## Risks and Edge Cases

- One data table is used for both SDM660 and SDM630 compatibles; any silicon differences not represented here can cause board-specific pinmux or wake issues.
- Tile assignment is part of each pingroup. A wrong tile can map otherwise correct register offsets into the wrong memory region.
- Wake mapping uses MPM rather than PDC; incorrect GPIO-to-MPM rows break suspend wake without affecting normal GPIO tests.
- `.ngpios = 114` must remain aligned with the ordinary GPIO range, excluding SDC-only groups.
- SD card groups disable most GPIO/IRQ fields and should only be used for supported pull/drive configuration.

## Test Signals

Build signals include successful compilation and no missing `msm_mux_*` references. Runtime signals include driver probe on both `qcom,sdm660-pinctrl` and `qcom,sdm630-pinctrl` boards, expected 114 GPIO lines, debugfs function/group visibility, pin state application for serial/camera/display/audio/storage clients, SD card pull/drive behavior, and suspend/resume wake tests for entries in `sdm660_mpm_map[]`.
