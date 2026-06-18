
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-brcmstb.c

Purpose: implements the Broadcom BRCMSTB UPG GPIO controller with multiple 32-line register banks, optional GPIO interrupt-controller support, and wake-capable suspend/shutdown behavior.

Important APIs/types/functions: `struct brcmstb_gpio_priv` owns the parent platform device, MMIO base, bank list, IRQ domain/chip, parent IRQs, wake IRQ, and suspend flag. `struct brcmstb_gpio_bank` wraps `struct gpio_generic_chip`, bank id, width, wake mask, and saved registers. Important functions are `brcmstb_gpio_probe()`, `brcmstb_gpio_irq_setup()`, `brcmstb_gpio_irq_bank_handler()`, `brcmstb_gpio_irq_set_type()`, `brcmstb_gpio_irq_set_wake()`, `brcmstb_gpio_suspend_noirq()`, `brcmstb_gpio_resume()`, and `brcmstb_gpio_remove()`.

Control flow: probe maps the register resource, validates the number of banks against `brcm,gpio-bank-widths`, creates one generic gpiochip per non-empty bank, masks stale interrupts, and then builds a linear IRQ domain if the DT node is an interrupt controller. IRQs are demuxed from the chained parent by scanning each bank's `GIO_STAT & GIO_MASK`, then `generic_handle_domain_irq()` is called with the global GPIO offset. Suspend saves all bank registers except status, masks everything except wake-enabled lines, and resume restores the saved bank state.

State and persistence behavior: persistent runtime state is hardware register state plus `wake_active`, `saved_regs`, `num_gpios`, and `suspended`. Shutdown deliberately leaves wake GPIO masks programmed for cold-boot wake. The driver uses generic-chip locking for register read-modify-write paths and stores bank list membership for IRQ mapping and removal.

Dependencies and integration points: integrates with gpiolib generic MMIO helpers, device tree GPIO translation, Linux IRQ domains/chained IRQs, PM wakeup APIs, and platform PM callbacks. It depends on `brcm,gpio-bank-widths`, optional `interrupt-controller`, and optional `wakeup-source`.

Risks: the source tree currently contains duplicated declarations around `brcmstb_gpio_irq_set_wake()` and `brcmstb_gpio_bank_save()`, which is a compile-time risk if not resolved elsewhere. Empty banks consume offset space, so DT bank-width correctness is critical. Wake handling depends on parent IRQ and wake IRQ ordering, and invalid-width banks still expose 32 logical offsets while warning for offsets beyond actual width.

Test signals: build coverage should catch duplicated declarations and type errors. Runtime signals include successful probe for mixed-width banks, correct `gpiod_to_irq()` mapping, interrupt type programming for level/rising/falling/both-edge cases, wake event generation from retained status bits, suspend/resume register restore, and removal disposing all IRQ mappings.
