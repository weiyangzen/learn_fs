# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sa8775p.c

## Purpose
This is the Qualcomm SA8775P TLMM pin controller data driver. It describes a 150-GPIO automotive SoC pin controller, including alternate functions for QUP, camera, display, audio, Ethernet/Sail, debug, test, and storage signals; eGPIO-capable pads; UFS reset; SD card pads; and a GPIO-to-PDC wake interrupt map. Probe delegates to the shared MSM pinctrl implementation.

## Important APIs, Types, And Functions
`PINGROUP()` defines the ordinary GPIO groups with ten function slots, `REG_BASE` of `0x100000`, `REG_SIZE` of `0x1000`, eGPIO presence/enable bits, and a four-bit interrupt target field (`intr_target_width = 4`). `SDC_QDSD_PINGROUP()` and `UFS_RESET()` describe nonstandard storage pads. The static arrays `sa8775p_pins`, `sa8775p_functions`, `sa8775p_groups`, and `sa8775p_pdc_map` are collected in `sa8775p_pinctrl`, where `.ngpios = 150`, `.wakeirq_map` is supplied, and `.egpio_func = 9` marks the mux index used for eGPIO on selected high-numbered pads.

## Control Flow
The driver is registered during `arch_initcall()` as `sa8775p-tlmm`. A matching DT node with `qcom,sa8775p-tlmm` calls `sa8775p_pinctrl_probe()`, which passes the static descriptor to `msm_pinctrl_probe()`. All operations after probe use the MSM common path: pin group enumeration, mux function lookup, pin configuration register writes, GPIO chip operations, irqchip setup, and wake IRQ translation through the PDC map. Module exit unregisters the platform driver.

## State And Persistence
The file carries no mutable local state. Static tables persist for the module lifetime. Hardware state persists in TLMM registers and PDC wake configuration until reset or reprogramming by the common core. eGPIO status is represented through the eGPIO bit fields in each group and the `.egpio_func` index. Wake state depends entirely on the static map from GPIO numbers to PDC interrupt numbers.

## Dependencies And Integration Points
The driver depends on Linux OF/platform infrastructure and `pinctrl-msm.h`. It integrates with DT pinctrl consumers for QUP serial engines, camera CCI/MCLK, display hotplug and vsync, MI2S/audio, SAIL/EMAC/OSPI/SGMII signals, trace/debug signals, USB test pins, UFS reset, and SDHCI. It also integrates with suspend wake through the `sa8775p_pdc_map`.

## Risks And Test Signals
This file is data-heavy and regression-prone. The four-bit interrupt target width is a notable SoC-specific detail; omitting it would target interrupts incorrectly. The eGPIO block covers pads 126-148 plus selected debug behavior and must match hardware mux numbering. `.ngpios = 150` separates GPIO-capable pads from UFS/SD special groups. Wake tests should cover mapped and unmapped GPIOs because normal GPIO IRQs can work even when PDC wake mapping is wrong. Test signals include probe and GPIO count, pinctrl state application for QUP/camera/display/audio/storage/Ethernet consumers, UFS reset behavior at `0x1a2000`, SD `sdc1_*` drive/pull configuration, GPIO IRQ handling, and suspend wake from representative PDC-mapped GPIOs.
