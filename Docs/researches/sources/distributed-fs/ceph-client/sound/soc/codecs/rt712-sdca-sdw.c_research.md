# sources/distributed-fs/ceph-client/sound/soc/codecs/rt712-sdca-sdw.c

Purpose: Provides the SoundWire bus glue for the multi-function RT712 SDCA codec. It declares regmaps, readable/volatile register ranges, port properties, SDCA interrupt handling, attach-time initialization, and PM cache synchronization.

Important APIs and functions: `rt712_sdca_sdw_probe()` creates the SDCA and MBQ regmaps and calls `rt712_sdca_init()`. `rt712_sdca_read_prop()` advertises source ports 4/8 and sink ports 1/3 with paging, wake capability, and clock-stop timeout. `rt712_sdca_update_status()` restores SDCA interrupt masks after attach and calls `rt712_sdca_io_init()`. `rt712_sdca_interrupt_callback()` reads and clears SDCA interrupt status, merges pending button status if work was canceled, and schedules jack delayed work.

Control flow: Probe registers the bus driver with SDW IDs for RT712/713/716/717. On attach, interrupt masks may be restored before initialization to avoid missing jack events. Interrupt processing cancels pending jack work, snapshots `SCP_SDCA_INT1/2`, loops up to three times clearing SDCA cascade flags, and schedules jack work after 30 ms unless system suspend disabled IRQ handling. Suspend cancels jack work, disables SDCA interrupt masks for system sleep, and switches both regmaps cache-only. Resume waits for enumeration if needed, reenables masks, clears `unattach_request`, and syncs both regmaps.

State and persistence: Uses the shared `rt712_sdca_priv` state from the core file, especially `scp_sdca_stat1/2`, `disable_irq`, `hw_init`, and `first_hw_init`. Regcache covers both 8-bit SDCA controls and 16-bit MBQ vendor/index values.

Dependencies and integration: Depends on SoundWire slave ops, regmap SoundWire helpers including MBQ, runtime PM, `rt712-sdca.h`, and the defaults in `rt712-sdca-sdw.h`. It imports `SND_SOC_SDCA`.

Risks and test signals: Interrupt clearing and canceled-work status merging are race-prone. Tests should cover jack/button events under repeated interrupts, attach after reset, suspend during pending jack work, unattach/resume timeout paths, source/sink port discovery, and cache sync of both regmaps.
