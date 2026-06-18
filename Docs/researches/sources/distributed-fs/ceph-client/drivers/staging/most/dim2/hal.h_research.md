# sources/distributed-fs/ceph-client/drivers/staging/most/dim2/hal.h

## Purpose
Declares the DIM2 HAL public interface, channel state structures, MediaLB clock values, and callback hook used by the platform driver.

## Important APIs, Types, And Functions
`enum mlb_clk_speed` enumerates 256fs through 8192fs. `struct dim_ch_state` reports readiness and completed-buffer count. `struct int_ch_state` holds request/service counters, producer/consumer indices, and queue level. `struct dim_channel` stores channel address, DBR address/size, packet/sync sizing, and done-buffer count. Public APIs cover startup/shutdown, lock state, buffer-size normalization, channel init/destroy for control/async/isoc/sync, MLB/AHB IRQ service, per-channel service, state query, DBR space, enqueue, detach, and error callback.

## Control Flow
`dim2.c` calls startup at probe, init functions during MOST configure, enqueue/detach during buffer flow, service functions from IRQ handlers, and shutdown from release.

## State And Persistence
The header exposes runtime state containers only. Persistent behavior is none.

## Dependencies And Integration Points
Depends on Linux types and `reg.h`. Integrates `dim2.c` with `hal.c`.

## Risks And Test Signals
The API assumes external locking and valid channel lifetimes. Test signals include all init variants, invalid parameters, ready/done state transitions, and no use after `dim_destroy_channel()`.
