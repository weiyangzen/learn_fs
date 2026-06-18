# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/Makefile

## Purpose
Defines the object composition for the MT7601U driver module.

## Important APIs, Types, And Functions
`obj-$(CONFIG_MT7601U) += mt7601u.o` builds the module from `usb.o init.o main.o mcu.o trace.o dma.o core.o eeprom.o phy.o mac.o util.o debugfs.o tx.o`. `CFLAGS_trace.o := -I$(src)` supports trace header include resolution.

## Control Flow
No runtime flow. Kbuild links listed objects into the `mt7601u` module when enabled.

## State And Persistence
Build state is the object list and per-object CFLAGS.

## Dependencies And Integration Points
Integrates with Kbuild, the Kconfig symbol, and tracepoint generation for `trace.o`.

## Risks
Omitting an object causes unresolved symbols or missing driver behavior. Trace CFLAGS are required for `TRACE_INCLUDE_PATH .` patterns.

## Test Signals
Successful module build, no unresolved symbols across the listed objects, and tracepoint generation for mt7601u trace events.
