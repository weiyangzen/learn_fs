# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_buffer.h

## Purpose
Provides inline command emission primitives for etnaviv command buffers.

## Important APIs, Types, and Functions
Defines `OUT`, `CMD_LOAD_STATE`, `CMD_LOAD_STATES_START`, `CMD_END`, `CMD_WAIT`, `CMD_LINK`, `CMD_STALL`, and `CMD_SEM`. These operate on `struct etnaviv_cmdbuf` and generated command/register macros.

## Control Flow
Each helper aligns `user_size` as required, writes command words into the buffer, and advances `user_size`. `CMD_SEM` emits a GL semaphore token through LOAD_STATE.

## State and Persistence
The only state changed is `cmdbuf->user_size` and the backing memory pointed at by `cmdbuf->vaddr`. `OUT` uses `BUG_ON` if writes exceed `cmdbuf->size`.

## Dependencies and Integration Points
Used heavily by `etnaviv_buffer.c` and `etnaviv_flop_reset.c`. Depends on generated `cmdstream.xml.h`, state register headers, and `struct etnaviv_cmdbuf`.

## Risks
These helpers assume callers reserve enough space and provide valid register/opcode values. Buffer overflow triggers a kernel BUG, so callers must compute sizes correctly.

## Test Signals
Command buffer construction tests, runtime GPU submissions, debug hex dumps, and KASAN/BUG reports from oversized emissions are relevant.
