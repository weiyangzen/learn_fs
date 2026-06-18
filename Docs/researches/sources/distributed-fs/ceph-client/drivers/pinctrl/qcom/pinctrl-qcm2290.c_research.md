# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-qcm2290.c

## Purpose
This file describes the Qualcomm QCM2290 TLMM pin controller. It provides the static pin, function, pingroup, eGPIO, SDC, and MPM wake metadata consumed by the common `pinctrl-msm` driver.

## Important APIs, types, and functions
The descriptor is formed by `qcm2290_pins`, `qcm2290_functions`, `qcm2290_groups`, `qcm2290_mpm_map`, and `qcm2290_pinctrl`. `PINGROUP()` creates normal 0x1000-stride GPIO groups and includes standard mux, pull, drive, output-enable, input/output, and interrupt bit positions. Unlike older descriptors, it also fills `.egpio_enable = 12` and `.egpio_present = 11`. `SDC_QDSD_PINGROUP()` covers SDC1/SDC2 special pads. A `UFS_RESET()` macro is defined but this file's group table does not instantiate a UFS reset group.

Probe is `qcm2290_pinctrl_probe()` -> `msm_pinctrl_probe(pdev, &qcm2290_pinctrl)`. The platform driver matches `qcom,qcm2290-tlmm` and registers through `arch_initcall()`.

## Control flow
The platform bus binds the DT node, probe passes `qcm2290_pinctrl` to the common core, and all pinmux, pinconf, GPIO, IRQ, and wake operations are driven from the arrays in this file. The `qcm2290_groups` array is indexed explicitly, including dummy groups for missing or unavailable pins so pin numbers remain aligned with pinctrl descriptors.

## State and persistence behavior
No mutable C state is stored here. Hardware register state is modified later by the common core. The descriptor contains GPIO0-126 plus SDC1_RCLK, SDC1_CLK/CMD/DATA, and SDC2_CLK/CMD/DATA descriptors. `.ngpios = 127` limits gpiolib exposure to GPIO0-126. `.egpio_func = 9` defines the mux slot used for eGPIO-capable pins 98-126, matching the final mux argument in those pingroups.

## Dependencies and integration points
The file depends on platform/OF/module APIs and `pinctrl-msm.h`. It integrates with DT consumers for QUP serial engines, CCI/camera, QDSS, PBS, PWM, UIM, USB PHY, MDP vsync, GCC GP clocks, navigation GPIOs, WLAN ADC, SDC test bus, and eGPIO. `qcm2290_mpm_map` integrates selected GPIOs with the MPM wake controller.

## Risks and edge cases
The eGPIO metadata is easy to break: `egpio_func` must match the mux slot where `egpio` is placed, and `egpio_enable`/`egpio_present` bit positions must match hardware. Dummy groups intentionally keep indexes stable; removing them can shift every later group. The file defines but does not use `UFS_RESET()`, which is harmless but can mislead future edits. SDC groups have disabled GPIO/IRQ fields and must not be exposed as normal GPIOs. Wake IRQ map mistakes affect suspend behavior rather than normal pinctrl registration.

## Test signals
Check binding for `qcom,qcm2290-tlmm`, 127 GPIO lines, successful eGPIO function selection on GPIO98-126, QUP/CCI/PWM/UIM/USB pinmux selection from DT, SDC1/SDC2 pinconf behavior, GPIO IRQ tests, suspend wake tests for mapped GPIOs, and pinctrl debugfs validation that dummy groups do not appear as requestable client groups.
