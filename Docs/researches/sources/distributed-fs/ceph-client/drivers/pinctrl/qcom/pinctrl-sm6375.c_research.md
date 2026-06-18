# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm6375.c

## Purpose
Provides the Qualcomm SM6375 TLMM pin controller description for the shared `pinctrl-msm` core. The file is a SoC data table: it enumerates 164 pin descriptors, 157 GPIO-capable pins, 164 mux functions, GPIO/special pin groups, SD card and UFS reset register descriptions, wake IRQ mappings, and platform-driver binding for `qcom,sm6375-tlmm`.

## Important APIs, Types, and Functions
The main exported contract is `static const struct msm_pinctrl_soc_data sm6375_tlmm`, passed to `msm_pinctrl_probe()` by `sm6375_tlmm_probe()`. The local `PINGROUP()` macro builds `struct msm_pingroup` entries with mux, pull, drive, output-enable, input/output, interrupt, and EGPIO bit positions at `REG_SIZE * id` offsets. `SDC_PINGROUP()` describes non-GPIO SD controller pads with pull/drive fields but no mux or interrupt operations. `UFS_RESET()` describes the UFS reset output pad. `sm6375_mpm_map[]` maps GPIO numbers to MPM wake interrupt IDs. Module registration uses `platform_driver_register()` from `arch_initcall()` and unregisters in `module_exit()`.

## Control Flow
At early init, `sm6375_tlmm_init()` registers `sm6375_tlmm_driver`. A device-tree node with compatible `qcom,sm6375-tlmm` binds to `sm6375_tlmm_probe()`, which delegates all runtime behavior to `msm_pinctrl_probe(pdev, &sm6375_tlmm)`. After that, the shared Qualcomm pinctrl core uses these tables to register pinctrl groups/functions, GPIO chip behavior for `ngpios = 157`, and wake IRQ support. This source has no custom request, set_mux, GPIO, IRQ, suspend, or resume logic.

## State and Persistence Behavior
All SoC-specific state is static and read-only after module load: pin descriptors, pin-function names, per-pin group register offsets, wake IRQ map, and OF match metadata. Runtime mutable state lives in the common `pinctrl-msm` driver and hardware registers. Pad configuration persists only in TLMM hardware register state and may be restored by consumers, firmware, or the common core across boot and power-management flows; this file itself does not store configuration.

## Dependencies and Integration Points
Depends on Linux module, OF, platform-device infrastructure, and `drivers/pinctrl/qcom/pinctrl-msm.h`. It integrates with device tree through `qcom,sm6375-tlmm`, with the generic pinctrl and gpiolib APIs through `msm_pinctrl_probe()`, and with interrupt wake routing through the MPM map. Consumer nodes use the function and group names listed here, including QUP, CCI, camera clocks, display sync, QDSS, UIM, audio, USB PHY, SD card, and UFS reset functions.

## Risks
The file is table-driven and index-sensitive. Pin descriptor order, `DECLARE_MSM_GPIO_PINS()` coverage, `sm6375_groups[]` indices, `.ngpios`, and special pad numbers must stay aligned. The `PINGROUP()` macro sets EGPIO bits even though no `egpio_func` is provided in the SoC data, so changes around EGPIO handling should be checked against the shared core. SDC and UFS groups intentionally disable mux and IRQ fields with `-1`; using normal GPIO paths on those pads would be wrong. Wake IRQ map entries are hardware-specific and incorrect mappings can break suspend wake without affecting normal GPIO interrupts.

## Test Signals
Compile with the Qualcomm pinctrl core, boot with a `qcom,sm6375-tlmm` node, verify pinctrl groups/functions appear in debugfs, request representative GPIOs 0 through 156, configure pull/drive/output/input through gpiolib, exercise QUP/CCI/UIM/audio/display alternate functions from device tree, test UFS reset and SDC1/SDC2 pads, validate wake from suspend for mapped GPIOs, and confirm no consumers can request dummy or special groups as ordinary GPIOs.
