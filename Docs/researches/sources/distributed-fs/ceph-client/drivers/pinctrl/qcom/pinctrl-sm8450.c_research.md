# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8450.c

## Purpose
This file is the Qualcomm SM8450 TLMM pin controller description. It does not implement the generic pinctrl algorithms itself; instead it supplies SM8450-specific pin, mux-function, pingroup, wake IRQ, eGPIO, UFS reset, and SDC/QDSD register metadata to the shared Qualcomm `pinctrl-msm` driver. The platform driver binds to `qcom,sm8450-tlmm` and registers early through `arch_initcall()` so board pin states are available during early platform bring-up.

## Important APIs, Types, And Functions
The primary exported-to-core data object is `static const struct msm_pinctrl_soc_data sm8450_tlmm`. It references `sm8450_pins`, `sm8450_functions`, `sm8450_groups`, and `sm8450_pdc_map`, sets `ngpios = 211`, and declares `egpio_func = 9`. `PINGROUP()` builds normal GPIO-backed `struct msm_pingroup` entries with a 0x1000 register stride, mux at bit 2, pull at bit 0, drive at bit 6, OE at bit 9, eGPIO presence/enable at bits 11/12, and PDC interrupt fields. `SDC_QDSD_PINGROUP()` describes special SD-card pins without GPIO mux or interrupt capability. `UFS_RESET()` describes the UFS reset pin with output control but no mux or IRQ. `sm8450_tlmm_probe()` delegates to `msm_pinctrl_probe(pdev, &sm8450_tlmm)`.

## Control Flow
Driver registration installs a platform driver named `sm8450-tlmm`. Device-tree matching on `qcom,sm8450-tlmm` calls `sm8450_tlmm_probe()`, which hands the static SoC tables to the shared `msm_pinctrl_probe()` path. From that point, normal pinctrl, pinmux, pinconf, GPIO, and interrupt operations are driven by the common driver using this file's offsets and bit positions. Each GPIO group selects among `msm_mux_gpio` plus nine alternate mux slots; most unused slots are filled with the placeholder `msm_mux__`.

## State And Persistence
The file itself has no mutable runtime state. All arrays are static const except compound-literal function lists embedded in group initializers. Runtime state, locking, IRQ domain setup, GPIO chip state, and register writes are owned by `pinctrl-msm.c`. Hardware state persists in TLMM registers until reset, suspend restore, or later pinctrl changes by consumers. The PDC wake mapping is static metadata translating selected TLMM GPIO numbers to PDC wake interrupt numbers.

## Dependencies And Integration Points
It depends on Linux platform-driver/module/OF APIs and the Qualcomm `pinctrl-msm.h` data contract. Integration points are device-tree pinctrl nodes using the `qcom,sm8450-tlmm` compatible, subsystem consumers naming function/group pairs in pin states, gpiolib users for GPIO 0-210, IRQ consumers routed through TLMM/PDC, and storage controllers using the special UFS reset and SDC2 groups. The function catalogue covers camera clocks and CCI, QUP serial engines, QSPI, UIM, audio I2S/MI2S, display vsync, PCIe clock request, USB PHY, qlink/coexistence, debug/QDSS, DDR/test, and eGPIO pads.

## Risks
The largest risk is table accuracy. A wrong group-to-function slot silently programs the wrong mux value. A wrong register offset or bit assignment can corrupt unrelated TLMM pads because normal GPIO register blocks are stride-derived. `ngpios = 211` intentionally excludes the non-GPIO UFS/SDC groups at array indices 210-213; changing that boundary would expose special pads as normal GPIOs. The wake IRQ map must match PDC hardware, or wake-capable GPIOs may fail suspend/resume testing. eGPIO support depends on the mux slot index matching `egpio_func = 9`.

## Test Signals
Useful signals are probe success for `qcom,sm8450-tlmm`, expected registration of 211 GPIOs, pinctrl state application for representative QUP, camera, audio, UIM, QSPI, PCIe, and display functions, GPIO input/output and interrupt tests across several banks, wake-from-suspend tests for mapped PDC GPIOs, UFS reset toggling, SDC2 pad configuration, and debugfs pinmux/pinconf dumps showing mux, pull, drive, and eGPIO fields at expected register offsets.
