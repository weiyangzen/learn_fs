# sources/distributed-fs/ceph-client/arch/s390/kernel/cpcmd.c

## Purpose
Implements in-kernel z/VM CP command execution through diagnose code 8. It converts commands and responses between ASCII and EBCDIC and serializes access to the shared low-address command buffer.

## Important APIs, Types, And Functions
`cpcmd()` is the exported SMP-safe API. `__cpcmd()` is exported but explicitly unlocked. Internal helpers are `diag8_noresponse()` and `diag8_response()`. Static state includes `cpcmd_lock` and `cpcmd_buf[241]`.

## Control Flow
`cpcmd()` optionally allocates a low buffer for vmalloc/module response destinations, takes the spinlock, and calls `__cpcmd()`. `__cpcmd()` validates command length with `BUG_ON`, copies and ASCII-to-EBCDIC converts the command, increments the DIAG 0x008 counter, issues diagnose 8 with or without a response buffer, converts response bytes back to ASCII, and returns response length while optionally storing the CP response code.

## State And Persistence
The shared static command buffer is transient protected state. No durable persistence is used, but CP commands can mutate z/VM control-program state outside Linux.

## Dependencies And Integration Points
Depends on diagnose accounting, physical address conversion, EBCDIC helpers, and low-level asm condition-code handling. It backs vmcp and other z/VM-aware kernel code.

## Risks And Edge Cases
Command length above 240 triggers `BUG_ON`, so callers must validate. The unlocked API is not SMP-safe. Response handling differs by condition code and must handle vmalloc destinations with bounce buffers.

## Test Signals
Signals include z/VM CP command smoke tests, no-response and response paths, EBCDIC round trips, vmalloc response buffer tests, and concurrency tests around `cpcmd_lock`.
