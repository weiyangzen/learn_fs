# sources/distributed-fs/ceph-client/drivers/extcon/extcon-palmas.c

## Purpose
Palmas/TWL6035 USB transceiver extcon provider for USB VBUS and ID detection. It reports `EXTCON_USB` for peripheral/VBUS and `EXTCON_USB_HOST` for grounded ID, using either Palmas internal interrupt/status registers or optional GPIO-backed ID/VBUS inputs.

## Important APIs, Types, and Functions
The driver operates on `struct palmas_usb` defined by the Palmas MFD headers. `palmas_usb_wakeup()` programs USB wakeup comparator enable. `palmas_vbus_irq_handler()` reads `PALMAS_INT3_LINE_STATE` and updates USB peripheral state. `palmas_id_irq_handler()` reads ID latch/source registers and updates host state. `palmas_gpio_id_detect()` is the software-debounced GPIO ID worker. `palmas_enable_irq()` enables hardware comparators and performs initial internal detection. Probe parses DT/platform options, optional `id` and `vbus` GPIOs, allocates extcon, requests internal or GPIO IRQs, and runs initial detection.

## Control Flow
Probe selects detection sources: DT booleans enable internal ID/VBUS detection, but present GPIOs override the matching internal path. GPIO ID can use hardware debounce or software delayed work. Internal ID and VBUS paths request virtual IRQs from the Palmas regmap IRQ data; GPIO paths call `gpiod_to_irq()` and request threaded IRQs. After registration, `palmas_enable_irq()` enables VBUS and ID comparators, optionally invokes the VBUS handler immediately, sleeps for host cold-plug stabilization, and invokes the ID handler. Probe also invokes GPIO initial detection. Suspend enables wake on active IRQs; resume disables wake and rechecks GPIO-backed state.

## State and Persistence
`palmas_usb->linkstat` tracks disconnected, VBUS, or ID state to suppress duplicate VBUS and ID events. Register latch clears are written for ID ground/float transitions. GPIO detection does not update `linkstat` in `palmas_gpio_id_detect()`, so hardware and GPIO paths have different state caches. No file-backed persistence exists.

## Dependencies and Integration Points
Depends on Palmas MFD register helpers and IRQ data, extcon provider APIs, GPIO descriptor APIs, OF/platform data, delayed work, and PM wakeup. It stores the USB child in `palmas->usb` for MFD-level integration.

## Risks
The VBUS GPIO acquisition error message says "id gpio", which can mislead debugging. Internal and GPIO source selection is implicit: a GPIO disables the matching internal detection flag. VBUS GPIO handling remuxes GPIO1 as VBUSDET before requesting the GPIO IRQ, so board pinmux assumptions matter. Some `palmas_read()`/`palmas_write()` calls ignore return codes in IRQ paths. GPIO ID detection does not set `linkstat`, which may matter if configurations change or if mixed paths are used.

## Test Signals
Validate ID grounded/float and VBUS high/low transitions for both internal and GPIO-backed configurations. Confirm cold-plug detection after probe, wakeup IRQ enable/disable during suspend/resume, GPIO debounce fallback when `gpiod_set_debounce()` fails, and correct extcon mutual behavior for USB and USB_HOST.
