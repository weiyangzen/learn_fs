# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mlxbf.c

Purpose: provides GPIO support for first-generation Mellanox/NVIDIA BlueField platforms using a simple 64-bit memory-mapped register model.

Important APIs/types/functions: `struct mlxbf_gpio_state` wraps a `gpio_generic_chip`, MMIO base, and optional PM save area. Register constants cover pin state, input/output direction, scratchpad, and pad control words. `mlxbf_gpio_probe()` initializes the generic chip. `mlxbf_gpio_suspend()` and `mlxbf_gpio_resume()` save and restore scratchpad, four pad-control words, and direction registers when PM is enabled.

Control flow: probe allocates state, maps resource 0, configures `gpio_generic_chip_init()` with 8-byte accesses, data at `PIN_STATE`, output direction at `PIN_DIR_O`, and input direction at `PIN_DIR_I`, sets `ngpio = 54`, registers the chip, and stores drvdata. GPIO operations are handled entirely by the generic MMIO callbacks selected by the helper.

State and persistence behavior: hardware registers hold value and direction. Generic chip initialization snapshots data and direction shadow state. PM suspend stores selected 64-bit registers in `csave_regs`; resume writes them back. There is no IRQ support in this generation.

Dependencies and integration points: depends on platform resources, ACPI HID `MLNXBF02`, `gpio-mmio` generic chip helper, and 64-bit MMIO accessors. The driver is a module platform driver.

Risks: only a fixed set of pad-control registers is saved despite `pad_control[MLXBF_GPIO_NR]` being sized for 54 entries, so the array is larger than actual use. Any GPIO state outside the saved scratchpad/pad/direction registers is not restored. Generic helper constraints mean 8-byte width requires a 64-bit-capable build.

Test signals: ACPI/platform probe, 54-line registration, generic get/set/direction behavior against 64-bit registers, PM save/restore of scratchpad/pad control/direction registers, and no IRQ exposure.
