# sources/distributed-fs/ceph-client/drivers/power/supply/ab8500_charger.c

## Purpose
`ab8500_charger.c` is the AB8500/AB8505 charger-management driver. It exposes AC and USB charger power supplies, controls charger voltage/current registers, handles charger watchdogs and AB8500 hardware errata, and acts as the component master for the AB8500 battery-management stack (`ab8500_fg`, `ab8500_btemp`, and `ab8500_chargalg`).

## Important APIs, Types, And Functions
- `struct ab8500_charger` is the central runtime state: AB8500 parent, ADC channels, VDDADC regulator, AC/USB `ux500_charger` instances, charger flags, USB notifier state, workqueue, locks, and delayed works.
- `struct ab8500_charger_info` stores per-source connection, online, measured voltage/current, CV state, and watchdog-expired state.
- `ab8500_charger_ac_en()` and `ab8500_charger_usb_en()` are the `ux500_charger` enable callbacks used by the charge algorithm. They validate requested voltage/current, set AB8500 registers, manage the LED, VDDADC regulator, and online state.
- `ab8500_charger_set_current()` steps current register values up/down to avoid supply or battery transients. `ab8500_charger_set_vbus_in_curr()` applies USB source, platform, USB-stack, and low-VBAT limits.
- `ab8500_charger_detect_chargers()`, `ab8500_charger_detect_usb_type()`, `ab8500_charger_read_usb_type()`, and `ab8500_charger_max_usb_curr()` detect AC/VBUS presence and map USB link status to allowed input current.
- `ab8500_charger_ac_get_property()` and `ab8500_charger_usb_get_property()` implement power-supply properties for health, present, online, voltage, current, CV state, and USB VBUS collapse.
- `ab8500_charger_probe()` allocates state, gets IIO ADCs and `vddadc`, registers power supplies, requests IRQs, parses battery-management data, registers the USB notifier, and creates the component-master match.
- `ab8500_charger_bind()` creates the ordered workqueue, performs startup charger detection, queues attach/type work, and binds the child battery-management components.

## Control Flow
Probe initializes hardware registers, power-supply descriptors, interrupts, USB notifier, and component matching. Binding creates the workqueue, detects already-present AC/USB sources, and binds the fuel gauge, battery-temperature, and charge-algorithm components.

AC plug/unplug IRQs queue `ac_work`, which re-reads charger status and updates the AC power supply. USB VBUS and USB-link IRQs queue USB detection work. USB link status is decoded into a maximum input current; unrecognized or ACA chargers may delay attach to allow enumeration. USB PHY notifier events update a temporary USB state/current, then delayed work applies configured/suspend/resume/reset behavior.

The charge algorithm calls the `ux500_charger` operations to enable/disable charging, kick the watchdog, re-check abnormal disable, or update output current. Enabling charging writes max voltage, input current, output current, and control registers. Disabling charging clears control/current registers, cancels voltage polling, and handles early AB8500 watchdog errata.

Periodic and delayed work handles VBAT threshold current reduction, hardware-failure recovery checks, USB charger-not-ok polling, thermal-protection status, VBUS drop-end retry, charger-attached debounce, and old AB8500 watchdog kicking.

## State And Persistence
Runtime state is in-memory only. Persistent hardware state is represented by AB8500 registers written during probe, enable/disable, watchdog, backup-battery setup, and USB-current-limit adjustment. `charger_connected`, `charger_online`, `wd_expired`, thermal/failure flags, USB input-current limits, `autopower`, and `vbus_detected` drive user-visible power-supply values. No file-backed persistence exists; suspend flushes/cancels work and resume reschedules needed recovery checks.

## Dependencies And Integration Points
The driver depends on ABX500/AB8500 MFD register access, IIO ADC channels (`main_charger_v`, `main_charger_c`, `vbus_v`, `usb_charger_c`), `vddadc` regulator, USB PHY notifier, platform IRQ names, OF compatible `stericsson,ab8500-charger`, `ab8500_bm_data`, and the `ux500_charger` API from AB8500 charge algorithm code. It supplies `ab8500_chargalg`, `ab8500_fg`, and `ab8500_btemp`, and it registers component drivers for the AB8500 battery-management stack.

## Risks
- `ab8500_charger_ac_check_enable()` calls `ab8500_charger_ac_en(&di->usb_chg, ...)`; the AC enable callback uses `to_ab8500_charger_ac_device_info()`, so passing the USB member can produce an invalid container pointer. This is a high-risk bug in the abnormal AC re-enable path.
- Hardware errata paths are complex: old AB8500 watchdog kicking, no-overshoot bits, VDDADC regulator behavior, invalid charger forcing, and VBUS collapse retry can regress if register ordering or delays change.
- Suspend returns `-EAGAIN` if current stepping is in progress; tests need to cover active step-up/step-down during PM.
- USB current limiting merges platform max, USB enumeration current, link-derived current, low-VBAT derating, and collapse-derived limits. Incorrect precedence can overdraw weak USB sources or undercharge.
- Many IRQ handlers defer state reads to workqueues. Race coverage matters around disconnect while enable, delayed attach, and queued VBUS drop-end work.

## Test Signals
- Probe on AB8500 and AB8505 variants should verify optional AC charger behavior, IIO channel acquisition, IRQ-name coverage, `ab8500_bm_of_probe()` parsing, and component binding.
- Exercise AC and USB plug/unplug IRQs, USB link-status changes, USB PHY current notifications, invalid charger states, ACA wait paths, and startup-with-VBUS-present.
- Validate power-supply properties for health, present, online, current/voltage, CV indicator, watchdog-expired, thermal, not-ok, and VBUS-collapse states.
- Test current stepping boundaries, low-VBAT USB derating around `VBAT_TRESH_IP_CUR_RED`, VBUS collapse retry, and disable paths.
- Suspend/resume tests should cover pending work, active current stepping, watchdog errata, main/USB hardware-failure flags, and VBUS drop-end recovery.
