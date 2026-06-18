# sources/distributed-fs/ceph-client/drivers/macintosh/via-macii.c

Purpose: implements Mac II style ADB transport over VIA shift-register signaling for many m68k Mac II-class machines.

Important APIs and functions: `via_macii_driver` supplies unified ADB callbacks: `macii_probe()`, `macii_init()`, `macii_send_request()`, `macii_autopoll()`, `macii_poll()`, and `macii_reset_bus()`. `macii_start()` begins a transaction; `macii_interrupt()` is the byte-level ADB state machine; `macii_queue_poll()` prepends autopoll Talk Register 0 commands.

Control flow: probe selects machines with `MAC_ADB_II`. Init configures VIA direction/state and requests `IRQ_MAC_ADB`. Requests must be `ADB_PACKET` and are queued with interrupts disabled. The interrupt handler toggles VIA ADB state bits through command/even/odd phases, sends bytes, reads replies or unsolicited autopoll data, detects bus timeout and SRQ, completes current requests, and queues new autopolls when idle.

State and persistence: global VIA pointer, queue pointers, `macii_state`, reply buffer/pointer, reply length, status flags, last command/talk/poll commands, and autopoll device bitmask. No persistent storage.

Dependencies and integration: m68k Macintosh configuration, VIA registers from `asm/mac_via.h`, Mac interrupt numbers, unified ADB helpers/macros, and `adb_input()`.

Risks: it relies on precise VIA state-bit transitions and transceiver behavior. Autopoll assumes unprobed devices do not assert SRQ. Static poll request reuse is safe only because it is queued in a controlled idle path. Buffer length is limited to 16 bytes. Local IRQ disabling serializes queue/state but makes long protocol handling latency-sensitive.

Test signals: Mac II ADB detection, request completion with and without replies, bus reset low-time delay, autopoll device rotation, SRQ handling, timeout behavior, keyboard/mouse input delivery, and no corruption when a command collides with buffered autopoll data.
