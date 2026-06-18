# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_pwr.c

## Purpose
Implements support for the newer Panthor PWR_CONTROL block: power IRQ handling, soft reset command completion, L2/shader/tiler power transitions, delegation and retraction of domains between host and MCU, and suspend/resume IRQ masking.

## Important APIs, Types, and Functions
`struct panthor_pwr` stores the IRQ wrapper, pending request mask, waitqueue, and spinlock. Exported functions are `panthor_pwr_init()`, `panthor_pwr_unplug()`, `panthor_pwr_reset_soft()`, `panthor_pwr_l2_power_off()`, `panthor_pwr_l2_power_on()`, `panthor_pwr_suspend()`, and `panthor_pwr_resume()`. Important helpers include `panthor_pwr_reset()`, `panthor_pwr_domain_transition()`, `delegate_domain()`, `retract_domain()`, and `panthor_pwr_domain_force_off()`.

## Control Flow
Initialization exits early when hardware lacks PWR_CONTROL, otherwise allocates `ptdev->pwr`, initializes wait state, obtains the named `gpu` IRQ, and requests a PWR IRQ handler for command/power events. Reset marks `PWR_IRQ_RESET_COMPLETED` pending, clears stale status, writes reset command, and waits on the waitqueue with timeout fallback. L2 power-on verifies allow bits, powers L2 ready cores, then delegates shader and tiler control to MCU. L2 power-off retracts and powers off tiler/shader first, then powers off L2. IRQ handling clears hardware status, reports invalid/disallowed commands, clears matching pending bits, and wakes waiters.

## State and Persistence
Persistent state is `ptdev->pwr`, `pending_reqs`, and the waitqueue. Hardware state is represented by PWR status, ready, transition, and delegation bits. The code does not retain software mirrors of powered cores beyond request completion; it polls registers as the source of truth.

## Dependencies and Integration Points
Depends on Panthor hardware feature detection, GPU register access helpers, the common Panthor IRQ wrapper, platform IRQ lookup, DRM managed allocation, and PWR register macros from `panthor_regs.h`. It coordinates with MCU/firmware ownership by delegating shader and tiler domains after L2 power-up and retracting them before host-forced power-down.

## Risks and Edge Cases
Timeout behavior is critical: reset timeout checks raw IRQ status before failing, while domain transition failures dump power debug registers. L2 cannot be delegated/retracted and shader domains may use RTU subdomain bits when ray traversal exists. Failed delegation after shader success retracts shader. If forced power-off retracts a domain but power-down fails, that domain remains under host control.

## Test Signals
Signals include boot on hardware with and without PWR_CONTROL, soft reset success/timeout, suspend/resume IRQ masking, L2 power cycle, shader/tiler delegation status, forced power-off after simulated hung MCU, invalid command IRQ logging, and register dumps on transition timeout.
