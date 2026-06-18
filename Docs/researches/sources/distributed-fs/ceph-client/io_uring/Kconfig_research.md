# sources/distributed-fs/ceph-client/io_uring/Kconfig

## Purpose
This Kconfig fragment enables optional io_uring features based on dependency availability.

## Important APIs, Types, And Functions
- `IO_URING_ZCRX` defaults on when `IO_URING`, `PAGE_POOL`, `INET`, and `NET_RX_BUSY_POLL` are present.
- `IO_URING_BPF` defaults on when `BPF` and `NET` are present.
- `IO_URING_BPF_OPS` defaults on when `IO_URING`, `BPF_SYSCALL`, `BPF_JIT`, and `DEBUG_INFO_BTF` are present.

## Control Flow
There is no runtime flow. These symbols drive compilation in the Makefile and conditional code paths.

## State And Persistence
Configuration state persists in the kernel build and determines which object files and APIs exist.

## Dependencies And Integration Points
The symbols map to `zcrx.o`, `bpf_filter.o`, and `bpf-ops.o` in the io_uring Makefile. Headers provide stubs when optional features are disabled.

## Risks And Edge Cases
Because all three are `def_bool y`, enabling dependencies implicitly enables the feature. Incorrect dependencies could expose compile failures or runtime APIs in unsupported environments.

## Test Signals
Build matrix coverage with and without BPF, BTF/JIT, networking, busy-poll, and page-pool support validates these dependencies.
