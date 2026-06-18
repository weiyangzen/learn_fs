# sources/distributed-fs/ceph-client/drivers/input/touchscreen/elo.c

Purpose: `elo.c` is a serio driver for several Elo serial touchscreen protocols: 10-byte standard E271-2210, 6-byte legacy E281A-4002, 4-byte legacy E271-140, and 3-byte legacy E261-280. It reports single-touch ABS coordinates, `BTN_TOUCH`, and optional pressure.

Important APIs, types, and functions: `struct elo` stores input/serio, a command mutex, command completion, protocol ID, packet parser state, expected packet type, checksum, data buffer, response buffer, and physical path. `elo_process_data_10()`, `elo_process_data_6()`, and `elo_process_data_3()` parse the three supported protocol families. `elo_command_10()` sends 10-byte protocol commands with lead byte and checksum, waits for response/ACK, and copies response data. `elo_setup_10()` queries controller identity and configures pressure capability/ranges. `elo_connect()` selects parser setup based on `serio->id.id`.

Control flow: connect allocates state/input, opens serio, and for ID 0 sends an identity command before registering input; legacy IDs configure fixed ranges directly. Runtime `elo_interrupt()` dispatches each byte to the parser for the selected protocol. The 10-byte parser verifies lead byte, checksum, and expected packet type, reports touch packets, completes ACKs, and stores command responses.

State and persistence: parser state persists across bytes; 10-byte command state is synchronized by `cmd_mutex`, `cmd_done`, `expected_packet`, and `response`. The driver does not persist settings on hardware.

Dependencies and integration points: it depends on serio protocol `SERIO_ELO`, input APIs, `serio_pause_rx` scoped guard for command setup, and external serial attachment.

Risks: older protocols have limited validation and no checksums. The 10-byte command path waits one second but does not inspect the timeout result directly; it infers failure from `expected_packet`. The connect comment incorrectly mentions Gunze. ABS ranges are hard-coded and may not match every panel.

Test signals: test each protocol ID, 10-byte checksum and unexpected packet handling, ACK/identity command completion, pressure-capable standard devices, legacy pressure byte handling, 3-byte touch polarity, connect failure cleanup, and serial resynchronization after bad bytes.
