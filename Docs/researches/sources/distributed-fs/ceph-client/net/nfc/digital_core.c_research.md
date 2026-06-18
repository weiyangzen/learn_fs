# sources/distributed-fs/ceph-client/net/nfc/digital_core.c

## Purpose

`digital_core.c` is the framework glue for NFC Digital Protocol devices. It provides skb allocation and CRC helpers, serializes driver commands through workqueues, implements polling orchestration, exposes NFC core operations for digital devices, and allocates/registers/unregisters `struct nfc_digital_dev`.

## Important APIs, Types, and Functions

`struct digital_cmd` is the queued command object. Command helpers include `digital_send_cmd()`, `digital_wq_cmd()`, `digital_send_cmd_complete()`, and `digital_wq_cmd_complete()`. CRC helpers are `digital_skb_add_crc()` and `digital_skb_check_crc()`.

Polling and target setup use `digital_start_poll()`, `digital_stop_poll()`, `digital_poll_next_tech()`, `digital_wq_poll()`, `digital_add_poll_tech()`, and `digital_target_found()`. NFC core operation implementations include `digital_dev_up()`, `digital_dev_down()`, `digital_dep_link_up()`, `digital_dep_link_down()`, `digital_activate_target()`, `digital_deactivate_target()`, `digital_in_send()`, and `digital_tg_send()`.

Device APIs exported to drivers are `nfc_digital_allocate_device()`, `nfc_digital_free_device()`, `nfc_digital_register_device()`, and `nfc_digital_unregister_device()`.

## Control Flow

Drivers allocate a digital device with required `nfc_digital_ops`. The allocator validates callbacks, records capabilities, initializes command and poll work, maps supported NFC protocols, reserves extra head/tailroom for digital headers and CRC, allocates an NFC core device, and stores `ddev` as driver data.

Commands are queued by `digital_send_cmd()`. `digital_wq_cmd()` picks the first non-pending command, marks it pending, logs TX data, dispatches to the proper driver operation based on command type, and lets the driver complete asynchronously through `digital_send_cmd_complete()`. Completion schedules `digital_wq_cmd_complete()`, which removes the command, logs RX data, invokes the original digital callback, frees command resources, and schedules the next command.

Polling builds a randomized table of matching initiator and target technologies. `digital_wq_poll()` invokes the selected technology probe/listen function; failures call `digital_poll_next_tech()` to switch RF off, pick another technology, and reschedule after a short interval. `digital_target_found()` selects framing and CRC functions based on detected protocol and RF technology, configures hardware framing, clears polling count, and reports the target to NFC core.

Data exchange adds protocol-specific wrappers: NFC-DEP goes to `digital_in_send_dep_req()`, ISO-DEP pushes/pulls PCB bytes, other protocols add/check CRC and send a normal initiator command. Target mode sends DEP responses.

## State and Persistence Behavior

Persistent digital state includes command queue, command work items, polling technology table/index/count, current protocol, current RF technology, current NFC-DEP PNI, target FSC, selected CRC function pointers, and driver capability flags. `poll_tech_count` doubles as the active polling marker. Unregistration cancels work and flushes queued commands with `ERR_PTR(-ENODEV)` callbacks.

## Dependencies and Integration Points

The file integrates public NFC core operations with lower-level digital drivers through `struct nfc_digital_ops`. It depends on `digital_dep.c` for NFC-DEP and `digital_technology.c` for RF technology discovery and target listen flows.

## Risks and Edge Cases

The command queue assumes one active driver command at a time. A driver that fails to complete a command can stall the queue. Unregister must cancel work and call callbacks so owners can free buffers. Polling state is shared between workqueue callbacks and stop/unregister paths, so lock ordering around `poll_lock` matters. CRC function selection must match driver offload flags or frames will be rejected.

## Test Signals

Use a digital-capable NFC driver or simulator to exercise start/stop poll, RF cycling, technology fallback, target activation, transceive, target mode send, unregister during pending commands, and both CRC-offload and software-CRC modes.
