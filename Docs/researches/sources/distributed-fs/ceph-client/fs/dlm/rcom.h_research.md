# sources/distributed-fs/ceph-client/fs/dlm/rcom.h

## Purpose
`rcom.h` declares DLM recovery communication send and receive entry points.

## Important APIs, Types, And Functions
It exposes status, names, lookup, lock recovery sends, the receive dispatcher, and the special lockspace-not-ready reply helper.

## Control Flow
Recovery code uses the send helpers during barrier, directory, master, and lock recovery phases. The receive path calls `dlm_receive_rcom()` for all RCOM packets and `dlm_send_ls_not_ready()` when a packet targets a lockspace that is not ready.

## State And Persistence
The header owns no state. Implementations mutate lockspace recovery buffers and resource/lock state.

## Dependencies And Integration Points
It is used by `recover.c`, `recoverd.c`, `member.c`, lock receive paths, and low/mid communications.

## Risks
RCOM callers must pass the correct recovery sequence; stale sequence usage causes intentional ignore behavior. Lookup and lock sends require valid RSB/LKB lifetime.

## Test Signals
Build and recovery tests should cover each declared message type and lockspace-not-ready behavior.
