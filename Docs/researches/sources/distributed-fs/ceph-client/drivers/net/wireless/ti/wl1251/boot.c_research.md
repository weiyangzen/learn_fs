# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/boot.c

Purpose: Performs wl1251 hardware and firmware boot: soft reset, NVS/EEPROM handling, PLL/init sequencing, firmware upload, firmware start, mailbox discovery, interrupt setup, event mask setup, and firmware version readout.

Important APIs, types, and functions: Public functions are `wl1251_boot_target_enable_interrupts()`, `wl1251_boot_soft_reset()`, `wl1251_boot_init_seq()`, `wl1251_boot_run_firmware()`, and `wl1251_boot()`. Static helpers upload firmware chunks and NVS tables and clear ECPU halt.

Control flow: `wl1251_boot()` halts the embedded CPU, soft-resets hardware, loads NVS from EEPROM or host NVS file, reads boot attributes, runs the PLL/restart initialization sequence, verifies ECPU halt, uploads firmware in chunks through the download partition, starts firmware, waits for `WL1251_ACX_INTR_INIT_COMPLETE`, reads command/event mailbox addresses, switches to working memory partition, enables host/target interrupts, configures event mask and mailbox pointers, and returns.

State and persistence: Updates `wl->boot_attr`, `wl->cmd_box_addr`, `wl->event_box_addr`, `wl->intr_mask`, `wl->event_mask`, mailbox pointers via event config, and firmware version. NVS contents and firmware are copied to device memory; no host persistence is written.

Dependencies and integration points: Depends on register/memory IO helpers, partition switching, SPI/bus DMA requirements, ACX/event helpers, firmware/NVS buffers in `struct wl1251`, and hardware constants from register headers.

Risks: Hardware timing is sensitive: reset self-clear timeout, EEPROM sleep, PLL delays, and init interrupt polling must match silicon. Firmware length is parsed from raw header bytes and must be 4-byte aligned. NVS parsing trusts encoded burst lengths and destination addresses. Firmware upload uses a temporary DMA-safe chunk buffer and partition window math that must not overrun device memory.

Test signals: Boot logs for chip-id match, soft reset completion, init-complete interrupt, mailbox addresses, firmware version, event unmask success, and failure paths for missing NVS, malformed firmware length, or init timeout.
