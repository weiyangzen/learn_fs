# sources/distributed-fs/ceph-client/drivers/misc/atmel-ssc.c

Purpose: implements the Atmel AT91 Synchronous Serial Controller platform driver and exports a small reservation API for other kernel users, especially audio.

Important APIs and functions: exported functions are `ssc_request(unsigned int ssc_num)` and `ssc_free(struct ssc_device *ssc)`. Platform lifecycle is `ssc_probe` and `ssc_remove`. Optional audio integration uses `ssc_sound_dai_probe` and `ssc_sound_dai_remove`. Device matching uses platform ids and OF compatibles for AT91RM9200, AT91SAM9RL, and AT91SAM9G45 variants.

Control flow: probe allocates `struct ssc_device`, selects platform data from OF or platform id, records optional `atmel,clk-from-rk-pin`, maps registers, gets `pclk`, disables all SSC interrupts under a prepared clock, obtains IRQ, adds the device to the global `ssc_list`, stores drvdata, and optionally registers the SSC for ASoC DAI use. `ssc_request` scans the list by OF alias or platform id, rejects missing or busy devices, increments a user count under `user_lock`, prepares the clock, and returns the device. `ssc_free` decrements the user count and unprepares the clock.

State and persistence: a global list and per-device `user` count serialize exclusive ownership. Register mappings, clock, IRQ, platform data, and audio flag persist for the platform-device lifetime.

Dependencies and integration points: depends on platform devices, OF aliases, clk, MMIO, `linux/atmel-ssc.h`, and optional Atmel ASoC SSC helpers.

Risks: only one user can reserve an SSC, so sharing must be coordinated externally. `clk_prepare` return value is ignored in `ssc_request`. Removal does not explicitly handle an active user beyond list deletion. OF alias lookup mutates `pdev->id`.

Test signals: DT and platform-id probe, request/free busy behavior, clock prepare/unprepare balancing, interrupt-disable register writes, audio DAI auto-setup, and removal while unused.
