# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mlxbf2.c

Purpose: supports NVIDIA/Mellanox BlueField-2 YU GPIO blocks, including GPIO value control, protected direction changes through a shared ARM GPIO lock register, optional interrupt support, and sleep PM hooks.

Important APIs/types/functions: `struct mlxbf2_gpio_context` holds a `gpio_generic_chip`, GPIO MMIO base, device pointer, and suspend context pointer. `struct mlxbf2_gpio_param` stores the shared `yu_arm_gpio_lock` mapping and mutex. Lock helpers `mlxbf2_gpio_get_lock_res()`, `mlxbf2_gpio_lock_acquire()`, and `mlxbf2_gpio_lock_release()` serialize protected mode changes. Direction callbacks program `YU_GPIO_MODE0/1` clear/set registers. IRQ callbacks implement enable/disable, type selection, handler, and print-chip.

Control flow: probe maps the GPIO block, maps the global lock resource once, reads optional `npins`, initializes a generic chip with DATAIN/DATASET/DATACLEAR, replaces direction callbacks with BlueField-specific lock-aware versions, optionally requests a shared parent IRQ, registers an immutable nested IRQ chip, then adds the gpiochip. Direction input acquires the global lock and generic chip lock, clears both MODE0 and MODE1 bits, and releases. Direction output clears MODE1 and sets MODE0. The IRQ handler reads cause/event-enable status, clears pending bits, and dispatches domain IRQs.

State and persistence behavior: GPIO data is in hardware data registers; direction mode is in MODE0/MODE1. IRQ desired trigger state is not shadowed except by hardware rise/fall enable registers. Sleep suspend/resume intends to save MODE0/MODE1 in `gs->csave_regs`.

Dependencies and integration points: depends on platform firmware with ACPI HID `MLNXBF22`, `gpio-mmio` generic helper, shared memory resource at `0x2801088`, gpiolib IRQ helpers, and optional `npins` device property for the last partial bank.

Risks: in this snapshot `gs->csave_regs` is dereferenced in suspend/resume but is not allocated in probe, so enabling PM can lead to a null-pointer crash. The lock acquire path returns `-EINVAL` if the hardware lock active bit is already set, which can make direction changes fail under firmware contention. `irq_set_type()` only ever sets requested rise/fall bits and does not clear disabled senses when changing type, so stale hardware enables should be checked. Direction output ignores the requested initial `value`; it only configures mode, relying on the generic output latch path elsewhere.

Test signals: probe on each GPIO block with and without IRQ, global lock mapping reuse across blocks, direction changes failing/succeeding based on lock state, edge IRQ configuration and dispatch, `npins` limiting the last bank, and PM suspend/resume with attention to the missing `csave_regs` allocation.
