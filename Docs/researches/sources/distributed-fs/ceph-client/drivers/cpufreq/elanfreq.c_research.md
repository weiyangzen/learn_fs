# sources/distributed-fs/ceph-client/drivers/cpufreq/elanfreq.c

Purpose: implements a legacy x86 CPUFreq driver for AMD Elan family SoCs by programming chip setup/control I/O ports for clock divider and hyperspeed modes.

Important APIs and control flow: `elanfreq_get_cpu_frequency()` reads indexed register `0x80` through ports `0x22/0x23`, decodes normal 1-33 MHz states and hyperspeed 66/99 MHz states, and returns the current frequency. `elanfreq_target()` disables hyperspeed, delays for pipeline cleanup, writes the selected CPU clock speed register value and PMU force-mode register value from `elan_multiplier`, then delays for settle. `elanfreq_cpu_init()` validates AMD family/model, initializes `max_freq` from current speed if unset, invalidates table entries above max, and attaches `elanfreq_table`. Built-in boot parameter parsing supports deprecated `elanfreq=`.

State and persistence behavior: static `max_freq`, multiplier table, and cpufreq table define available states. The target function persists hardware state in Elan internal registers. Invalidated table entries remain modified for the module lifetime.

Dependencies and integration points: depends on x86 CPU identification, legacy I/O port access, local IRQ disabling around register access, cpufreq generic table verification, and cpufreq core target-index notifications. The driver sets `CPUFREQ_NO_AUTO_DYNAMIC_SWITCHING`, so the core should fall back from dynamic governors.

Risks and test signals: risks include global mutation of the static frequency table, CPU0-only hardware assumptions, long IRQ-off and udelay sections, no explicit error checking for I/O writes, current-frequency fallback making maximum frequency depend on boot state, and deprecated boot-parameter behavior. Test signals include driver matching only AMD 486 model 10, correct current frequency decoding, table invalidation above `max_freq`, successful transitions to normal and hyperspeed states, and fallback to non-dynamic governor behavior.
