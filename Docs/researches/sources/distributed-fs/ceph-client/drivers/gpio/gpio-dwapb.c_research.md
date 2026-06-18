
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-dwapb.c

Purpose: implements Synopsys DesignWare APB GPIO for OF and ACPI systems, supporting multiple ports, optional shared or chained IRQ handling, debounce on port A, resets/clocks, register-layout variants, and suspend/resume context.

Important APIs/types/functions: `struct dwapb_gpio` owns the device, MMIO base, flags, reset, clocks, and flexible array of `struct dwapb_gpio_port`. `struct dwapb_context` stores suspend state. Important functions include `dwapb_gpio_get_pdata()`, `dwapb_gpio_add_port()`, `dwapb_configure_irqs()`, `dwapb_irq_set_type()`, `dwapb_do_irq()`, `dwapb_gpio_probe()`, `dwapb_gpio_suspend()`, and `dwapb_gpio_resume()`.

Control flow: probe parses child nodes into per-port properties, deasserts reset, maps registers, enables optional clocks, chooses v1/v2 register offsets, and registers each port through `gpio_generic_chip_init()`. Port A can configure IRQs; ACPI uses a shared requested IRQ while OF uses gpio_irq_chip parent handlers. The IRQ worker reads status, handles mapped GPIO IRQs, and toggles polarity for both-edge emulation. Suspend saves per-port data/direction/external and port-A IRQ/debounce state, masks non-wake IRQs, and disables clocks; resume reenables clocks and restores state.

State and persistence behavior: per-port contexts persist across system sleep. `ctx->wake_en` is updated by `irq_set_wake` and used during suspend masking. Generic-chip registers hold live GPIO state. Reset and clocks are devm-managed with cleanup actions.

Dependencies and integration points: depends on OF/ACPI firmware properties, gpiolib generic MMIO, reset framework, clk bulk APIs, IRQ core, and ACPI shared interrupt conventions. Compatible and ACPI IDs select register offset layout.

Risks: only port A supports interrupts/debounce. Both-edge handling toggles polarity based on current GPIO value and can miss rapid transitions. Child-node property correctness is critical. Shared ACPI IRQ handling must coexist with other devices on the line.

Test signals: multi-port DT parsing, v1/v2 register conversion, chained and shared IRQ modes, all supported trigger types, wake masking through suspend, debounce config on port A only, reset/clock error paths, and resume state restore.
