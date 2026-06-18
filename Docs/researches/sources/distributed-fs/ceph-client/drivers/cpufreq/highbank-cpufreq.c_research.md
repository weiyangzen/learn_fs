# sources/distributed-fs/ceph-client/drivers/cpufreq/highbank-cpufreq.c

Purpose: provides Calxeda Highbank/ECX-2000 voltage-change coordination for the generic `cpufreq-dt` driver. It registers a clock notifier that tells the EnergyCore Management Engine to adjust voltage before upward rate changes and after downward rate changes.

Important APIs and control flow: `hb_voltage_change()` sends a PL320 IPC message containing a CPUFreq change note and target frequency in MHz. `hb_cpufreq_clk_notify()` handles `PRE_RATE_CHANGE` for upward transitions and `POST_RATE_CHANGE` for downward transitions, retrying up to `HB_CPUFREQ_VOLT_RETRIES` before returning `NOTIFY_BAD`. Module init checks DT machine compatibility, gets CPU0 device/node and CPU clock, registers the notifier, and instantiates a `cpufreq-dt` platform device.

State and persistence behavior: static notifier block persists for module lifetime. There is no remove path shown; registered notifier and cpufreq-dt device are effectively boot/module lifetime resources.

Dependencies and integration points: depends on OF machine compatibles `calxeda,highbank` and `calxeda,ecx-2000`, CPU0 device DT node, common clock framework notifiers, PL320 IPC firmware interface, and `cpufreq-dt`.

Risks and test signals: risks include missing cleanup/unregister path, retry loops without delay, ignoring `platform_device_register_full()` return value, potential clock reference leak on successful notifier registration, voltage IPC failure blocking clock changes, and no handling for abort-rate-change notifications. Test signals include notifier registration on matching machines only, IPC messages before/after expected rate directions, `NOTIFY_BAD` on repeated ECME failure, successful cpufreq-dt instantiation, and stable CPU voltage during frequency transitions.
