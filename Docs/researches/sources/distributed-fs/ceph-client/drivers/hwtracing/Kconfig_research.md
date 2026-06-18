# sources/distributed-fs/ceph-client/drivers/hwtracing/Kconfig

## Purpose
This top-level Kconfig file creates the `HW tracing support` menu and includes hardware tracing subsystem Kconfig files for STM, Intel TH, and PTT.

## Important APIs, Types, And Functions
This is declarative Kconfig. It sources `drivers/hwtracing/stm/Kconfig`, `drivers/hwtracing/intel_th/Kconfig`, and `drivers/hwtracing/ptt/Kconfig`.

## Control Flow
When Kconfig processes this file, it opens a menu, sources the three tracing subsystem configurations, and closes the menu. It does not directly define a symbol.

## State And Persistence
Only build-time menu organization is affected. Runtime state is created by whichever sourced tracing drivers are enabled.

## Dependencies And Integration Points
It integrates with the broader drivers Kconfig hierarchy and delegates all actual symbol definitions to child Kconfig files.

## Risks
- CoreSight is not sourced here in this tree version, so it must be included elsewhere or it will be absent from the top-level hwtracing menu.
- A bad source path breaks Kconfig parsing for the whole menu.

## Test Signals
Run menuconfig/listnewconfig to confirm STM, Intel TH, and PTT options appear under hardware tracing support, and verify CoreSight inclusion from the expected parent if required by this source tree.
