<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/power/Kconfig

Purpose: Defines kernel power-management configuration options for suspend, hibernation, autosleep, wakelocks, PM QoS wakeup latency, PM debug/test features, APM emulation, generic PM domains, workqueue power efficiency, CPU PM, and the Energy Model framework.

Important APIs/types/functions: This is Kconfig data rather than C APIs. Key symbols include `SUSPEND`, `SUSPEND_FREEZER`, `SUSPEND_SKIP_SYNC`, `HIBERNATE_CALLBACKS`, `HIBERNATION`, `HIBERNATION_SNAPSHOT_DEV`, `HIBERNATION_COMP_LZO`, `HIBERNATION_COMP_LZ4`, `HIBERNATION_DEF_COMP`, `PM_STD_PARTITION`, `PM_SLEEP`, `PM_SLEEP_SMP`, `PM_AUTOSLEEP`, `PM_USERSPACE_AUTOSLEEP`, `PM_WAKELOCKS`, `PM_QOS_CPU_SYSTEM_WAKEUP`, `PM`, `PM_DEBUG`, `PM_ADVANCED_DEBUG`, `PM_TEST_SUSPEND`, `DPM_WATCHDOG`, `PM_TRACE`, `PM_TRACE_RTC`, `APM_EMULATION`, `PM_CLK`, `PM_GENERIC_DOMAINS`, `WQ_POWER_EFFICIENT_DEFAULT`, `CPU_PM`, and `ENERGY_MODEL`.

Control flow: Dependencies and selects determine build inclusion: suspend requires `ARCH_SUSPEND_POSSIBLE`; hibernation requires swap and arch support and selects callbacks/crypto; `PM_SLEEP` becomes true for suspend or hibernate callbacks and selects `PM`; SMP sleep selects hotplug CPU; autosleep/wakelocks depend on `PM_SLEEP`; Energy Model depends on CPU frequency or devfreq support.

State and persistence: Kconfig choices persist in the kernel build configuration and control compiled objects, defaults, boot/runtime sysfs defaults, and available kernel parameters. No runtime code is executed here.

Dependencies/integration: Drives `kernel/power/Makefile` object selection and many compile-time conditionals across PM, scheduler energy-aware scheduling, cpufreq/devfreq, freezer, pstore watchdog, RTC wakealarm test, ACPI/APM, and generic PM domains.

Risks: Option dependencies encode policy and safety tradeoffs. `PM_USERSPACE_AUTOSLEEP` explicitly warns about aggressive Android-style suspend behavior. `SUSPEND_SKIP_SYNC` changes default data-safety behavior. `PM_TRACE_RTC` intentionally corrupts RTC time for debugging. `DPM_WATCHDOG` can intentionally panic systems on suspend/resume stalls.

Test signals: Kconfig dependency resolution for minimal PM, suspend-only, hibernation-only, debug, Android autosleep, and Energy Model builds; object inclusion in Makefile; visibility/defaults in `olddefconfig`; and runtime presence of sysfs/debug features implied by selected options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/Kconfig -->
