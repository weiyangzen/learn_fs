# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-qdu1000.c

## Purpose
This file describes the Qualcomm QDU1000 TLMM pin controller for the shared MSM pinctrl core. It provides the static pin inventory, mux functions, per-pin mux group table, special SD card groups, and QUP/I3C metadata for a large industrial/networking-oriented SoC. It binds to `qcom,qdu1000-tlmm` and uses a register base offset of `0x100000` for normal GPIO groups.

## Important APIs, Types, And Functions
The important data types are `struct pinctrl_pin_desc`, `struct pinfunction`, `struct msm_pingroup`, and `struct msm_pinctrl_soc_data`. `PINGROUP()` defines ordinary GPIO groups with ten function slots including GPIO mode, `REG_BASE + REG_SIZE * id` register placement, and the standard MSM TLMM GPIO/IRQ bit positions. `SDC_QDSD_PINGROUP()` describes the four fixed `sdc1_*` groups at the end of the table. `UFS_RESET()` exists in the file but the visible group table for this variant uses SD special groups, not a UFS reset group. `QUP_I3C()` is available for QUP I3C mode/offset metadata used by the common pinctrl code where matching function data is present.

## Control Flow
The module registers `qdu1000_tlmm_driver` at `arch_initcall()`. OF matching on `qcom,qdu1000-tlmm` invokes `qdu1000_tlmm_probe()`, which delegates directly to `msm_pinctrl_probe(pdev, &qdu1000_tlmm)`. The MSM core then consumes `.pins`, `.functions`, `.groups`, and `.ngpios = 151` to register pinctrl, pinmux, pinconf, GPIO, and irqchip interfaces. There are no local runtime callbacks beyond probe and driver unregister.

## State And Persistence
All pin data is immutable static storage. Runtime state, including selected muxes, bias, drive strength, GPIO direction/value, and interrupt configuration, is stored in TLMM hardware registers and managed by `pinctrl-msm.c`. The file has no wake IRQ map, so wake integration is limited to what the common core and platform interrupt wiring can infer without a GPIO-to-PDC table in this descriptor.

## Dependencies And Integration Points
The driver depends on OF platform matching and `pinctrl-msm.h`. It integrates with device tree pinctrl consumers for QUP serial engines, QSPI, qlink, Ethernet interrupt pins, PCIe clock request pins, PPS/GPS, debug/trace (`qdss_*`), SDHCI via `sdc1_*`, USB-related signals, and multiple timing/test functions. The `MODULE_DEVICE_TABLE(of, ...)` line provides module aliasing for the TLMM compatible.

## Risks And Test Signals
Most risk is table correctness: QDU1000 exposes many similarly named QUP, QSPI, qlink, DDR PXI, and debug functions, so copy/paste errors can silently route a signal to the wrong pad. The `.ngpios = 151` value excludes the special SD groups at indices 151-154; off-by-one mistakes here could expose non-GPIO pads as GPIOs. The `REG_BASE` offset must match the SoC memory map. Test signals include successful probe, pinctrl state selection for representative QUP/QSPI/qlink/SD consumers, gpiolib line count of 151, GPIO IRQ programming on normal pads, and SD card/eMMC signaling on the special `sdc1_*` groups.
