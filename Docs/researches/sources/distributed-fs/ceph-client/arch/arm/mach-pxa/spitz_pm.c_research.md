# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/spitz_pm.c

Purpose: model-specific SharpSL power-management data and GPIO callbacks for Spitz, Borzoi, and Akita.

Important APIs/types/functions: callbacks include `spitz_charger_init()`, `spitz_measure_temp()`, `spitz_charge()`, `spitz_discharge()`, `spitz_discharge1()`, `spitz_presuspend()`, `spitz_postsuspend()`, `spitz_should_wakeup()`, `spitz_charger_wakeup()`, and `spitzpm_read_devdata()`. It defines exported `spitz_pm_machinfo` and registers a `sharpsl-pm` platform device.

Control flow: module init allocates and registers `spitzpm_device` with `spitz_pm_machinfo`. The common PM driver calls this file to request GPIOs, toggle charge/discharge/temp-measure pins, configure wakeup edges before suspend, restore GPIO18 mux after resume, decide whether a wake should be honored, and read ADC/GPIO status selectors.

State and persistence: stores `spitz_last_ac_status` and original GPIO18 config. Mutates board GPIOs and PWER/PRER/PFER wake registers. No disk persistence.

Dependencies and integration points: depends on `spitz.h`, PXA registers, `sharpsl_pm.c`, MAX1111 ADC helper, GPIO APIs, and machine type checks.

Risks: charger thresholds and GPIO polarities are safety-critical. Wakeup policy depends on several raw PXA edge-detect bits and can either miss a real wake or resume spuriously. GPIO18 mux save/restore is fragile.

Test signals: AC/battery/fatal GPIO reads, ADC values for battery/temp/AC, charger LED/current flow, wake from On key/AC/SD/CF/lid, and suspend/resume GPIO mux restoration.
