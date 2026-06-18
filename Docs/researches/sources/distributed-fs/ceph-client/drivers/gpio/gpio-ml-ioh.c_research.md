# sources/distributed-fs/ceph-client/drivers/gpio/gpio-ml-ioh.c

Purpose: supports the OKI/Rohm ML-IOH PCI GPIO controller, which exposes eight GPIO channels with different line counts and per-channel interrupt registers.

Important APIs/types/functions: `struct ioh_regs` models the register block, `struct ioh_gpio_reg_data` stores suspend state, and `struct ioh_gpio` is per-channel state with a `gpio_chip`, register base, IRQ base, and spinlock. GPIO callbacks are `ioh_gpio_get()`, `ioh_gpio_set()`, `ioh_gpio_direction_input()`, and `ioh_gpio_direction_output()`. IRQ callbacks include `ioh_irq_type()`, mask/unmask/enable/disable helpers, `ioh_gpio_handler()`, and `ioh_gpio_alloc_generic_chip()`.

Control flow: PCI probe enables the device, maps BAR1, allocates an array of eight `ioh_gpio` structures, initializes each channel's GPIO chip and registers it, then allocates a Linux IRQ range and generic irq_chip for each channel. A shared device IRQ dispatches through `ioh_gpio_handler()`, which scans all eight channels' status registers, clears active bits, and calls `generic_handle_irq()` on `irq_base + line`. Direction output sets the PM bit and writes PO; direction input clears the PM bit. IRQ type programming writes the packed mode fields in IM_0 or IM_1, clears pending status, unmasks, and enables the interrupt.

State and persistence behavior: runtime GPIO state lives in PO/PI/PM and interrupt registers. Suspend saves PO, PM, IEN, IMASK, IM_0, IM_1, and use-select registers for all channels, then resume resets the block via `srst` and restores those registers. Each channel has a spinlock, but suspend locks only the first channel's lock while saving/restoring the whole array.

Dependencies and integration points: integrates with PCI ID `PCI_VENDOR_ID_ROHM, 0x802E`, gpiolib, generic IRQ chips, and the PCI-managed MMIO helpers. `to_irq()` returns the preallocated per-channel Linux IRQ number.

Risks: eight GPIO chips share one MMIO block and parent IRQ; array-pointer arithmetic is used in save/restore and interrupt scanning, so allocation/layout assumptions are important. The interrupt handler calls `generic_handle_irq()` directly from a shared IRQ context. IRQ mode supports rising, falling, both, high, low, and probe but has no explicit validation for channel line bounds beyond generic chip masks. PM locking may not serialize against all per-channel locks.

Test signals: PCI probe should register eight chips with line counts `{6,12,16,16,15,16,16,12}`, allocate irq descriptors for each, program interrupt mode registers for each trigger type, dispatch shared IRQs by status bit, save/restore all channel registers across suspend/resume, and reject/handle probe failures in BAR mapping or IRQ allocation.
