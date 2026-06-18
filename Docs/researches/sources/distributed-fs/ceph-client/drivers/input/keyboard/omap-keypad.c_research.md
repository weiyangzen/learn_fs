## sources/distributed-fs/ceph-client/drivers/input/keyboard/omap-keypad.c

Purpose: legacy OMAP1 MPUIO keypad driver. It scans a platform-data-described matrix using OMAP1 I/O registers, tasklet processing, and a timer while keys remain down.

Important APIs/types/functions: file-static `keypad_state`, `kp_enable`, and `kp_cur_group` hold global scanner state. `struct omap_kp` stores input, timer, IRQ, dimensions, delay/debounce, and flexible keymap. `omap_kp_interrupt()` masks IRQ and schedules `kp_tasklet`; `omap_kp_tasklet()` scans, reports diffs, and manages polling; sysfs `enable` toggles IRQ.

Control flow: probe validates platform data, disables MPUIO keyboard interrupt, builds keymap, registers input, enables optional debouncing, scans initial state, requests IRQ, and unmasks keyboard interrupt. IRQs are masked immediately; the tasklet scans each column and reports changed keys. If any key remains down, a timer reschedules scans at 20 Hz; otherwise IRQs are unmasked and group filtering resets.

State/dependencies/integration: state is global, so the driver effectively assumes one keypad. Dependencies are OMAP1 MPUIO register access, platform data, tasklets, timer, input matrix helpers, and sysfs attribute groups.

Risks and test signals: global state and tasklet object are not per-device. Group filtering masks keys by `GROUP_MASK` and can suppress events outside the active group. Test enable sysfs races, timer release detection, platform-data validation, grouped keymaps, debounce register behavior, and remove path tasklet/timer shutdown.
