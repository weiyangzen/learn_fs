# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mm-lantiq.c

Purpose: exposes output-only GPIO lines implemented by external latches attached to the Lantiq EBU memory bus.

Important APIs/types/functions: `struct ltq_mm` holds the `gpio_chip`, mapped latch address, and 16-bit shadow latch value. `ltq_mm_apply()` programs EBU timing/write-protect registers and writes the shadow value to the latch under the global `ebu_lock`. `ltq_mm_set()` updates one bit and applies it. `ltq_mm_dir_out()` aliases direction-output to set. `ltq_mm_save_regs()` configures the EBU address-select register.

Control flow: probe allocates state, initializes a 16-line dynamic-base GPIO chip with only output direction and set callbacks, maps the OF MMIO resource, programs EBU address selection, applies the initial zero shadow, then reads optional `lantiq,shadow` and stores it. Registration uses `devm_gpiochip_add_data()`.

State and persistence behavior: software shadow is the authoritative latch image; the hardware is write-only from the driver's perspective. The current code calls `ltq_mm_save_regs()` and applies before reading the optional shadow property, so a devicetree-provided shadow initializes the software cache after the first hardware write rather than being immediately applied. There is no suspend/resume hook.

Dependencies and integration points: depends on Lantiq SoC EBU helpers, global `ebu_lock`, OF compatible `lantiq,gpio-mm`, and memory-mapped latch wiring. It uses `subsys_initcall()` so latch GPIOs are available early.

Risks: no input/get support and no validation that consumers only request output behavior beyond missing callbacks. The optional shadow ordering may surprise boards expecting the property to set initial physical latch values at probe. EBU lock and timing writes can interfere with other EBU users if not kept serialized.

Test signals: OF probe, 16 output-only lines, latch writes under `ebu_lock`, EBU write-protect restore, `lantiq,shadow` behavior, and consumer attempts to use unsupported input/read operations.
