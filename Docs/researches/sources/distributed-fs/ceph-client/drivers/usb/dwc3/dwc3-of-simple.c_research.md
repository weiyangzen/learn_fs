# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-of-simple.c

Purpose: generic OF glue driver for simple DWC3 integrations that need only reset deassertion, bulk clock enablement, OF child population, and minimal PM handling. It covers Rockchip RK3399, Spreadtrum, Allwinner, HiSilicon, and Intel Keem Bay compatibles.

Important APIs, types, and functions: `struct dwc3_of_simple` stores device, bulk clock array, clock count, reset array, and a `need_reset` flag. `dwc3_of_simple_probe()` owns setup. `__dwc3_of_simple_teardown()` centralizes remove and shutdown cleanup. Runtime PM callbacks disable/enable clocks, while system sleep callbacks optionally assert/deassert resets for RK3399.

Control flow: probe allocates private state, marks RK3399 as needing reset toggles during system sleep, gets optional exclusive reset array, deasserts resets, gets all clocks, enables them, populates the DWC3 child, and enables runtime PM. Remove and shutdown depopulate children, disable and put clocks, assert and put resets, disable runtime PM, and mark the device suspended.

State and persistence: software state is limited to the reset and clock handles plus `need_reset`. Hardware state consists of reset deassertion and clocks being active. Runtime suspend gates clocks without unpreparing; runtime resume re-enables them. System sleep reset handling is conditional and does not restore additional registers.

Dependencies and integration: depends on OF, platform child population, reset controller arrays, bulk clock APIs, and runtime PM. It deliberately avoids SoC-specific register programming.

Risks: it is only appropriate for wrappers with no hidden register sequencing. The teardown helper is shared by remove and shutdown, so repeated or late calls must not race with child devices. `pm_runtime_get_sync()` result is not checked in probe, so unusual PM failures could go unnoticed.

Test signals: compatible-specific smoke tests should verify reset deassert, all-clock enablement, child DWC3 creation, runtime clock gating, RK3399 sleep reset toggling, shutdown cleanup, and probe deferral on clocks/resets.
