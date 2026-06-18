# sources/distributed-fs/ceph-client/drivers/net/can/softing/softing_fw.c

Purpose: firmware protocol and card-control implementation for Softing DPRAM CAN cards. It loads boot, loader, and application firmware, sends synchronous firmware commands, powers on chips, converts timestamps, and starts/stops card buses.

Important APIs/types/functions: `_softing_fct_cmd()` and `softing_fct_cmd()` implement firmware mailbox commands through DPRAM function parameters. `softing_bootloader_command()` sends bootloader commands. `fw_parse()` parses little-endian Softing structured binary records with checksum validation. `softing_load_fw()` writes boot/loader records directly to DPRAM and verifies readback. `softing_load_app_fw()` transfers app records through bootloader SRAM commands and checksum receipts. `softing_chip_poweron()` synchronizes and reads identity. `softing_raw2ktime()` converts card raw ticks. `softing_startstop()` performs the card-wide bus restart/start/stop sequence.

Control flow: firmware loading requests named files, validates a Softing header record, iterates data/start/eof records, writes data to DPRAM or bootloader staging, and verifies checksums/readback. Power-on sends sync vectors, resets chips, reads serial/version/license/chip IDs. Start/stop locks firmware state, stops queues for all relevant netdevs, closes active CAN devices, disables IRQ, resets chip, initializes one or both CAN chips with bittiming/filter/output settings, initializes interface/FIFOs/TX ACK, starts chips, initializes timestamps, reopens/wakes active buses, and re-enables IRQ. Failures shut down IRQs, reset chip, unlock, and close all netdevs.

State and persistence: updates `card->fw.up`, `card->id`, `card->ts_ref`, `card->ts_overflow`, card and per-bus TX counters, bus CAN states, and DPRAM mailbox/FIFO/control fields. Firmware files are external persistent inputs, but driver state is runtime only.

Dependencies/integration: Linux firmware loader, DPRAM I/O accessors/barriers, SocketCAN state helpers, Softing platform data firmware offsets/addresses, and `softing_main.c` IRQ/RX helpers.

Risks: firmware ABI is timing-sensitive; command polling timeouts and signal interruption can leave the card reset. `strncmp()` uses firmware-provided length for header comparison, so malformed short/long headers deserve attention. Starting one bus can restart the other because firmware control is card-wide. Error reporting command is disabled with `if (0 && error_reporting)`, so BERR reporting is intentionally not active despite ctrlmode. Timestamp overflow adjustment mutates `ts_ref` while converting.

Test signals: missing/corrupt firmware files; checksum mismatch; DPRAM readback failure; successful boot identity reads; start one bus then both buses; bus-off recovery through `CAN_MODE_START`; verify queues stop/wake and restart error frames on sibling bus.
