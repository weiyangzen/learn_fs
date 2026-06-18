# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-raw.c

Purpose: implements the raw-edge ImgTec IR receive path for systems that use generic software raw decoders instead of the ImgTec hardware scancode decoder. It registers a `RC_DRIVER_IR_RAW` rc-core device, enables edge interrupts, converts hardware level changes into raw edge events, and emits a final echo sample after quiet periods.

Important APIs, types, and functions: `img_ir_refresh_raw()` reads `IMG_IR_STATUS`, filters same-level double-edge noise, stores rising/falling edges with `ir_raw_event_store_edge()`, and calls `ir_raw_event_handle()`. `img_ir_isr_raw()` is called by the core ISR with the device spinlock held; it refreshes raw state and pushes the echo timer. `img_ir_echo_timer()` emits a final sample when no edges arrive for `ECHO_TIMEOUT_MS`. `img_ir_setup_raw()` enables `IMG_IR_IRQ_EDGE`. `img_ir_probe_raw()` allocates and registers the raw rc-core device. `img_ir_remove_raw()` unregisters the device, disables edge IRQs, clears pending edge IRQs, frees the rc device, and deletes the timer.

Control flow: probe creates the rc-core raw device and timer. Setup enables edge interrupts after the platform device has been initialized. Each edge interrupt refreshes the raw decoder state and schedules the echo timer. The echo timer reacquires `priv->lock` and refreshes with `irq_status == 0`, which bypasses double-edge treatment while preserving the final-space signal expected by raw decoders.

State and persistence behavior: `struct img_ir_priv_raw` stores the rc device pointer, timer, and last sampled level. `raw->rdev` is also the enabled/removing guard; removal sets it to `NULL` under `priv->lock` before deleting the timer. There is no persistent storage beyond device lifetime.

Dependencies and integration points: depends on `img-ir.h` register definitions and `media/rc-core.h` raw event APIs. It shares `priv->lock` and IRQ status dispatch with the platform core and can coexist with the hardware decoder depending on build/configuration.

Risks and edge cases: double-edge interrupts can be noise if the sampled level did not change; the filter avoids false raw transitions. Timer deletion order matters during removal because the timer also takes `priv->lock`. The final echo sample is necessary for decoders that need an ending space; removing it may break software protocol decoders despite correct edges.

Test signals: with raw mode enabled, use a known remote and verify generic software decoders receive events. Test quiet-period completion for protocols with long trailer spaces, removal while IR activity is present, and simultaneous rise/fall IRQ status noise.
