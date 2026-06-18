<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pcf857x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-pcf857x.c

## Purpose
Driver for PCF857x/PCA857x/PCA967x/MAX7328/MAX7329 quasi-bidirectional I2C expanders. It models input by writing a high latch bit and maintains software state because hardware has only one read and one write register.

## Important APIs, types, and functions
`struct pcf857x` stores chip, client, latch mutex, `out`, previous `status`, enabled IRQ bits, and 8/16-bit transfer functions. GPIO callbacks cover input, output, get/set, and multiple operations. Optional IRQ support uses a threaded parent IRQ and software change filtering.

## Control flow
Probe optionally resets the chip, reads `lines-initial-states`, selects 8-bit SMBus or 16-bit I2C helpers, verifies presence, initializes `out = ~n_latch`, snapshots status, optionally requests parent IRQ, and registers the chip. Parent IRQ reads current status, computes changed enabled bits, updates status, and dispatches nested IRQs.

## State and persistence behavior
`out` is the software latch and `status` is the previous sample for IRQ change detection. Shutdown drives all lines high. No suspend/resume context exists.

## Dependencies and integration points
Uses I2C functionality checks, optional reset GPIO, DT initial-state property, gpiolib, optional IRQs, and `subsys_initcall()`.

## Risks and edge cases
Direction is not independently readable. Initial latch assumptions affect glitches. IRQs are software-filtered changes and can be missed/coalesced. Parent IRQ trigger is generic falling edge rather than per-line sense.

## Test signals
8/16-bit access, reset timing, initial states, high-latch input behavior, multiple ops, shutdown high write, enabled-line IRQ filtering, and wake forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pcf857x.c -->
