# sources/distributed-fs/ceph-client/drivers/video/backlight/wm831x_bl.c

Purpose: Wolfson WM831x PMIC backlight driver. It controls a current sink and DC4 boost converter to drive LEDs, using board platform data for current limit and sink selection.

Important APIs/types/functions: `struct wm831x_backlight_data` stores parent PMIC, selected current-sink register, and current brightness. `wm831x_backlight_set()` handles brightness changes and power sequencing. Backlight ops include update and cached get-brightness. Probe validates `wm831x_backlight_pdata`, chooses max current index from `wm831x_isinkv_values`, configures DC4 feedback source under register unlock, registers the backlight, and bootstraps full brightness.

Control flow: when brightness transitions from zero to nonzero, the driver enables ISINK, enables DC4, writes current select, then asserts drive. When transitioning to zero, it disables DC4 before ISINK/drive. On error during a transition it attempts a safe shutdown. Probe disables DC4 before initial `backlight_update_status()` so the sequence starts cleanly.

State and persistence: `current_brightness` is the software cache returned by get-brightness. PMIC registers retain actual enable/current state.

Dependencies and integration: WM831x MFD core, platform data, WM831x regulator/current-sink constants, Linux backlight core suspend/resume.

Risks: no DT path; missing platform data prevents binding. Brightness values are raw current-select indexes rather than perceptual levels. Probe sets default brightness to the maximum supported current, which can be bright at boot. Tests should cover invalid sink/current limits, register unlock failure, power-up/down error unwinding, cached brightness, and DC4 feedback-source selection.
