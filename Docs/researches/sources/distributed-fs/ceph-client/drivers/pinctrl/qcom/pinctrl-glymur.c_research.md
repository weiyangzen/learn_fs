# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-glymur.c

## Purpose
Provides TLMM pinctrl data for QTI Glymur-family SoCs, including a Mahua variant that shares the pin/function/group tables but uses a different PDC wakeirq map. The file defines GPIO groups, UFS reset, SDC2 control groups, eGPIO support, and OF matching for both `qcom,glymur-tlmm` and `qcom,mahua-tlmm`.

## Important APIs, Types, and Functions
Core objects are `glymur_pins[]`, `enum glymur_functions`, function group arrays, `glymur_functions[]`, `glymur_groups[]`, `glymur_pdc_map[]`, `mahua_pdc_map[]`, `glymur_tlmm`, and `mahua_tlmm`. `PINGROUP()` records GPIO mux options, eGPIO bits, pull/drive/output fields, and IRQ/wakeup fields using `REG_SIZE * id` spacing. `SDC_QDSD_PINGROUP()` adds SDC2 clock, command, and data pinconf-only groups. `UFS_RESET()` adds an output-only UFS reset group. `glymur_tlmm_probe()` uses `of_device_get_match_data()` so the matching compatible chooses the correct `struct msm_pinctrl_soc_data`.

## Control Flow
The platform driver registers during `arch_initcall()`. On probe, the OF match entry supplies either `glymur_tlmm` or `mahua_tlmm`; a missing match data pointer returns `-ENODEV`. Valid probe data is passed to `msm_pinctrl_probe()`, after which common MSM code handles runtime pinctrl, GPIO, IRQ, wakeirq, and eGPIO behavior.

## State and Persistence Behavior
The file has no writable private state. Static tables persist in kernel memory, while actual pin state persists in TLMM registers and PDC wake routing. Glymur and Mahua share all pin and mux metadata but intentionally differ in wakeirq mappings, so wake state behavior is variant-specific despite a common group table. `.egpio_func = 11` identifies the virtual eGPIO function slot.

## Dependencies and Integration Points
Depends on OF match data, platform-driver registration, `pinctrl-msm.h`, and the common Qualcomm pinctrl implementation. It integrates with board DT compatibles, QUP serial engines, camera/CCI, display/eDP, audio I2S, PCIe, QSPI, USB debug/PHY sideband pins, SDC2, UFS reset, QDSS trace, WCN switch controls, PDC wake interrupts, and GPIO consumers.

## Risks
The dual-compatible design makes wakeirq-map selection the highest-risk area: using the Glymur map on Mahua or vice versa can produce broken or wrong wake sources while normal GPIO use still works. Table index drift is also hazardous because `eliza`/`hawi`-style eGPIO slot assumptions are reused here. The `.ngpios = 251` value excludes the UFS and SDC-only groups from GPIO export; changing it would misrepresent non-GPIO groups. The file contains many `msm_mux__` placeholder uses, so generated names and placeholder enum entries must remain consistent.

## Test Signals
Test both compatibles. Probe should pick non-null match data, debugfs should expose the expected GPIO count plus UFS/SDC pinctrl-only groups, and DT states should resolve for QUP, display, camera, PCIe, USB, QSPI, SDC2, and UFS reset. Suspend/resume wake testing should cover GPIOs present in both `glymur_pdc_map[]` and `mahua_pdc_map[]`, especially entries that differ between variants.
