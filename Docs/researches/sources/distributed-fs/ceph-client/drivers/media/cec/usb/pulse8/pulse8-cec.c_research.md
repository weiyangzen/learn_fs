# sources/distributed-fs/ceph-client/drivers/media/cec/usb/pulse8/pulse8-cec.c

## Purpose
This driver supports Pulse Eight HDMI CEC adapters over a serio serial protocol. It translates the Pulse8 framed byte protocol to Linux CEC adapter operations and can restore/write persistent dongle configuration.

## Important APIs, Types, and Functions
`struct pulse8` stores serio, CEC adapter, firmware version, ping/EEPROM work, IRQ/RX queues, TX work/message/status, command completion buffers, parser state, lock, and autonomous/config flags. Protocol helpers are `pulse8_send`, `pulse8_send_and_wait_once`, and `pulse8_send_and_wait`. CEC callbacks are `pulse8_cec_adap_enable`, `pulse8_cec_adap_log_addr`, `pulse8_cec_adap_transmit`, and `pulse8_cec_adap_free`.

## Control Flow
Serio connect allocates the adapter, opens serio, queries firmware and persistent configuration, registers the adapter, optionally restores persistent config, and starts periodic ping/EEPROM work. TX is asynchronous: the CEC transmit callback stores the message and schedules `tx_work`, which sends idle time, ACK polarity, and each byte with EOM markers. The interrupt parser handles escaped frames between `MSGSTART` and `MSGEND`, queues received CEC frames, captures command replies, and reports TX status through workqueue context.

## State and Persistence
Runtime state includes parser state, command reply data, queued RX messages, one pending TX message, and CEC config flags. Persistent dongle state can be read from firmware and written to EEPROM via `MSGCODE_WRITE_EEPROM` when `persistent_config` is enabled and configuration changed.

## Dependencies and Integration Points
The driver binds to `SERIO_PULSE8_CEC`, uses CEC core monitor/physical-address capabilities, serio, workqueues, completions, and module parameters `debug` and `persistent_config`.

## Risks and Test Signals
Risks include command/async frame interleaving, one-second command timeouts, TX work racing with disconnect, and broadcast NACK suppression. Firmware-version branches differ for HDMI version and auto-power commands. Test frame escaping, RX queue overflow, firmware <2 behavior, autonomous restore, EEPROM write scheduling, all TX failure codes, CEC logical address programming, and serio disconnect cleanup.
