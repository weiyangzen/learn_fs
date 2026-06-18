# File Research: sources/block-storage/util-linux/sys-utils/hwclock.c

Purpose: Implements the main `hwclock(8)` utility: reading, setting, adjusting, predicting, and synchronizing hardware and system clocks.

Core behavior:
- Defaults to `--show`, and supports `--get`, `--set --date`, `--hctosys`, `--systohc`, `--systz`, `--adjust`, `--predict --date`, Linux RTC parameters, voltage-low operations, Alpha epoch operations, testing mode, alternate adjtime/RTC files, UTC/localtime selection, and verbose/debug output.
- Selects a hardware access backend through `clock_ops`: direct CMOS when compiled and requested, otherwise `/dev/rtc` on Linux/GNU.
- Reads `/etc/adjtime`-style data into drift factor, last adjustment, last calibration, unadjusted remainder, and UTC/local marker; writes it back when dirty unless `--noadjfile`.
- Determines whether the hardware clock is UTC from command-line options or adjtime state, defaulting to UTC when not explicitly local.
- Performs tick-synchronized reads, converts RTC `struct tm` with `mktime()`/`timegm()`, calculates drift, and displays either raw show time or drift-corrected get time.
- Sets the hardware clock with sub-second alignment logic that waits for the chosen reference offset and accounts for the typical RTC set delay.
- Handles system clock/timezone operations through `settimeofday` wrappers that avoid libc portability issues around the deprecated timezone argument.

Important implementation details:
- `set_hardware_clock_exact()` is the timing-critical core: it computes a target system time, loops until close enough within an expanding tolerance, retargets after missed windows or backward jumps, then sets the RTC to an adjusted integer second.
- `adjust_drift_factor()` updates drift only with `--update-drift`, enough calibration history, and at least four hours since prior calibration; excessive drift is reset to zero.
- `manipulate_clock()` centralizes operation selection and intentionally avoids reading the RTC for simple set/systohc operations unless drift update is requested, reducing shutdown latency and allowing recovery from corrupt RTC reads.
- Audit logging is optional through libaudit and records time-changing operations unless testing.

Dependencies and integration:
- Uses `hwclock.h` backend contracts, `hwclock-rtc.c`, optionally `hwclock-cmos.c`, and optionally `hwclock-parse-date.y`.
- Relies on util-linux time, path, string, debug, NLS, and close-stream helpers.

Risks and edge cases:
- Time-setting logic is sensitive to scheduler delays and system time jumps; the code explicitly retargets and widens tolerance but cannot guarantee exactness under severe scheduling latency.
- `--noadjfile` requires explicit `--utc` or `--localtime`, preventing silent defaulting when state storage is disabled.
- Kernel timezone/PCIL behavior is Linux-specific and handled with detailed compatibility paths.
