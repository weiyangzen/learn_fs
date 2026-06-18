# Research: sources/distributed-fs/ceph-client/drivers/usb/common/usb-conn-gpio.c

Purpose: platform driver for GPIO-based USB connector detection. It reads optional ID and VBUS GPIOs, derives the current USB role, drives a USB role switch, optionally controls a VBUS regulator in host mode, and exposes charger online state through the power-supply class.

Important types and functions: `struct usb_conn_info` holds device state, IDA allocated charger ID, role switch, last role, optional regulator, delayed detection work, debounce, GPIO descriptors/IRQs, power-supply descriptor, and initial-detection flag. Key functions are `usb_conn_detect_cable`, `usb_conn_isr`, `usb_charger_get_property`, `usb_conn_psy_register`, `usb_conn_probe`, `usb_conn_remove`, `usb_conn_suspend`, and `usb_conn_resume`.

Control flow: probe gets optional `id` and `vbus` GPIOs and requires at least one. It configures hardware debounce where possible or falls back to delayed work, gets optional VBUS regulator, gets the role switch, registers a USB power supply, requests threaded IRQs on both GPIOs, marks wakeup capable, and queues initial detection. Detection maps GPIO levels to `USB_ROLE_HOST`, `USB_ROLE_DEVICE`, or `USB_ROLE_NONE`; host mode has priority over VBUS. It disables the regulator when leaving host, sets the role switch, enables VBUS regulator when entering host, updates `last_role`, and notifies power supply.

State and persistence: no persistence. Runtime state is kept in `usb_conn_info`; charger ID is allocated from a global IDA and freed on remove. Delayed work coalesces GPIO IRQ changes. Suspend either enables IRQ wake or disables IRQs and selects sleep pinctrl; resume reverses that and queues detection.

Dependencies and integration points: depends on GPIOLIB, IRQ, pinctrl PM, regulator, USB role switch, power supply, OF compatible `gpio-usb-b-connector`, IDA, and system power-efficient workqueue.

Risks: role derivation relies on board GPIO polarity being described correctly. If only one GPIO is present, the code synthesizes the missing signal (`ID=1` for VBUS-only, `VBUS=ID` for ID-only), which must match hardware intent. Regulator enable/disable errors are logged but `last_role` still changes. Repeated role warnings are suppressed only during initial detection. Remove must cancel work before freeing ID/regulator state.

Test signals: DT probe with ID-only, VBUS-only, and both GPIOs; IRQ edge role changes; debounce fallback path; regulator enable/disable in host transitions; power-supply `ONLINE`; suspend/resume with and without wakeup; remove during pending work.
