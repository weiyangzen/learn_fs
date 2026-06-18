# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/qmi.c

## Purpose

`qmi.c` implements the ath12k WLAN firmware QMI control plane. It defines QMI element-info schemas for WLFW messages, discovers firmware service arrival, advertises host/MLO capabilities, responds to firmware memory requests, downloads board/regdb/calibration data, supplies M3 and auxiliary microcode memory, starts/stops WLAN firmware mode, and processes asynchronous firmware-ready events through an ordered workqueue.

## Important APIs And Functions

- QMI schema tables (`qmi_wlanfw_*_ei`) define the wire encoding for host capability, PHY capability, indication registration, memory request/response, target capability, BDF download, M3/AUX info, WLAN config/mode/INI, and firmware-ready indications.
- `ath12k_qmi_init_service()` initializes the QMI handle, event list/lock/workqueue, and QRTR lookup for `service_ins_id`; `ath12k_qmi_deinit_service()` releases QMI and allocated firmware memory.
- `ath12k_qmi_event_server_arrive()` requests PHY capability, registers indications, blocks host-cap event processing until all devices in the hardware group are ready, then triggers host cap.
- `ath12k_qmi_host_cap_send()` sends host memory mode, BDF/M3/calibration support, feature bitmap, internal sleep clock flags, and MLO chip/link metadata.
- `ath12k_qmi_msg_mem_request_cb()` parses firmware memory requests, allocates or maps target memory, then posts `REQUEST_MEM`; `ath12k_qmi_respond_fw_mem_request()` replies with physical addresses.
- `ath12k_qmi_event_load_bdf()` requests target capabilities, downloads regdb and board data, optional calibration, M3, and optional AUX microcode.
- `ath12k_qmi_firmware_start()` sends WLAN INI, CE/service/shadow register config, then mode; `ath12k_qmi_firmware_stop()` sends mode off.

## Control Flow

QMI callbacks are thin and asynchronous: QRTR new-server and firmware indications post `ath12k_qmi_driver_event` entries to an ordered workqueue. The workqueue ignores events during unregistering and otherwise dispatches server arrival, memory request, firmware-memory-ready, firmware-ready, and host-cap events. Firmware boot sequencing is therefore: service arrival, PHY cap, indication registration, grouped host-cap gating, firmware memory request, host memory response, firmware memory ready, target-cap/BDF/regdb/cal/M3/AUX download, firmware ready, and finally `ath12k_core_qmi_firmware_ready()`.

## State And Persistence

All state is in memory under `struct ath12k_qmi`: QRTR socket address, event queue, CE config, target memory chunks, target info, M3/AUX buffers, memory mode, calibration done, service instance, and device memory descriptors. MLO global memory is shared through `ath12k_hw_group::mlo_mem` under the group mutex and can be reset when no devices are started. DMA allocations are reused across recovery/resume when sizes match; fixed memory regions are ioremapped reserved memory.

## Dependencies And Integration

The file depends on Linux QMI/QRTR, firmware loader, DMA coherent memory, reserved memory/OF/ACPI/SMBIOS helpers, ELF detection, workqueues, and ath12k core/HIF/QMI headers. PCI initializes QMI CE config and unique service instance. Core firmware startup waits on QMI events. Board/regdb/calibration download integrates with ath12k firmware APIs.

## Risks And Test Signals

Risks include QMI ABI table mismatches, firmware memory segment overflows, delayed allocation handling for large contiguous DMA requests, MLO host-cap gating deadlocks, service instance collisions, missing cleanup of event workqueue on init failure, and partial boot failures leaving QMI fail flags. Test signals include QMI boot on every chip family, fixed and dynamic memory modes, large-memory retry path, multi-device MLO boot, regdb/BDF/calibration fallback paths, M3/AUX loading from bundled and legacy files, firmware-ready recovery path, service deletion/crash handling, and deinit leak checks.
