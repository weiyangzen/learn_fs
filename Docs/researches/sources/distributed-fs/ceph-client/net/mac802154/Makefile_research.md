# sources/distributed-fs/ceph-client/net/mac802154/Makefile

## Purpose
The Makefile builds the mac802154 composite object when `CONFIG_MAC802154` is enabled.

## Important APIs, Types, And Functions
`obj-$(CONFIG_MAC802154) += mac802154.o` gates the module/built-in object. `mac802154-objs` lists `main.o`, `rx.o`, `tx.o`, `mac_cmd.o`, `mib.o`, `iface.o`, `llsec.o`, `util.o`, `cfg.o`, `scan.o`, and `trace.o`. `CFLAGS_trace.o := -I$(src)` supplies trace include path handling.

## Control Flow
There is no runtime control flow. Kbuild aggregates the listed objects into `mac802154.o`.

## State And Persistence
Build output depends on the kernel configuration and object list. No runtime state is defined here.

## Dependencies And Integration Points
The object list ties together registration (`main.o`), RX/TX, MAC commands, MIB, interface creation, LLSEC, cfg802154 ops, scanning, and tracepoints into one module.

## Risks And Edge Cases
Missing a new source file from `mac802154-objs` can compile cleanly only if no references require it, leaving features absent. Trace include path changes can break trace event generation.

## Test Signals
Build tests with `CONFIG_MAC802154=m/y` and tracepoint generation are the main signals.
