# sources/distributed-fs/ceph-client/drivers/extcon/extcon-qcom-spmi-misc.c

## Purpose
Qualcomm PM8941 SPMI MISC extcon provider for USB ID and VBUS detection. It is based on GPIO-style extcon logic but reads IRQ line levels through irqchip state rather than GPIO descriptors.

## Important APIs, Types, and Functions
`struct qcom_usb_extcon_info` contains extcon, optional ID/VBUS IRQs, debounce delay, and delayed detection work. `qcom_usb_extcon_detect_cable()` calls `irq_get_irqchip_state(..., IRQCHIP_STATE_LINE_LEVEL, ...)` for `usb_id` and `usb_vbus` IRQs, sets SuperSpeed properties when active, and publishes USB_HOST/USB states. `qcom_usb_irq_handler()` queues the debounce work. Probe allocates extcon, enables SuperSpeed property capability, obtains named optional IRQs, requests handlers, validates at least one source, initializes wakeup, and performs initial detection.

## Control Flow
After probe, each ID or VBUS edge queues one delayed work item after 5 ms. The worker independently samples line level for each configured IRQ. ID low means host and sets `EXTCON_USB_HOST`; VBUS high means peripheral and sets `EXTCON_USB`. Initial detection calls the worker body directly. Suspend/resume enable and disable wake on the configured IRQs if the device may wake the system.

## State and Persistence
No cached cable state is maintained. Every report is derived from current irqchip line levels. The extcon framework stores last published state/properties. There is no hardware register programming beyond IRQ wake toggling.

## Dependencies and Integration Points
Depends on platform IRQ resources named `usb_id` and/or `usb_vbus`, irqchip line-level support, extcon provider APIs, devm delayed work autocancel, and PM wakeup. Device matching is `qcom,pm8941-misc`.

## Risks
If the IRQ controller does not support line-level state queries, detection silently returns early. The worker returns immediately on the first failed source, so one broken IRQ can suppress the other source update. SuperSpeed properties are only set true on active states and are not explicitly cleared. Suspend/resume return only the last wake operation result, potentially hiding an earlier failure.

## Test Signals
Validate named IRQ discovery, line-level polarity for ID low and VBUS high, initial detection, debounce behavior, wake IRQ enable/disable, behavior with only one source configured, and failure injection for `irq_get_irqchip_state()`.
