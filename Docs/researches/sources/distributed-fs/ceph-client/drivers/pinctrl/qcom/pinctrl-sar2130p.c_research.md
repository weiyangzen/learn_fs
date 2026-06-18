# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sar2130p.c

## Purpose
This file is the Qualcomm SAR2130P TLMM descriptor for `pinctrl-msm`. It defines GPIO pins, functions, pin groups, SD card special pads, and a dense GPIO-to-PDC wake map for the `qcom,sar2130p-tlmm` compatible. The SoC has 156 GPIO-capable pads and four additional SD card groups in the group array.

## Important APIs, Types, And Functions
The driver uses the standard MSM pinctrl data types: `struct pinctrl_pin_desc`, `struct pinfunction`, `struct msm_pingroup`, `struct msm_gpio_wakeirq_map`, and `struct msm_pinctrl_soc_data`. `PINGROUP()` supplies ten mux slots including GPIO, standard GPIO register offsets at `REG_SIZE * id`, eGPIO present/enable bit locations, and interrupt field positions with `intr_target_kpss_val = 4`. `SDC_QDSD_PINGROUP()` describes the `sdc1_rclk`, `sdc1_clk`, `sdc1_cmd`, and `sdc1_data` fixed-function groups. `sar2130p_tlmm_probe()` is the only local probe function and simply delegates to `msm_pinctrl_probe()`.

## Control Flow
During `arch_initcall()`, `sar2130p_tlmm_init()` registers `sar2130p-tlmm`. OF matching uses `qcom,sar2130p-tlmm`, with `.data = &sar2130p_tlmm` in the match entry, although the probe passes the same static object directly. Once probed, pinctrl, pinmux, pinconf, GPIO, and IRQ behavior is entirely driven by the common MSM core using the SAR2130P tables. Exit unregisters the platform driver.

## State And Persistence
There is no dynamic state in this file. Static tables persist for the lifetime of the module or built-in driver. Runtime pin, GPIO, and interrupt state persists in TLMM/PDC hardware and is modified by the common core. The wake map defines which GPIOs can be translated to PDC wake interrupts during suspend.

## Dependencies And Integration Points
The file depends on OF platform driver infrastructure and `pinctrl-msm.h`. Its function table integrates pinctrl states for QUP instances, CCI I2C, QDSS trace/debug, USB PHY/test pins, display hotplug, audio/I2S, phase flags, GCC test clocks, and SDHCI through the fixed SD card groups. The wake map integrates with the Qualcomm PDC wake IRQ mechanism used by suspend/resume.

## Risks And Test Signals
Risks are dominated by table accuracy. SAR2130P has many numbered phase flags and QDSS GPIO functions; a function/group mismatch can be hard to detect unless that exact peripheral is enabled. The group array contains indices 156-159 for SD pads while `.ngpios = 156`, so GPIO exposure must stop before the SD special groups. The wake map is large and nonmonotonic, making suspend wake validation important. Test signals include successful probe on the compatible, `gpiochip` line count of 156, representative QUP/CCI/audio/display/USB pinctrl states, SD card pad configuration, GPIO IRQ operation, and suspend wake tests across several mapped GPIO ranges.
