# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_hwi.c

Purpose: hardware interface implementation for AIC94xx initialization, context memory setup, PHY enablement, SCB allocation/posting, done-list processing, interrupt handling, LED control, and chip reset.

Important APIs/types/functions: exported functions include `asd_init_hw()`, `asd_chip_hardrst()`, `asd_hw_isr()`, `asd_ascb_alloc_list()`, `asd_post_ascb_list()`, `asd_post_escb_list()`, `asd_enable_phys()`, `asd_turn_led()`, and `asd_control_led()`. Major internal helpers initialize sliding windows, phys, ports, SCB queues, done lists, empty data buffers, empty SCBs, sequencer firmware, and extended command/device context memory.

Control flow: `asd_init_hw()` configures PCI sliding windows, disables split-completion timer, reads OCM/flash, sizes/extends SCB and DDB context memory, obtains SAS addresses, initializes PHYs/ports/SCB/done/ESCB resources, hard-resets the chip, downloads sequencer code, and starts sequencers. Runtime interrupts read/ack `CHIMINT`, schedule done-list tasklets, and dispatch COM/DEV/INIT/HOST error handlers. Done-list tasklet entries find `asd_ascb`s by `tc_index`, stop timers, remove pending SCBs, and invoke completion callbacks.

State and persistence: maintains `MBAR0_SWB_SIZE`, `hw_prof` limits/bitmaps, PHY identify-frame DMA buffers, `seq` pending queue, `tc_index` map, done-list ring/toggle, EDB/ESCB arrays, context extension DMA tokens, and hardware registers. State is volatile and rebuilt on probe; firmware/flash data is read but not persisted here.

Dependencies and integration: depends on PCI config space, DMA pools/coherent memory, libsas PHY structures, sequencer firmware helpers in `aic94xx_seq.c`, SDS readers, register accessors, tasklet/timer APIs, and dump helpers.

Risks and test signals: initialization has many partial-allocation paths and `asd_init_hw()` callers must clean up through `asd_destroy_ha_caches()`. Error handlers mostly hard-reset and leave recovery marked `XXX`, so injected parity/DMA/ARP2 errors are high risk. SCB posting relies on pending counts, head swapping, DMA next pointers, and timers. Signals include probe/remove stress, interrupt storms, SCB timeout tests, DDB/SCB max module parameters, MSI/shared IRQ behavior, PHY enablement, and DMA-mask fallback.
