# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-intel.c

## Purpose

`pinctrl-intel.c` is the shared runtime implementation for modern Intel GPIO/pinctrl controllers. SoC-specific files provide static or generated pin/group/community data; this file implements pinctrl, pinmux, pinconf, GPIO, IRQ, capability discovery, PWM probing, ACPI data selection, and suspend/resume behavior.

## Important APIs, Types, And Functions

Core exported APIs include `intel_pinctrl_probe()`, `intel_pinctrl_probe_by_hid()`, `intel_pinctrl_probe_by_uid()`, `intel_pinctrl_get_soc_data()`, `intel_get_community()`, `intel_gpio_add_pin_ranges()`, group/function query helpers, and `intel_pinctrl_pm_ops`. Internal helpers translate pins and GPIO offsets (`intel_gpio_to_pin()`, `intel_pin_to_gpio()`), locate pad registers (`intel_get_padcfg()`), check ownership and locks (`intel_pad_owned_by_host()`, `intel_pad_acpi_mode()`, `intel_pad_locked()`), configure muxes (`intel_pinmux_set_mux()`), set pinconf state, and dispatch GPIO IRQs.

## Control Flow

Probe allocates `struct intel_pinctrl`, copies SoC community templates, maps each community BAR, rejects absent devices whose revision reads all ones, discovers capabilities through revision and CAPLIST, computes `pad_regs` from `PADBAR`, normalizes pad groups by explicit GPP tables or fixed group size, probes optional LPSS PWM if advertised, obtains the platform IRQ, initializes PM context, registers pinctrl, registers the GPIO chip, and requests a shared interrupt.

GPIO requests enter through pinctrl/gpiolib callbacks. A GPIO request checks host ownership and pad lock state, preserves firmware GPIO settings when already in GPIO mode, or forces GPIO mode with RX enabled and TX/SCI/SMI/NMI routes disabled. Direction, value, pull bias, high impedance, and debounce operations update PADCFG registers under `raw_spinlock_t`. IRQ setup rejects ACPI-mode pads, puts pads into GPIO mode, programs RX event/inversion bits, masks/unmasks GPI_IE, clears GPI_IS, and dispatches pending enabled bits to the gpiochip IRQ domain.

## State And Persistence

Runtime state is in `struct intel_pinctrl`: device pointer, spinlock, pinctrl descriptor/device, gpiochip, SoC data pointer, copied communities with MMIO pointers, PM context, and parent IRQ. Suspend saves PADCFG0/1/2 only for kernel/userspace-owned pins or direct-IRQ pins, saves interrupt masks and host ownership registers, and masks interrupts on resume before restoring saved state. PADCFG0 restore masks out RX state because it is read-only/live input state.

## Dependencies And Integration Points

The file integrates with Linux pinctrl, pinmux, pinconf, gpiolib, irqchip, ACPI, platform resources, PM, and optional `PWM_LPSS`. SoC data comes from `pinctrl-intel.h` structures. Firmware state is respected through PAD_OWN, HOSTSW_OWN, and ACPI ownership logic. It also contains a direct-IRQ firmware workaround for systems that route GPIO input to IOxAPIC without normal GPIO IRQ ownership.

## Risks

Register programming is hardware-sensitive. Incorrect community data can make every helper operate on the wrong MMIO address. Lock and ownership checks intentionally return busy or unsupported for firmware-owned or locked pads; bypassing them would risk firmware conflicts. IRQ handling uses shared IRQ scanning across all pad groups, so status/enable offset errors can cause missed or spurious interrupts. Suspend/resume restore is selective to avoid clobbering BIOS-managed pins, but that means inactive pins intentionally are not restored.

## Test Signals

Strong signals include successful probe and gpiochip registration, correct debugfs ownership/lock/mode output, pinmux mode changes for SoC group tables, pinconf bias/debounce get/set, GPIO direction/value behavior, IRQ trigger type handling and shared IRQ dispatch, wake enable/disable calls, optional PWM registration when CAPLIST advertises it, and suspend/resume preservation of requested lines, IRQ lines, and direct-IRQ pins.
