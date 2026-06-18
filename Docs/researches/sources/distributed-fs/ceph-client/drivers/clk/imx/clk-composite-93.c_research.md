## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-composite-93.c

### Purpose
`clk-composite-93.c` implements i.MX93 slice composite clocks with mux, divider, optional gate, busy polling, and TrustZone/domain authorization handling.

### Important APIs, Types, And Functions
`imx93_clk_composite_wait_ready()` polls the slice status register. Gate, divider, and mux ops update fields and wait for readiness. `imx93_clk_composite_flags()` is the exported constructor and selects read-only ops when authorization forbids non-secure writes.

### Control Flow
Registration allocates mux and divider components, reads `AUTHEN_OFFSET`, and checks `TZ_NS_MASK` plus the domain whitelist bit. Unauthorized clocks are registered as read-only composites with no gate. Authorized clocks allocate a gate at `CCM_OFF_SHIFT` and use custom ops that wait for busy clear after every write.

### State, Persistence, And Dependencies
Hardware state persists in slice control, status, and authorization registers. Driver state is heap-allocated CCF components. Dependencies include `readl_poll_timeout_atomic`, global `imx_ccm_lock`, `mcore_booted`, and domain IDs supplied by SoC tables.

### Integration Points
i.MX93 CCM drivers use this for clock roots exposed to Linux or marked read-only due to secure-world ownership.

### Risks
Wrong domain IDs can make clocks read-only or writable incorrectly. Busy timeouts return errors for rate/parent changes but gate enable ignores timeout except for logging through helper return path. Gate disable is skipped when M-core is booted.

### Test Signals
Test authorized and unauthorized domains, busy-timeout fault injection, parent/rate changes with status polling, M-core shared-clock behavior, and secure firmware configurations.
