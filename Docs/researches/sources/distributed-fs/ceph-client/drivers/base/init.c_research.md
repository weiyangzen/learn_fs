# sources/distributed-fs/ceph-client/drivers/base/init.c

## Purpose
`init.c` orders early initialization of the Linux driver model and core pseudo-buses/devices.

## Important APIs, Types, And Functions
The only function is `driver_init()`. It calls initialization for noop backing device info, devtmpfs, devices, buses, classes, firmware, hypervisor, faux bus, Open Firmware core, software nodes, platform bus, auxiliary bus, memory, node, CPU, and container devices.

## Control Flow, State, And Persistence
`driver_init()` is called early from kernel init. It first initializes foundational pieces required by later device registration: backing info, devtmpfs, generic device/bus/class infrastructure, and top-level firmware/hypervisor kobjects. It then initializes higher-level core buses and device classes that depend on the core being present.

## Dependencies, Integration Points, Risks, And Test Signals
The file is an integration point rather than a feature body. Risks are ordering regressions: later init calls assume sysfs, buses, classes, devtmpfs, and top-level kobjects already exist. Test signals include boot smoke tests, initcall ordering checks, `/dev` population, platform/auxiliary bus availability, CPU and node sysfs presence, and failure injection in individual init routines where callers expect panic or propagated errors.
