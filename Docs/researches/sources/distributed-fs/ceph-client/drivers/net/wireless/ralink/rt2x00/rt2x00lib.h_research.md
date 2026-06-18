# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00lib.h

## Purpose
Declares the common rt2x00 library API used across configuration, queues, link tuning, firmware, debugfs, crypto, rfkill, and LED support. It also defines shared rate metadata and timing intervals for link tuning/watchdog.

## Important APIs, Types, And Functions
Defines intervals `WATCHDOG_INTERVAL`, `LINK_TUNE_INTERVAL`, `AGC_SECONDS`, `VCO_SECONDS`, `struct rt2x00_rate`, rate flags, `rt2x00_supported_rates`, `rt2x00_get_rate()`, `RATE_MCS()`, and `rt2x00_get_rate_mcs()`. It declares radio/start/stop/config handlers, queue allocation/alignment/TX/beacon APIs, link stats/tuner/watchdog APIs, firmware load/free, debugfs register/deregister/update, crypto helpers or stubs, rfkill polling inline helpers, and LED helpers or stubs.

## Control Flow
Common and bus-specific modules include this header to call shared services without depending on optional feature implementations. Compile-time feature flags select real functions or no-op stubs for firmware, debugfs, crypto, and LEDs. Queue and link declarations are used throughout rt2x00 TX/RX and lifecycle code.

## State And Persistence
No runtime storage is defined except through external `rt2x00_supported_rates`. The declarations describe operations over persistent state in `rt2x00_dev`, queues, link structures, firmware pointer, debugfs interface, and LED objects.

## Dependencies And Integration Points
Depends on `rt2x00.h` types, mac80211 SKBs/configuration, queue structures, and optional kernel configs. It is the common internal API surface between `rt2x00dev.c`, `rt2x00config.c`, `rt2x00queue.c`, `rt2x00link.c`, `rt2x00firmware.c`, `rt2x00debug.c`, `rt2x00crypto.c`, and `rt2x00leds.c`.

## Risks
Stubbed optional features must preserve semantics expected by callers; for example no-op crypto changes skb handling assumptions only when hardware crypto is disabled. Public queue and beacon APIs have locking expectations documented in comments; misuse can deadlock or race. Rate helper indexes assume mac80211 hw values are within the 12-entry table.

## Test Signals
Build matrix with firmware/debugfs/crypto/LED configs enabled and disabled, queue/beacon update locking, link tuner/watchdog scheduling, rate mapping for all supported rates, and rfkill polling behavior for hardware button capability.
