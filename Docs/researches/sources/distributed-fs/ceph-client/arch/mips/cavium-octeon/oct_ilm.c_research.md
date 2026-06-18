# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/oct_ilm.c

## Purpose
Measures Octeon interrupt latency with a CIU one-shot timer and exposes statistics through debugfs.

## Important APIs, Types, And Functions
Important functions are `oct_ilm_show()`, `reset_statistics()`, `init_debugfs()`, `init_latency_info()`, `start_timer()`, `cvm_oct_ciu_timer_interrupt()`, `disable_timer()`, `oct_ilm_module_init()`, and `oct_ilm_module_exit()`. State is `struct latency_info li`, `reset_stats`, and debugfs `dir`.

## Control Flow
Module init creates debugfs, requests timer IRQ 3, initializes intervals from clock rates, and starts a one-shot timer. The interrupt handler computes latency from cycle count versus expected deadline, updates min/max/sum/count, handles reset requests, and restarts the timer. Exit disables the timer, removes debugfs, and frees the IRQ.

## State, Persistence, And Dependencies
Stats persist while loaded. CIU timer registers persist until disabled. Dependencies include debugfs, Octeon clock functions, local IRQ masking, and CIU timer CSRs.

## Integration Points
Users interact via `/sys/kernel/debug/oct_ilm/statistics` and `reset`.

## Risks
`oct_ilm_show()` divides by `interrupt_cnt`, so early reads can divide by zero. `disable_timer()` does not zero the union before field writes. Stats are read without locking. The statistics debugfs mode appears write-only despite show usage.

## Test Signals
Check IRQ registration, counter growth, plausible ns values, reset behavior, safe first read, and clean unload.
