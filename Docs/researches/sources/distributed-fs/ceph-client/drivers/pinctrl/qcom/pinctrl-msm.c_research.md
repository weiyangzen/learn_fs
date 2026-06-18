# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm.c

## Purpose
Implements the shared Qualcomm MSM/TLMM pinctrl, pinmux, pinconf, GPIO, IRQ, suspend/resume, and PS_HOLD reset/poweroff logic used by many SoC-specific table files. SoC files provide `struct msm_pinctrl_soc_data`; this core turns those tables into Linux pinctrl functions, a gpiochip, and an IRQ domain backed by TLMM registers.

## Important APIs, Types, And Functions
`struct msm_pinctrl` is the runtime device state: device handles, pinctrl descriptor, gpiochip, parent IRQ, SCM-routing flag, raw spinlock, IRQ state bitmaps, SoC data pointer, MMIO bases, and physical base addresses. `msm_pinctrl_probe()` is the exported entry point for SoC drivers. Pinctrl ops include group count/name/pins and generic DT mapping. Pinmux ops include strict muxing, GPIO request validation, mux programming, eGPIO handling, glitch avoidance when first returning an output pin to GPIO, and IRQ masking while muxed away. Pinconf ops translate generic bias, drive, open-drain, input/output enable, and output level settings into TLMM bitfields.

GPIO functions implement direction, get, set, and debugfs display. IRQ functions implement mask/unmask, enable/disable, ack/eoi, type programming, software dual-edge handling, wake setup, resource locking, affinity forwarding for wake parents, chained summary interrupt dispatch, and wake-parent child-to-parent mapping. PM helpers force sleep/default pinctrl states. PS_HOLD helpers register restart and poweroff when a SoC exposes a `ps_hold` function.

## Control Flow
Probe allocates `msm_pinctrl`, maps one or more MMIO tiles, detects the special IPQ8064 SCM interrupt-target path, registers restart/poweroff if `ps_hold` exists, gets the parent IRQ, registers the pinctrl device, adds all generic pinfunctions, and initializes the gpiochip/IRQ domain. Runtime pinctrl requests from device tree flow through generic maps into `msm_pinmux_set_mux()` and `msm_config_group_set()`. GPIO API calls go through gpiolib callbacks. GPIO IRQs arrive on the TLMM summary interrupt and `msm_gpio_irq_handler()` scans enabled GPIOs for status bits, except wake-parent lines can be handled through a PDC/MPM parent domain.

## State And Persistence
Driver state is in `struct msm_pinctrl` and hardware registers. The raw spinlock protects register read-modify-write sequences. Bitmaps track enabled IRQs, software dual-edge lines, wake-parent-skipped lines, IRQs disabled because mux moved away from GPIO, and pins that have already had first-GPIO output glitch avoidance. GPIO validity can come from SoC `reserved_gpios` or ACPI `gpios`. Suspend/resume does not save TLMM registers directly; it asks pinctrl to select sleep/default states.

## Dependencies And Integration Points
Depends on Linux pinctrl, pinmux, pinconf, gpiolib, irqchip/irqdomain, OF/platform resources, Qualcomm SCM for secure interrupt target writes on IPQ8064, Qualcomm IRQ wake-parent helpers, sys-off registration, and PM core. SoC-specific files must provide accurate group register offsets, bit positions, function arrays, GPIO counts, optional tile names, reserved GPIOs, wakeirq maps, and eGPIO metadata.

## Risks
This is high-impact shared code. Incorrect bit arithmetic can affect every Qualcomm TLMM user. IRQ handling is subtle: raw status handling differs for level versus edge interrupts, some hardware needs software both-edge emulation, and wake-parent lines bypass local TLMM handling. Muxing away from GPIO while an IRQ is configured requires disable/ack/reenable coordination to avoid spurious interrupts. `PIN_CONFIG_INPUT_ENABLE` intentionally preserves historical output-disable behavior despite generic pinconf documentation. PS_HOLD poweroff uses global `pm_power_off`, so multi-controller systems must not register conflicting handlers casually.

## Test Signals
Core test signals include probe/remove through representative SoC drivers, pinctrl state application from device tree, GPIO direction/value tests, pinconf readback for pull/drive/open-drain/output-level, edge/level/both-edge IRQ tests, mux-away-while-IRQ-active tests, wake-parent suspend/resume wake tests, debugfs state inspection, sleep/default state transitions, and restart/poweroff behavior on SoCs with `ps_hold`.
