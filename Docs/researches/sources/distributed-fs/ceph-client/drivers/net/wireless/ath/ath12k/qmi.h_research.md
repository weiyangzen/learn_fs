# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/qmi.h

## Purpose

`qmi.h` is the WLFW QMI ABI and state definition for ath12k. It defines message IDs, maximum payload sizes, firmware file types, memory-region types, event types, host capability structures, target capability structures, BDF/M3/AUX/WLAN config messages, and `struct ath12k_qmi`.

## Important APIs And Types

- Constants define WLFW service ID/version/instance IDs, response limits, timeout, data segment size, memory segment counts, BDF/caldb sizing, and firmware mode off.
- `enum ath12k_qmi_event_type` lists workqueue events for service arrival/exit, memory request, firmware memory ready, firmware ready, host cap, and legacy placeholders.
- `struct ath12k_qmi` stores QMI handle/socket, ordered event workqueue, event list/lock, CE config, target memory array, memory mode/delay flag, block-event flag, target info, M3/AUX memory, service instance, and device memory descriptors.
- QMI request/response structs mirror firmware ABI for host cap including MLO metadata, PHY cap, indication registration, memory request/response, target cap, BDF download, M3/AUX info, WLAN mode/config/INI.
- Inline helpers `ath12k_qmi_set_event_block()` and `ath12k_qmi_get_event_block()` enforce event-lock ownership.

## Control Flow And Integration

`qmi.c` uses these structures with `qmi_send_request()`, `qmi_txn_wait()`, and QMI indication decoding. PCI fills `ath12k_qmi_ce_cfg`; core calls init/deinit, firmware start/stop, resource free, host-cap trigger, and MLO memory reset. The structs are also used by firmware file loading, reserved-memory mapping, and multi-device MLO boot coordination.

## State And Persistence

The header defines state ownership. Target memory chunks may be DMA coherent allocations or fixed ioremaps; M3/AUX regions carry total and active sizes for reuse; target info caches firmware-reported chip, board, SoC, and build identifiers. State is transient and released during QMI deinit/resource free.

## Risks And Test Signals

Wire-ABI drift is the main risk: message IDs, max lengths, enum values, and struct fields must match firmware and QMI element tables in `qmi.c`. Array bounds such as max memory segments, MLO chips/links, and BDF data size are critical. Test signals include compile coverage, QMI transaction success across all request types, malformed/oversized indication handling, MLO boot, and firmware resource cleanup.
