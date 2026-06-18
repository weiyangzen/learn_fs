# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_dvb.c

- Purpose: Registers the DVB adapter, demux, dmxdev, DVB net device, hardware/memory frontends, and board frontend for the Mantis bridge.
- Important APIs/types/functions: `mantis_frontend_power()`, `mantis_frontend_soft_reset()`, `mantis_dvb_init()`, `mantis_dvb_exit()`, feed callbacks, and module adapter-number option.
- Control flow: Init registers a DVB adapter, initializes demux and dmxdev, adds frontends, connects hardware input, initializes DVB net, configures DMA work, calls board `frontend_init`, then registers the frontend. Feed start increments `feeds` and starts DMA on the first feed; feed stop decrements and stops DMA at zero.
- State and persistence: Tracks active feed count, frontend pointer, demux objects, and work item in `struct mantis_pci`. No persistence; frontend power/reset lines are hardware state controlled over GPIO.
- Dependencies and integration points: Depends on DVB core/demux/net, local DMA and GPIO helpers, and each board frontend attachment implementation.
- Risks: Feed count is not protected by a lock. Error unwind must keep DVB object release order exact. Frontend power/reset has fixed sleeps and board-specific GPIO assumptions. `mantis->fe` is passed into board init before assignment by many boards.
- Test signals: Test with adapter registration, frontend attach failure paths, scan/tune, multiple demux consumers, feed start/stop races, and unload after failed or active frontend registration.
