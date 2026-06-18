## sources/distributed-fs/ceph-client/drivers/input/keyboard/mpr121_touchkey.c

Purpose: Freescale/NXP MPR121 capacitive touch-key driver. It configures up to 12 electrodes and reports touch/release bits as Linux keys, via IRQ or input polling.

Important APIs/types/functions: `struct mpr121_touchkey` stores client, input, cached status bits, keycount, and keycodes. `mpr121_phys_init()` writes thresholds, filter/AFE/autoconfig registers, and electrode enable. `mpr_touchkey_report()` reads status bytes, diffs against cached bits, and reports changed keys. `mpr_touchkey_probe()` handles regulator voltage, keycode properties, IRQ/poll setup, and input registration.

Control flow: probe enables `vdd` and reads voltage for autoconfig thresholds, reads `linux,keycodes`, configures input, initializes hardware, chooses IRQ or polling, and registers input. Runtime reads two status bytes, masks 12 touch bits, reports changes with `MSC_SCAN`, and updates cache. Suspend disables electrodes; resume re-enables `keycount` electrodes.

State/dependencies/integration: state is cached status bits and hardware electrode configuration. Dependencies are I2C SMBus, regulator voltage, firmware properties, optional IRQ, input polling, and PM.

Risks and test signals: the threshold initialization loop uses `i <= MPR121_MAX_KEY_COUNT`, which appears to program one more electrode threshold pair than the 12-key limit. Resume writes `keycount` without the quick-charge bit used at init. Test IRQ and polling modes, keycount zero/too large, voltage-derived autoconfig values, suspend/resume touch recovery, and I2C read/write failures.
