# sources/distributed-fs/ceph-client/drivers/peci/controller/peci-aspeed.c

Purpose: Implements the ASPEED AST2400/AST2500/AST2600 PECI controller driver. It programs the controller MMIO block, manages a hardware-derived PECI clock divider, sends PECI requests through the core controller API, and handles command-completion interrupts.

Important APIs and functions: `aspeed_peci_probe()` maps MMIO, requests IRQ, gets/deasserts reset, reads sanitized properties, initializes registers, registers a clock divider, enables it, enables the controller, and calls `devm_peci_controller_add()`. Runtime transfer is `aspeed_peci_xfer()`. IRQ handling is `aspeed_peci_irq_handler()`. Clock operations are `clk_aspeed_peci_set_rate()`, `clk_aspeed_peci_determine_rate()`, and `clk_aspeed_peci_recalc_rate()`.

Control flow: A transfer validates 32-byte TX/RX limits, calls `aspeed_peci_check_idle()` which may reset/reinitialize hung hardware, programs target/write/read lengths and TX data registers, clears status, fires the command, waits for completion, checks interrupt status, then reads RX data registers in dwords. The IRQ handler reads and clears interrupt status, ORs masked status into `priv->status`, completes the transfer on command done, writes zero to the command register, and releases the spinlock.

State and persistence: `struct aspeed_peci` stores controller pointer, device, MMIO base, reset, IRQ, spinlock, completion, clock, configured frequency, status, and timeout. Device-tree properties `clock-frequency` and `cmd-timeout-ms` are sanitized and persist in driver state. Hardware timing, interrupt, control, and data registers persist until reset or reprogramming.

Dependencies and integration points: Depends on Linux PECI core (`struct peci_controller_ops`), platform device/of matching, reset controller, common clock framework, MMIO polling, completions, spinlocks, and unaligned access helpers. Matches `aspeed,ast2400-peci`, `aspeed,ast2500-peci`, and `aspeed,ast2600-peci`.

Risks: The transfer path in this source contains a duplicated `spin_lock_irq(&priv->lock)` before checking `priv->status`; as written, that is a deadlock-level bug because the same spinlock is acquired twice without an intervening unlock. TX/RX loops write/read in 4-byte chunks using unaligned helpers, so request buffer sizing must remain compatible with `PECI_REQUEST_MAX_BUF_SIZE`. Idle recovery resets hardware and must restore clock rate and controller enable correctly. Clock divider search approximates the requested frequency.

Test signals: Device-tree probe on AST24xx/25xx/26xx, reset and clock setup, sanitized property warnings for invalid values, PECI ping/transactions through the core, command-done IRQ completion, timeout path, idle-hang reset recovery, dynamic-debug TX/RX dumps, and lockdep or runtime testing catching the duplicate spinlock acquisition.
