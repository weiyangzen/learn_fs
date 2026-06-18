# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-hawi.c

## Purpose
Defines the QTI Hawi TLMM SoC description for the common Qualcomm MSM pinctrl driver. It describes 227 GPIO-capable lines plus UFS reset and three SDC2 control groups, with modern eGPIO and PDC wakeirq support.

## Important APIs, Types, and Functions
Key objects are `hawi_pins[]`, `enum hawi_functions`, the function group arrays, `hawi_functions[]`, `hawi_groups[]`, `hawi_pdc_map[]`, and `hawi_tlmm`. `PINGROUP()` creates GPIO groups with 12 function slots, 0x1000 register spacing, mux/pull/drive/output fields, eGPIO present/enable fields, and IRQ/wakeup routing fields. `UFS_RESET()` models the UFS reset output group. `SDC_QDSD_PINGROUP()` creates SDC2 clock, command, and data pinconf-only groups. `hawi_tlmm_probe()` delegates to `msm_pinctrl_probe()`.

## Control Flow
`arch_initcall(hawi_tlmm_init)` registers the platform driver. OF matching on `qcom,hawi-tlmm` invokes probe, which passes `hawi_tlmm` to the common pinctrl implementation. Runtime mux/config/GPIO/IRQ operations are driven by device-tree pinctrl states and common `pinctrl-msm` callbacks using Hawi's static metadata.

## State and Persistence Behavior
The file contains only static tables and no local mutable state. Pin configuration, GPIO output, interrupt, wakeup, UFS reset, and eGPIO ownership state persist in hardware registers managed by the common core. `.ngpios = 227` exposes only real GPIO pingroups; UFS and SDC2 groups remain pinctrl-only.

## Dependencies and Integration Points
Depends on platform-driver/OF support and `pinctrl-msm.h`. It integrates with Hawi device trees, QUP and I2C hub serial engines, camera CCI/MCLK, DP/display sync, PCIe clock/reset pins, QSPI, UIM, USB, navigation/RFFE/coexistence pins, SDC2, UFS reset, QDSS/debug pins, PDC wake IRQs, and Linux GPIO consumers.

## Risks
Hawi's dense function table contains many similarly named split functions, such as QUP lane variants and display sync outputs; wrong group membership or enum ordering would be hard to diagnose at runtime. PDC wake mapping must match silicon and board wiring. The UFS reset and SDC groups use reduced capability macros, so generic GPIO assumptions would be incorrect. eGPIO selector value `11` must remain synchronized with the final function slot in `PINGROUP()`.

## Test Signals
Validate successful probe for `qcom,hawi-tlmm`, expected pin and GPIO counts in debugfs, DT pinctrl selection for QUP/I2C hub, camera, DP/display, PCIe, QSPI, UIM, USB, SDC2, and UFS reset, GPIO IRQ operation, and suspend wake for GPIOs in `hawi_pdc_map[]`.
