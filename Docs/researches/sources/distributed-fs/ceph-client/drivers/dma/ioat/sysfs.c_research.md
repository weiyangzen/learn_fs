
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ioat/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/dma/ioat/sysfs.c

Purpose: exposes per-channel IOAT diagnostics and tuning through a `quickdata` kobject under each DMA channel device. It reports advertised capabilities, hardware version, ring size/activity, and a writable interrupt-coalescing factor.

Important APIs and control flow: `struct ioat_sysfs_entry` binds sysfs attributes to DMA-channel show/store callbacks. `cap_show()` prints the active DMAEngine capability set, `version_show()` formats the IOAT version nibble pair, `ring_size_show()` and `ring_active_show()` report ring allocation/activity, and `intr_coalesce_show()`/`intr_coalesce_store()` expose `ioat_chan->intr_coalesce`. `ioat_kobject_add()` initializes `quickdata` kobjects for all channels after DMAEngine registration, and `ioat_kobject_del()` removes them if initialization succeeded. `ioat_ktype` wires custom sysfs ops and default attribute groups.

State and persistence behavior: per-channel kobject lifetime is tracked in `ioat_chan->state` with `IOAT_KOBJ_INIT_FAIL`. `intr_coalesce` persists in the channel object; `dma.c` later writes the global interrupt-delay register when the value changes during cleanup. Ring counters are sampled without precision guarantees.

Dependencies and integration points: depends on DMAEngine channel devices already existing, IOAT channel/device containers from `dma.h`, and capability masks set by `init.c`. It integrates with sysfs through raw kobject APIs rather than a device attribute helper.

Risks and test signals: risks include `sscanf(page, "%du", ...)` accepting odd input patterns, ring-size display masking off one descriptor while allocation keeps the full power-of-two count, imprecise unlocked `ring_active`, kobject parent assumptions, and global interrupt-delay hardware being tuned from per-channel state. Test signals include `quickdata` nodes present for every channel, capability output matching DMAEngine caps, version output matching MMIO version, writable `intr_coalesce` rejecting out-of-range values, and removal/unload not leaking kobjects after partial init failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ioat/sysfs.c -->
