# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm6115.c

## Purpose
Defines the main SM6115 TLMM controller for the shared MSM pinctrl driver. It uses a tiled register map (`south`, `east`, `west`), 113 regular GPIOs, a UFS reset pseudo-line, SDC1/SDC2 special pads, mux functions for QUP/camera/UIM/audio/debug/test signals, and an MPM wake map.

## Important APIs, Types, And Functions
`sm6115_tiles[]` and the `SOUTH/EAST/WEST` enum name the TLMM regions consumed by the common driver. `PINGROUP()` adds `.tile = _tile` alongside the normal 0x1000 stride and standard mux/pull/drive/GPIO/IRQ bit fields. `SDC_QDSD_PINGROUP()` and `UFS_RESET()` also carry tile metadata, with UFS forced to `WEST`. `sm6115_groups[]` assigns every GPIO and special group to a tile and mux selector list. `sm6115_mpm_map[]` maps GPIOs to MPM wake interrupt numbers. `sm6115_tlmm` sets `ngpios = 114`, tile metadata, and wake map pointers.

## Control Flow
`sm6115_tlmm_init()` registers the platform driver at `arch_initcall`. The `qcom,sm6115-tlmm` match calls `sm6115_tlmm_probe()`, which delegates to `msm_pinctrl_probe()`. The common driver uses tile names to map/select register banks, then uses group descriptors to program mux/pinconf/GPIO/IRQ state. Wake setup uses the MPM map rather than a PDC map.

## State And Persistence
This file has static descriptor state only. Runtime state lives in the common driver and TLMM/MPM hardware. `ngpios = 114` includes GPIO0-112 and UFS reset at group 113; SDC groups 114-120 are special pad controls and not normal GPIOs.

## Dependencies And Integration Points
Integrates with `pinctrl-msm` tiled-bank support, MPM wake IRQ handling, UFS, SD/eMMC, QUP0-5, camera CCI/MCLK/timers, UIM1/2, display vsync, audio/adsp pins, USB PHY, QDSS, WLAN ADC, navigation/GPS, and several test/debug functions. Device-tree must provide TLMM resources compatible with the tile names used here.

## Risks
Tile assignment is a major risk: a correct offset in the wrong tile writes the wrong MMIO bank. MPM wake mappings are hand-maintained and must match firmware/interrupt-controller numbering. UFS reset and SDC groups are GPIO-like array entries but have restricted bit fields; consumers must not assume full IRQ or mux support. Function names such as `atest`, `dac_calib`, and `phase_flag` are broad test hooks, so accidental board usage can conflict with manufacturing/debug modes.

## Test Signals
Probe on `qcom,sm6115-tlmm`, debugfs showing tile-backed groups, GPIO direction/value/IRQ tests across all three tiles, MPM wake tests during suspend, UFS reset and storage bring-up, SD1/SD2 pad operation, QUP/camera/UIM/display pin states, and validation that pinctrl states touching special groups reject unsupported GPIO/IRQ operations. Source size reviewed: 923 lines.
