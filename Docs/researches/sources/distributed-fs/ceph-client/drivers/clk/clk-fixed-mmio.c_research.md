# sources/distributed-fs/ceph-client/drivers/clk/clk-fixed-mmio.c


### Purpose
`clk-fixed-mmio.c` provides a simple fixed-rate clock whose frequency is read from a memory-mapped register at registration time.

### Important APIs, Types, And Functions
The main helper is `fixed_mmio_clk_setup()`. It is used by early `of_fixed_mmio_clk_setup()` registered with `CLK_OF_DECLARE()` and by the fallback platform driver probe for compatible `fixed-mmio-clock`.

### Control Flow, State, And Persistence
Setup maps the first OF resource with `of_iomap()`, reads a 32-bit frequency, immediately unmaps the resource, optionally reads `clock-output-names`, registers a fixed-rate clock, and adds an OF provider. Platform probe runs only if early setup did not succeed and stores the `clk_hw` for remove. Remove deletes the provider and unregisters the fixed-rate clock. The clock is a snapshot of the register value; later MMIO changes are not tracked.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include OF address mapping, fixed-rate CCF registration, platform-driver fallback, and `fixed-mmio-clock` binding. Risks include assuming a 32-bit little-endian register, no cleanup if fixed-rate registration fails after mapping is already unmapped but before provider install, early setup lacking remove, and snapshot staleness. Test signals include early and platform probe paths, mapping failure, output-name override, provider lookup, register-frequency correctness, and remove cleanup.
