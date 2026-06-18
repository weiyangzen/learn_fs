# sources/distributed-fs/ceph-client/drivers/input/keyboard/adp5588-keys.c

Purpose: supports ADP5588/ADP5587 I2C keypad and GPIO expander chips. It can operate as a matrix keypad, export unused pins as GPIOs, and optionally provide nested IRQs for GPIO events.

Important APIs/types/functions: `struct adp5588_kpad` stores I2C client, input, IRQ timing delay, matrix dimensions/keymap, unlock keys, GPIO-only mode, GPIO map, `gpio_chip`, cached GPIO registers, and a mutex. Core functions include I2C `adp5588_read/write`, GPIO operations, IRQ chip callbacks, `adp5588_gpio_add`, `adp5588_report_events`, `adp5588_thread_irq`, `adp5588_setup`, `adp5588_fw_parse`, `adp5588_probe`, remove, suspend, and resume.

Control flow: probe checks SMBus byte support, parses firmware matrix properties or marks GPIO-only mode, enables regulator, toggles optional reset GPIO, reads revision, registers input, configures keypad rows/columns/unlock keys, clears event FIFO/status, enables interrupts, exports unused pins as GPIOs, and requests a threaded IRQ when present. The hard IRQ timestamps arrival. The thread applies a silicon-revision delay if needed, reads interrupt status, drains key events, reports matrix keys or dispatches nested GPIO IRQs, syncs input, and clears status. GPIO operations update cached direction/output/pull registers under mutex and write through I2C.

State and persistence: keymap, matrix dimensions, unlock keys, cached GPIO direction/output/interrupt/pull registers, and IRQ masks persist in memory. Hardware configuration persists in chip registers until removal, reset, or power loss. Remove disables the main config register.

Dependencies and integration: depends on I2C SMBus, matrix keypad helpers, GPIO library, GPIO IRQ chip support, regulators, optional reset GPIO, pin config constants, PM sleep hooks, and input.

Risks: mixed keypad/GPIO mode has a broad surface: matrix pins must be excluded from GPIO export, nested IRQ mapping depends on `gpiomap`, and cached GPIO state must stay coherent with hardware. The pull-disable update path appears sensitive to bit operations. Early silicon delayed readout uses jiffies-derived delay converted into ktime/usleep logic. GPIO-only mode still registers an input device before setup is skipped.

Test signals: test keypad matrix events, GPIO get/set/direction/config, interrupt-controller mode with rising/falling nested IRQs, regulator/reset sequencing, early revision delayed readout, FIFO overflow logging, suspend/resume IRQ disable/enable, and GPIO-only firmware with no rows/columns.
