# sources/distributed-fs/ceph-client/drivers/ipack/devices/ipoctal.h

Purpose: Provides shared IP-OCTAL constants and statistics structure for the serial driver.

Important APIs/types/functions: `NR_CHANNELS`, `IPOCTAL_MAX_BOARDS`, `MAX_DEVICES`, and `struct ipoctal_stats` with TX/RX/error counters.

Control flow: No executable flow. `ipoctal.c` uses the constants for TTY allocation and array sizing and uses `ipoctal_stats` for `TIOCGICOUNT` reporting.

State and persistence: `struct ipoctal_stats` is per-channel runtime state reset on close/free and incremented from IRQ paths.

Dependencies/integration: Header is local to the IP-OCTAL driver and complements SCC2698 register definitions.

Risks and test signals: Confirm the eight-channel constant matches board hardware, `MAX_DEVICES` aligns with tty minor allocation assumptions, and stats increments are safe under interrupt/TTY access patterns.
