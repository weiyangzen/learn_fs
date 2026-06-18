# File Research: sources/cow-pools/bcachefs-tools/raid/raid.h

This is the public header for the RAID library used by bcachefs-tools. It defines supported modes, hard limits, initialization, parity generation, recovery, verification, and scan APIs.

Key definitions:
- `RAID_MODE_CAUCHY`: default mode, up to 6 parity blocks.
- `RAID_MODE_VANDERMONDE`: up to 3 parity blocks, useful on lower-end CPUs without SSSE3.
- `RAID_PARITY_MAX = 6`.
- `RAID_DATA_MAX = 251`.

Public API:
- `raid_init()` initializes function dispatch and default Cauchy mode.
- `raid_selftest()` runs a startup integrity test.
- `raid_mode()` changes the parity matrix mode for later calls.
- `raid_zero()` sets the required zero-filled recovery buffer.
- `raid_gen()` computes parity blocks.
- `raid_rec()` recovers data and/or parity failures.
- `raid_data()` recovers data failures only using specified parity blocks.
- `raid_check()` validates a suspected failure set using one extra parity.
- `raid_scan()` brute-force scans for failed blocks.

Important contract:
- Block sizes must be multiples of 64 bytes.
- Failure index arrays must be ordered.
- Recovery does not independently verify parity correctness unless `raid_check()`/`raid_scan()` is used.
