# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_cccb.c

Purpose: implements PowerVR client CCBs used by per-context queues to write job commands for firmware consumption and kick firmware through KCCB.

Important APIs/functions: `pvr_cccb_init()`/`pvr_cccb_fini()` allocate/free uncached firmware objects for client CCB control and data. `pvr_cccb_cmdseq_fits()` checks available ring space while reserving end padding if wrapping is needed. `pvr_cccb_write_command_with_header()` writes command headers, optional padding, and payload bytes. `pvr_cccb_send_kccb_kick()` and `pvr_cccb_send_kccb_combined_kick()` send firmware kicks for single or combined geometry/fragment queues.

Control flow and state: the CCCB owns CPU-visible `write_offset`, firmware-visible read/dependency offsets in control memory, and a power-of-two `wrap_mask`. Command writes ensure a padding command fits at ring end, wrap to zero when needed, and use `wmb()` before KCCB kicks so firmware sees client commands before the kick. Combined kicks optionally omit fragment cleanup resources for partial-render jobs.

Dependencies and integration: depends on firmware object mapping, KCCB command APIs, HWRT cleanup state addresses, firmware ABI command headers, and queue/job scheduler serialization. The code relies on drm_sched serializing command writes rather than an internal mutex.

Risks: command sequences larger than the supported half-ring capacity complicate wrapping and should be rejected by callers using `pvr_cccb_cmdseq_can_fit()`. Incorrect write offsets or missing padding can make firmware parse garbage.

Test signals: job submission tests should see CCCB write offsets advance, KCCB kicks issued after writes, and no WARN from insufficient CCB space checks.
