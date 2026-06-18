<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/common.c -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/common.c

## Purpose
Platform driver and shared controller layer for Renesas USBHS. It owns MMIO helpers, power/clock/reset setup, OF matching, hotplug role switching, runtime power policy, control-request helpers, bus reset/SOF, and PM suspend/resume.

## Important APIs, Types, And Functions
Register helpers are `usbhs_read()`, `usbhs_write()`, and `usbhs_bset()`. System helpers are `usbhs_sys_host_ctrl()`, `usbhs_sys_function_ctrl()`, `usbhs_sys_function_pullup()`, and `usbhs_sys_set_test_mode()`. Bus/control helpers include `usbhs_usbreq_get_val()`, `usbhs_usbreq_set_val()`, `usbhs_bus_send_reset()`, `usbhs_bus_send_sof_enable()`, `usbhs_bus_get_speed()`, `usbhs_vbus_ctrl()`, `usbhs_set_device_config()`, and `usbhs_xxxsts_clear()`. `usbhs_probe()` and `usbhs_remove()` own lifecycle; `usbhsc_hotplug()` owns role changes; `usbhsc_power_ctrl()` combines PM runtime, clocks, platform power, and SCKE.

## Control Flow
Probe resolves platform info, maps MMIO, gets IRQ/extcon/resets/clocks, patches default pipe and timing parameters, powers/clocks hardware temporarily, probes pipe/FIFO/mod subsystems, deasserts resets, calls hardware init, resets PHY, drops temporary power, selects autonomy or non-autonomy hotplug, and schedules cold-plug detection. Hotplug starts host/gadget when VBUS is present and stops/powers off/reset PHY when absent.

## State And Persistence
`usbhs_priv` stores MMIO base, IRQ, callbacks, driver parameters, delayed work, platform device, extcon, lock, mod/pipe/FIFO state, PHY, resets, and clocks. Hardware state includes SYSCFG, DVSTCTR, DEVADDn, interrupt registers, and SoC-specific registers.

## Dependencies And Integration Points
Binds Renesas/R-Car/RZ compatibles to platform-info objects. Integrates with platform driver, reset, clk, PM runtime, extcon, GPIO, generic PHY callbacks, and internal mode/pipe/FIFO layers.

## Risks
Power ordering is delicate, especially the probe temporary-enable phase and runtime power-control handoff. `usbhsc_power_ctrl()` can silently return after clock-enable failure. Hotplug rejects role mismatches from extcon. IRQ is explicitly freed before module removal to avoid UAF.

## Test Signals
Cold/hot plug, autonomy and runtime power modes, extcon mismatch, multi-clock DTs, reset failures, suspend/resume connected/disconnected, VBUS callbacks, and compatible match coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/common.c -->
