<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/cldma.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/cldma.c

Purpose: code-loader DMA implementation for AVS platforms with CLDMA, used primarily by SKL-style firmware and module loading.

Important APIs, types, and functions: internal `struct hda_cldma`; global `code_loader`; exported helpers `hda_cldma_init()`, `free()`, `setup()`, `set_data()`, `transfer()`, `fill()`, `start()`, `stop()`, `reset()`, and `interrupt()`. Register helpers target stream descriptor registers and software position based FIFO (SPIB) registers.

Control flow: `hda_cldma_init()` allocates SG data buffer and BDL buffer, records DSP base and stream address. `hda_cldma_setup()` builds BDL entries over the circular buffer, writes BDL/CBL/LVI/stream tag registers, and enables SPIB. `hda_cldma_transfer()` initializes completion state, fills the first chunk, and schedules delayed work. The work function starts DMA, waits for IOC completions, checks stream status, refills data until `remaining` reaches zero, and re-enables CLDMA interrupts between chunks. IRQ handling disables CLDMA interrupt, captures SD status, and completes the wait.

State and persistence: `code_loader` is a singleton with a fixed stream tag. Runtime transfer state is `position`, `remaining`, and `sd_status`; DMA buffers persist until `hda_cldma_free()`. Completion and delayed work coordinate process context and interrupt context.

Dependencies and integration points: called from `loader.c` for base firmware, libraries, and modules; interrupt path is expected from platform DSP interrupt handlers; uses HDA stream and ADSP register helpers plus `BDL_SIZE`.

Risks: singleton state means only one CLDMA transfer may be active. Pointer arithmetic on `void *position` relies on compiler extension common in kernel C. Timeout or non-IOC status logs errors but higher layers must stop/reset appropriately. BDL IOC is set only on the last entry of the circular buffer, affecting refill cadence.

Test signals: firmware load reaches ROM/basefw status transitions, CLDMA IOC timeouts are absent, `SD_INT_COMPLETE` appears in status, and `hda_cldma_stop()` cleanly cancels delayed work on errors/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/cldma.c -->
