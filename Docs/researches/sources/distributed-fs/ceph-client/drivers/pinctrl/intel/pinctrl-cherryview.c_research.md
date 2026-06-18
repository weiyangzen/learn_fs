# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-cherryview.c

## Purpose
Implements the Intel Cherryview/Braswell pinctrl and GPIO driver. It provides custom register access, pinmux, pinconf, GPIO, IRQ, ACPI OpRegion, DMI quirk, and noirq suspend/resume handling for Cherryview communities rather than relying solely on the shared Intel core operations.

## Important APIs, Types, and Functions
Register macros describe community interrupt registers and per-pad `CHV_PADCTRL0/1` fields. `struct intel_pad_context` stores saved pad registers; `struct intel_community_context` tracks interrupt-line mappings and saved masks. Static SoC data covers southwest, north, east, and southeast communities. Important helpers include `chv_pctrl_readl/writel()`, `chv_padreg()`, `chv_pinmux_set_mux()`, `chv_gpio_request_enable()`, `chv_config_get/set()`, GPIO callbacks, IRQ callbacks, `chv_gpio_set_intr_line()`, `chv_gpio_irq_handler()`, `chv_gpio_probe()`, ACPI address-space handler, `chv_pinctrl_probe/remove()`, and noirq PM callbacks.

## Control Flow
Probe selects SoC data from ACPI `INT33FF`, maps one MMIO resource, initializes interrupt-line context to invalid, registers pinctrl and gpiochip/irqchip, installs an ACPI address-space handler, and stores driver data. Pinmux refuses locked pads and otherwise writes PMODE/GPIOEN and optional OE inversion. GPIO request enables GPIO mode and clears stale interrupt routing unless locked. IRQ setup maps one of 16 hardware interrupt lines to GPIO offsets, working around shared or BIOS-assigned lines where possible. Suspend saves unlocked pad registers and INTMASK; resume masks interrupts, restores changed pads, clears status, and restores INTMASK.

## State and Persistence Behavior
Runtime state includes `struct intel_pinctrl`, cloned communities, `context.pads`, `context.communities[0].intr_lines`, saved interrupt mask, gpiochip, irqdomain, and a global `chv_lock`. Hardware retains pad mode, GPIO config, pull, open-drain, inversion, interrupt wake config, and interrupt mask/status. Writes are followed by readback for hardware erratum handling.

## Dependencies and Integration Points
Depends on ACPI, DMI, gpiolib, pinctrl, pinconf-generic, IRQ infrastructure, and shared Intel data types. It integrates with ACPI firmware both as a platform driver and via an installed MMIO OpRegion handler. DMI quirks preserve legacy IRQ numbering on selected Chromebooks.

## Risks
Locked pads can only be partially controlled, so ignoring lock checks can fail or corrupt firmware-owned configuration. Interrupt-line sharing and ACPI hardcoded IRQ numbers are board-sensitive. The write-readback sequence is required for Cherryview errata. DMI valid-mask quirks trade correctness for compatibility on known systems. Resume ordering must avoid unmasked interrupts while pad state is inconsistent.

## Test Signals
Probe on `INT33FF`, pinmux and GPIO requests on locked/unlocked pads, pull/open-drain config, GPIO value/direction operations, IRQ startup with BIOS default type, remapping shared interrupt lines, DMI quirk behavior, ACPI OpRegion reads/writes, noirq suspend/resume restore, spurious-interrupt suppression, and build/module unload are key signals.
