# sources/distributed-fs/ceph-client/drivers/hwmon/coretemp.c

Purpose: Intel CPU digital thermal sensor hwmon driver. It creates per-package platform devices and per-package/per-core temperature sysfs attributes based on CPU hotplug state and MSR readings.

Important APIs, types, and functions: `temp_data` holds one package or core temperature source, cached temperature, TjMax, target CPU, MSR register, generated sysfs attributes, and update mutex. `platform_data` represents a physical package/die with hwmon device, package ID, online CPU mask, core `ida`, package data, and core data pointers. `get_tjmax()`, `adjust_tjmax()`, and `get_ttarget()` determine critical and target temperatures through MSRs, PCI/model tables, or `tjmax=` override. `create_core_attrs()` creates `tempN_label`, `crit_alarm`, `input`, `crit`, and optional `max` sysfs attributes. CPU hotplug callbacks add/remove or retarget core/package data.

Control flow: init checks Intel DTS CPU match, allocates a zone device array sized by packages times dies, creates platform devices for each zone, and registers CPU hotplug callbacks. On CPU online, it checks CPUID thermal sensor support and microcode errata, registers the package hwmon device if this is the first online CPU in the package, adds package temp if supported, and adds a core temp only if no sibling thread already represents that core. On CPU offline, it removes a core when the last sibling leaves or retargets reads to another sibling, and unregisters hwmon when the package is empty.

State and persistence: temperatures are cached per `temp_data` for one second. `tjmax` may be permanently cached when forced or derived heuristically; a zero `tjmax` means dynamic MSR TjMax remains available. Sysfs attributes are dynamically created and removed according to hotplug state. No hardware state is written.

Dependencies and integration points: depends on x86 CPU feature matching, MSR reads on target CPUs, topology package/die/core/sibling masks, CPU hotplug framework, platform devices, hwmon sysfs groups, PCI host bridge lookup for TjMax quirks, and housekeeping CPU isolation checks.

Risks: TjMax heuristics for old CPUs can be inaccurate, and the driver explicitly warns when using relative scales. Hotplug handling must avoid dangling sysfs attributes while retargeting sibling CPUs. `NUM_REAL_CORES` is a hardcoded allocation limit pending better topology information. Reads use `rdmsr_on_cpu()` in some paths without explicit error handling after initial validation. Isolated non-housekeeping CPUs are skipped, affecting visibility on tuned systems.

Test signals: test on Intel CPUs with and without package temperature support, SMT on/off, CPU online/offline cycles, suspend/resume frozen hotplug, forced `tjmax=` parameter, and older Atom/Core2 quirk paths. Verify sysfs numbering (`temp1` package, `core_id + 2` cores), `crit_alarm`, one-second cache, and removal when the last package CPU goes offline.
