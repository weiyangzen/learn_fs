<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/of_rtc.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/of_rtc.c

Purpose: Instantiates legacy MMIO RTC platform devices from device-tree compatible strings.

Important APIs/types/functions: Provides `of_instantiate_rtc()` and static mapping table from `ds1743-nvram` to platform device name `rtc-ds1742`.

Control flow: Iterates each table entry and compatible node, allocates a resource, translates the first address range, logs the device, and registers a simple platform device with that resource.

State and persistence: No global state. Registered platform devices and allocated resources persist for the device lifetime.

Dependencies and integration points: Depends on OF compatible/address APIs and platform bus registration for RTC drivers.

Risks: If address translation fails after resource allocation, the resource is leaked. Device registration return value is not checked. The table is narrow and only covers DS1743-as-DS1742.

Test signals: Device-tree node instantiation, resource translation failure paths, platform driver binding to `rtc-ds1742`, and boot without matching RTC nodes.

Source read size: 59 lines, 1395 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/of_rtc.c -->
