# sources/distributed-fs/ceph-client/drivers/gpio/gpio-zynq.c

## Purpose
Implements the Xilinx Zynq, ZynqMP, Versal, and PMC GPIO controller driver. It supports banked MMIO GPIO, per-bank interrupt handling, variant-specific bank layouts and quirks, runtime PM/clock management, wakeup, and suspend/resume context save.

## Important APIs, Types, And Functions
- `struct zynq_gpio` stores the gpiochip, MMIO base, clock, parent IRQ, platform data, saved register context, and direction spinlock.
- `struct zynq_platform_data` describes label, quirks, total line count, max bank, and logical bank min/max ranges.
- `zynq_gpio_get_bank_pin` maps logical GPIO numbers to hardware bank and bank-local pin, with Versal unused-bank skipping.
- GPIO callbacks `zynq_gpio_get_value`, `zynq_gpio_set_value`, `zynq_gpio_dir_in`, `zynq_gpio_dir_out`, and `zynq_gpio_get_direction` handle register access and variant quirks.
- IRQ callbacks `zynq_gpio_irq_mask`, `zynq_gpio_irq_unmask`, `zynq_gpio_irq_ack`, `zynq_gpio_irq_enable`, `zynq_gpio_set_irq_type`, `zynq_gpio_set_wake`, `zynq_gpio_irq_reqres`, and `zynq_gpio_irq_relres` implement per-line interrupt behavior.
- `zynq_gpio_irqhandler` scans bank interrupt status/mask registers and dispatches child IRQs.
- `zynq_gpio_save_context` and `zynq_gpio_restore_context` preserve data, direction, and interrupt configuration around suspend.

## Control Flow
Probe selects platform data from OF match, maps registers, obtains the parent IRQ and clock, initializes runtime PM, disables all interrupts in each active bank, sets up a chained gpio irqchip, registers the gpiochip, marks the parent IRQ disable-unlazy, enables device wakeup, and drops the runtime PM reference. GPIO set uses mask/data LSW/MSW write-only registers so only one pin changes. Direction-output sets direction and output-enable bits under lock before writing the value. IRQ type programming updates INT_TYPE, INT_POLARITY, and INT_ANY and switches the child irqchip/handler between level and edge descriptors. The chained handler reads each bank's pending enabled bits and dispatches child IRQs using logical bank offsets.

## State And Persistence
Hardware registers store data, direction, output enable, interrupt mask/status/type/polarity/any-edge state. Software context arrays save data mask registers, direction, interrupt mask, type, polarity, and any-edge state across non-wakeup suspend. Runtime PM manages the clock, and each requested GPIO/IRQ holds runtime PM references through request/free or IRQ resource callbacks.

## Dependencies And Integration Points
Depends on OF compatibles for Zynq, ZynqMP, Versal, and PMC variants, platform MMIO/IRQ/clock resources, gpiolib chained IRQ support, runtime PM, wakeup APIs, and Xilinx-specific bank-layout quirks including the data read-only bug.

## Risks And Edge Cases
Bank mapping is variant-specific and Versal skips unused hardware banks by mutating the loop index inside loops. Zynq bank 0 pins 7 and 8 cannot be inputs. The data read path has a quirk-dependent choice between DATA_RO and DATA registers. Suspend stores `INTMASK` but restore writes the complement to `INTEN`, so mask semantics must stay understood. Runtime PM references are held from both GPIO requests and IRQ resources. Edge interrupts use `handle_level_irq` after type setup, which is intentional for this controller but easy to misread.

## Test Signals
Validate every variant's total lines and bank min/max mapping, pins at bank boundaries, Zynq bank0 pin 7/8 input rejection, mask/data writes for lower and upper half pins, DATA_RO bug paths, all IRQ trigger types and handler switching, wake-enabled suspend paths, context save/restore, runtime PM request/free and IRQ resource balancing, and Versal unused-bank loops.
