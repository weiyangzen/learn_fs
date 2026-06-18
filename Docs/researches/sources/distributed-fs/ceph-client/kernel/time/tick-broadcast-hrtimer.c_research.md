# sources/distributed-fs/ceph-client/kernel/time/tick-broadcast-hrtimer.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/tick-broadcast-hrtimer.c` implements an hrtimer-backed pseudo clock-event device used as a broadcast tick source. It lets the generic tick broadcast code emulate a broadcast clockevent when no suitable hardware broadcast device is available. The complete 104-line source was read.

## Important APIs, Types, and Functions

The main global state is `static struct hrtimer bctimer` and `static struct clock_event_device ce_broadcast_hrtimer`. Important functions are `bc_shutdown`, `bc_set_next`, `bc_handler`, and externally visible `tick_setup_hrtimer_broadcast`.

## Control Flow

`tick_setup_hrtimer_broadcast` initializes `bctimer` on `CLOCK_MONOTONIC` and registers `ce_broadcast_hrtimer` with the clockevents layer. The broadcast core programs the pseudo device through `bc_set_next`, which starts the hrtimer at an absolute pinned hard deadline and records the CPU base in `bc->bound_on`. When the hrtimer expires, `bc_handler` invokes the clockevent device's event handler, which is installed by the generic broadcast code. Shutdown uses `hrtimer_try_to_cancel` rather than a blocking cancel to avoid lock inversion with the broadcast handler.

## State and Persistence Behavior

State is global and in memory. The clockevent advertises oneshot and hrtimer features, broad CPU affinity, delta limits, and the current CPU it is bound on. `bctimer` persists for the lifetime of the kernel after registration.

## Dependencies and Integration Points

Dependencies include hrtimers, clockevents, CPU masks, and `tick-internal.h`. This file integrates directly with `tick-broadcast.c`: the generic broadcast logic treats `ce_broadcast_hrtimer` as a broadcast device but contains special handling to avoid recursion and to keep the CPU that owns the hrtimer out of deep idle.

## Risks and Edge Cases

The shutdown path is intentionally non-blocking because `tick_broadcast_lock` may be held while the callback is waiting for the same lock. `bc_set_next` cannot cancel or synchronously move a running hrtimer callback, so the timer may remain on its current CPU; `bound_on` must match the real hrtimer base after start. Broadcast recursion is a risk if the hrtimer broadcast device tries to run a local handler that expires the same hrtimer path.

## Test Signals

Relevant tests include booting systems that rely on hrtimer broadcast, NO_HZ idle entry/exit with hrtimer broadcast active, CPU hotplug when the broadcast hrtimer is bound to an outgoing CPU, suspend/resume, and lockdep tests around broadcast lock and hrtimer callback interactions.
