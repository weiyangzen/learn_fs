<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cacheinfo.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cacheinfo.h

Purpose: Declares cacheinfo lifecycle hooks used by PowerPC sysfs and hotplug code.

Important APIs/types/functions: `cacheinfo_cpu_online()`, `cacheinfo_cpu_offline()`, `cacheinfo_teardown()`, and `cacheinfo_rebuild()`.

Control flow: External code calls online/offline hooks around CPU hotplug and teardown/rebuild around migration or suspend scenarios.

State and persistence: State is implemented in `cacheinfo.c`; this header exposes the interface.

Dependencies and integration points: Integrated with PowerPC CPU sysfs and hotplug paths.

Risks: Prototype mismatches break build or hotplug integration.

Test signals: PowerPC cacheinfo build and CPU hotplug/suspend sysfs tests.

Source read size: 13 lines, 425 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cacheinfo.h -->
