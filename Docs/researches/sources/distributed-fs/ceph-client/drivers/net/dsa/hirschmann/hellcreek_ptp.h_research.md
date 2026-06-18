# sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/hellcreek_ptp.h

Purpose: this header defines the Hellcreek PTP register map, adjustment constants, overflow interval, exported PTP helpers, and container macros used by PTP, hwtstamp, and main switch code.

Important APIs, types, and functions: constants define the 7 ns maximum step, slow-offset resource limit, quarter-second overflow period, PTP settings/command/status/read/write/offset/drift/snapshot registers, and `STATUS_OUT` LED bits. Prototypes expose setup/free, raw PTP register read/write, and seconds reconstruction. Macros convert `ptp_clock_info`, delayed overflow work, and LED class devices back to `struct hellcreek`.

Control flow: `hellcreek_ptp.c` uses the constants to program the PHC and LEDs, while `hellcreek_hwtstamp.c` uses raw register helpers and `hellcreek_ptp_gettime_seconds()` for packet timestamps. `hellcreek.c` indirectly depends on the software time state for TAPRIO schedule start calculations.

State and persistence: the header stores no state, but defines persistent hardware clock and LED output registers and the policy that overflow maintenance runs four times per second.

Dependencies and integration points: it includes bit operations, PTP clock kernel types, and `hellcreek.h`. It is the local interface between the PHC implementation and the timestamping code.

Risks: constants encode assumptions about hardware step size, oscillator behavior, and available slow-offset resources. If overflow work is delayed beyond the hardware nanoseconds rollover window, seconds tracking can drift. Container macros require embedded struct names to remain stable.

Test signals: build/link across PTP and hwtstamp objects, register access at expected offsets, PHC adjustment limits, overflow worker cadence, LED status bit control, and timestamp seconds reconstruction through the exported helper.
