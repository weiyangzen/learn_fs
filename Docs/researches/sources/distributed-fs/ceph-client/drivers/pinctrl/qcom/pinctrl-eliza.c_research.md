# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-eliza.c

## Purpose
Defines the QTI Eliza TLMM pin controller data for the shared MSM pinctrl core. It describes 186 pins/groups, including a UFS reset group, eGPIO-capable GPIO muxing, PDC wake interrupt mapping, and a modern 0x1000-per-GPIO register layout.

## Important APIs, Types, and Functions
Important objects include `eliza_pins[]`, per-GPIO pin arrays created by `DECLARE_MSM_GPIO_PINS`, `enum eliza_functions`, function group arrays, `eliza_functions[]`, `eliza_groups[]`, `eliza_pdc_map[]`, and `eliza_tlmm`. `PINGROUP()` provides 12 function slots: GPIO mode, ten named TLMM mux slots, and an eGPIO slot. It also records `egpio_present`, `egpio_enable`, wakeup bits, interrupt target value `3`, and per-group register offsets computed from `REG_SIZE * id`. `UFS_RESET()` models the reset pin as a non-interrupt group with output control only. `eliza_tlmm_probe()` calls `msm_pinctrl_probe()`.

## Control Flow
`arch_initcall(eliza_tlmm_init)` registers the `eliza-tlmm` platform driver. OF matching on `qcom,eliza-tlmm` invokes probe, which hands the static `eliza_tlmm` data to the common driver. The common driver then parses device-tree pin states and uses the group metadata to service pinmux, pinconf, GPIO, IRQ, wakeirq, and eGPIO requests.

## State and Persistence Behavior
No local mutable state is maintained. Persistent data is the static pin/function/group table and PDC wake map. Runtime state lives in the common MSM pinctrl device structures and in TLMM/PDC hardware registers. `.egpio_func = 11` marks the virtual eGPIO function number used by the common core to mux ownership away from TLMM when requested. The UFS reset group persists as hardware output state, not as a GPIO IRQ-capable line.

## Dependencies and Integration Points
Depends on `pinctrl-msm.h`, OF platform matching, the generic pinctrl framework, and the common Qualcomm GPIO/IRQ/wakeirq implementation. It integrates with Eliza board device trees, QUP serial engines, camera CCI/MCLK, display/HDMI/DP signals, PCIe clock requests, QSPI, UIM, USB, SDC, QDSS trace/debug pins, PDC wake interrupts, and UFS reset control.

## Risks
Function selector ordering is critical because `PINGROUP()` encodes hardware mux values by array index. eGPIO is represented as a virtual mux state, so `.egpio_func`, `egpio_present`, and `egpio_enable` must stay aligned with the common core expectations. Wake-capable GPIOs depend on `eliza_pdc_map[]`; stale GPIO-to-PDC mappings can break suspend wake without obvious pinmux errors. Non-GPIO UFS reset must not be treated like a normal interrupt-capable GPIO.

## Test Signals
Expected signals are successful binding to `qcom,eliza-tlmm`, debugfs showing 186 pins/groups and eGPIO-capable functions, pinctrl state resolution for QUP/camera/display/PCIe/QSPI/UIM/USB/SDC users, working UFS reset toggling, GPIO IRQ routing including wake from suspend for entries in `eliza_pdc_map[]`, and no invalid function selector warnings.
