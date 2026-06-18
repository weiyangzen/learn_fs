# sources/distributed-fs/ceph-client/drivers/media/cec/usb/rainshadow/rainshadow-cec.c

## Purpose
This driver supports RainShadow Tech HDMI CEC adapters over an ASCII serio protocol. It registers a CEC adapter and translates text commands/replies to CEC RX/TX events.

## Important APIs, Types, and Functions
`struct rain` stores device, serio, CEC adapter, command completion, worker, low-level character ring buffer, command parser buffer, command reply, and write mutex. Main functions are `rain_interrupt`, `rain_irq_work_handler`, `rain_process_msg`, `rain_send`, `rain_send_and_wait`, `rain_setup`, and CEC callbacks `rain_cec_adap_enable`, `rain_cec_adap_log_addr`, and `rain_cec_adap_transmit`.

## Control Flow
Serio connect allocates the adapter, opens serio, queries firmware/reply configuration, registers the adapter, and updates `dev`. Incoming characters are buffered in interrupt context and parsed in workqueue context. Commands start with `?`, end with CR, and either represent received/status CEC messages or synchronous setup replies. Transmit sends `!x...~` ASCII commands and completion is later reported by `STA` parser messages.

## State and Persistence
State is volatile: ring buffer indices, command parse state, latest command reply, and adapter state. The setup sends configuration/address commands but does not implement persistent storage management.

## Dependencies and Integration Points
The driver binds to `SERIO_RAINSHADOW_CEC`, uses CEC core with physical address and monitor-all capabilities, and relies on serio plus workqueues/completions.

## Risks and Test Signals
The ring buffer uses `& 0xff`, which assumes `DATA_SIZE == 256`; changes must preserve power-of-two sizing. ASCII parsing is permissive and maps unknown TX status to low-drive. Test buffer overflow, malformed hex, firmware setup failures, polling one-byte messages, logical address invalid mapping to unregistered, TX status mapping, and disconnect while commands are pending.
