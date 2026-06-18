# sources/distributed-fs/ceph-client/drivers/input/misc/nxp-bbnsm-pwrkey.c

Purpose: reports the i.MX93 BBNSM power key as a configurable Linux key with wakeup and timer-based debounce/release polling.

Important APIs/types/functions: parent syscon regmap, timers, IRQ, PM wakeup/wakeirq, and input. `struct bbnsm_pwrkey` stores regmap, IRQ, keycode, keystate, suspend flag, timer, and input. Main routines are timer check, IRQ handler, probe, remove, suspend, and resume.

Control flow: probe gets the parent syscon regmap, reads `linux,code` default KEY_POWER, gets IRQ, enables BBNSM power/debounce control, clears stale events, sets up timer and input, registers timer cleanup, requests shared IRQ, registers input, and configures wake IRQ. IRQ filters for `BBNSM_BTN_OFF`, emits wakeup, synthesizes one press after resume if needed, starts debounce timer, clears event, and returns handled. Timer reads pressed state, reports changes, relaxes wakeup, and reschedules while held.

State/persistence: `keystate` suppresses duplicate reports; `suspended` gates post-resume synthetic press. Hardware event bits are cleared in probe/IRQ.

Dependencies/integration: compatible `nxp,imx93-bbnsm-pwrkey`, parent syscon, BUS_HOST input.

Risks: regmap errors are mostly ignored in IRQ/timer. Shared IRQ correctness depends on event filtering. Wake relaxation only occurs on timer state changes.

Test signals: custom/default keycode, event clearing, IRQ filtering, debounce/release reports, long-press timer reschedule, suspend/resume synthetic press, wake IRQ cleanup, and regmap failures.
