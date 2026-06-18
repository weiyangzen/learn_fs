# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8250.c

## Purpose
Describes the Qualcomm SM8250 TLMM/pinctrl hardware for the shared MSM pinctrl driver. It defines three tiles (`west`, `south`, `north`), 184 pin descriptors, 181 GPIO-capable lines, 115 mux functions, SDC2 and UFS reset special groups, PDC wake mappings, EGPIO metadata, and platform binding for `qcom,sm8250-pinctrl`.

## Important APIs, Types, and Functions
`sm8250_pinctrl` is the authoritative `struct msm_pinctrl_soc_data`. `PINGROUP()` builds tile-aware GPIO groups and includes both `.egpio_enable = 12` and `.egpio_present = 11`. `SDC_PINGROUP()` and `UFS_RESET()` create special non-GPIO groups. `sm8250_pdc_map[]` maps GPIOs to PDC wake IRQ IDs. `.egpio_func = 9` tells the shared core which mux slot corresponds to EGPIO-capable groups. `sm8250_pinctrl_probe()` delegates to `msm_pinctrl_probe()`, and module registration is done from `arch_initcall()`.

## Control Flow
Early boot registers `sm8250_pinctrl_driver`. Device-tree matching on `qcom,sm8250-pinctrl` calls probe, and probe hands the static SoC data to the common MSM pinctrl core. All later mux selection, pin configuration, GPIO operation, and IRQ handling is data-driven through the tables. The source has no custom SM8250 code paths after probe.

## State and Persistence Behavior
All SM8250-specific data is static after load. Runtime state lives in common-core allocations and TLMM registers. `.ngpios = 181` means descriptors beyond the GPIO range are not ordinary GPIO lines. EGPIO state is represented by the common core and hardware fields using the mux slot and EGPIO bit metadata supplied here.

## Dependencies and Integration Points
Uses Linux OF/platform/module support and `pinctrl-msm.h`. It integrates with device tree through `qcom,sm8250-pinctrl`, with PDC wake routing through `sm8250_pdc_map[]`, and with pinctrl consumers for QUP, QSPI, TSIF, PCIe, camera, CCI, display, audio/MI2S, LPASS slimbus, UIM, QDSS, USB PHY, SD card, UFS reset, and EGPIO-capable pads.

## Risks
The table is highly index-sensitive. A concrete consistency issue is visible in this source: pin descriptors label 180 as `SDC2_CLK`, 181 as `SDC2_CMD`, 182 as `SDC2_DATA`, and 183 as `UFS_RESET`, while the special pin arrays assign `ufs_reset_pins[] = { 180 }`, `sdc2_clk_pins[] = { 181 }`, `sdc2_cmd_pins[] = { 182 }`, and `sdc2_data_pins[] = { 183 }`. Any consumer of the descriptor names or group names should be checked for this mismatch. More generally, tile assignment, `.ngpios`, `.egpio_func`, and wake map entries can all fail at runtime without compile-time errors.

## Test Signals
Probe `qcom,sm8250-pinctrl`, inspect debugfs for pin names versus group membership around pins 180-183, verify GPIO operation for pins 0-180 as intended by `.ngpios`, test EGPIO muxing on groups whose ninth alternate function is `egpio`, exercise SDC2 and UFS reset pinctrl consumers, validate PDC wake from suspend on mapped GPIOs, and bring up representative QUP, PCIe, camera, display, USB, audio, and QDSS states across all three tiles.
