# sources/distributed-fs/ceph-client/drivers/mtd/tests/torturetest.c

## Purpose
Repeatedly erases and writes selected eraseblocks to stress flash endurance and data integrity. It is explicitly dangerous and can wear out flash.

## Important APIs, Types, and Functions
Parameters include `dev`, starting `eb`, `ebcnt`, optional `pgcnt`, status `gran`, `check`, and `cycles_count`. Main helpers are `check_eraseblock()`, `write_pattern()`, `report_corrupt()`, `print_bufs()`, and `countdiffs()`. Pattern buffers hold `0xff`, alternating `0x55/0xaa`, and inverse alternating data.

## Control Flow
Init opens the MTD, validates page count, allocates patterns and bad-block table, scans the selected range, then loops until `cycles_count` expires or indefinitely by default. Each cycle erases good blocks, optionally verifies erased `0xff`, writes alternating patterns, optionally verifies them, increments cycle count, and periodically prints elapsed timing.

## State and Persistence
This test intentionally consumes erase cycles and writes selected blocks repeatedly. Runtime state includes pattern buffers, check buffer, bad-block map, and erase cycle counter. If interrupted or failed, blocks may contain the last written test pattern.

## Dependencies and Integration Points
Depends on MTD erase/read/write APIs, shared bad-block and erase helpers, kernel timing, and cooperative `mtdtest_relax()`.

## Risks
High destructive risk: it can wear out flash and destroy data. Infinite default behavior when `cycles_count` is zero requires operator care. Verification retries can distinguish transient read issues from persistent corruption but also produce large logs.

## Test Signals
Status logs show erase cycles completed and timing. Verification failures report differing pages, byte/bit counts, and detailed read-versus-written bytes.
