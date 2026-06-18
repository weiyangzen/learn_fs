# sources/distributed-fs/ceph-client/drivers/extcon/extcon-usb-gpio.c

## Purpose
Generic USB extcon provider backed by optional ID and VBUS GPIOs. It reports peripheral state as `EXTCON_USB` and host state as `EXTCON_USB_HOST`, enforcing that host mode wins when ID is grounded.

## Important APIs, Types, and Functions
`struct usb_extcon_info` stores device, extcon, optional GPIO descriptors, IRQ numbers, debounce delay, and delayed detection work. `usb_extcon_detect_cable()` samples GPIOs, applies fallback semantics when only one signal exists, clears stale extcon states, and publishes host or device state. `usb_irq_handler()` queues debounce work. Probe obtains GPIOs, registers extcon, configures hardware debounce or software debounce fallback, requests GPIO IRQs, enables wakeup capability, and performs initial detection. Remove cancels delayed work and disables wakeup.

## Control Flow
Probe requires an OF node and at least one of `id` or `vbus` GPIO. If ID is absent, ID defaults high; if VBUS is absent, VBUS defaults to ID, allowing ID-only setups to distinguish no host versus host. IRQs are edge-triggered and queue the delayed worker. The worker first clears USB_HOST if ID high and clears USB if VBUS low, then sets USB_HOST when ID low, otherwise sets USB if VBUS high. Suspend enables IRQ wake when allowed or selects pinctrl sleep state; resume restores pinctrl, disables wake, and queues immediate detection.

## State and Persistence
No explicit cable cache exists; state is derived from current GPIO levels. `debounce_jiffies` is nonzero only when GPIO hardware debounce fails. Extcon stores published state. Pinctrl sleep/default states may persist across PM transitions.

## Dependencies and Integration Points
Uses GPIO descriptor APIs, extcon provider, platform/OF matching, IRQ APIs, delayed work, pinctrl PM helpers, and device wakeup. Compatible string is `linux,extcon-usb-gpio`; platform ID is `extcon-usb-gpio`.

## Risks
When both GPIOs exist, hardware debounce setup for VBUS only occurs if ID debounce succeeded because of `if (!ret && info->vbus_gpiod)`. If hardware debounce fails, software debounce is used, but only one shared delay is tracked. GPIO polarity is defined by descriptor flags in firmware; wrong polarity reverses role detection. Host and device state changes are split into multiple extcon sync calls, so observers may see transient clearing before setting.

## Test Signals
Test ID-only, VBUS-only, and both-GPIO configurations; ID low with VBUS high/low; ID high with VBUS high/low; hardware debounce success/failure; suspend/resume wake handling; pinctrl transitions; remove cancellation; and GPIO polarity from DT flags.
