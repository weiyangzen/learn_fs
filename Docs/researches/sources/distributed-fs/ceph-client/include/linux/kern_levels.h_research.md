# sources/distributed-fs/ceph-client/include/linux/kern_levels.h

## Purpose
Defines printk log-level string prefixes and their integer equivalents.

## Important APIs, Types, And Functions
String prefixes include `KERN_EMERG` through `KERN_DEBUG`, plus `KERN_DEFAULT` and `KERN_CONT`. Integer levels include `LOGLEVEL_SCHED`, `LOGLEVEL_DEFAULT`, and `LOGLEVEL_EMERG` through `LOGLEVEL_DEBUG`. `KERN_SOH` and `KERN_SOH_ASCII` define the prefix marker.

## Control Flow
There is no runtime flow in this header. Printk parses prefix strings embedded in format strings and maps them to log levels or continuation behavior.

## State And Persistence
No state is stored. The selected log level affects printk ring buffer entries and console output elsewhere.

## Dependencies And Integration Points
Used by `printk.h`, kernel logging, scheduler deferred logging, early boot messages, and drivers that include log-level prefixes in messages.

## Risks
`KERN_CONT` is only safe for narrow early/core use because continuation lines are not generally SMP-safe. Incorrect prefixes can hide important messages or flood logs.

## Test Signals
Signals include printk formatting tests, console loglevel filtering, continuation-line behavior, scheduler deferred message handling, and static checks for valid prefix use.
