# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_scb.c

Purpose: this file manages non-I/O SCB behavior for aic94xx, especially empty SCB event handling, phy/link event translation, port formation/deformation, EDB recycling, and libsas phy-control requests.

Important APIs/types/functions: exported/externally used functions are `asd_invalidate_edb()`, `asd_init_post_escbs()`, `asd_build_control_phy()`, `asd_ascb_timedout()`, and `asd_control_phy()`. Internal handlers include `get_lrate_mode()`, `asd_phy_event_tasklet()`, `asd_get_attached_sas_addr()`, `asd_form_port()`, `asd_deform_port()`, `asd_bytes_dmaed_tasklet()`, `asd_link_reset_err_tasklet()`, `asd_primitive_rcvd_tasklet()`, `escb_tasklet_complete()`, `control_phy_tasklet_complete()`, and `set_speed_mask()`.

Control flow and state: posted ESCBs receive hardware empty-buffer events. `escb_tasklet_complete()` decodes the done-list opcode/status block, handles special sequencer requests (`REQ_TASK_ABORT`, `REQ_DEVICE_RESET`, NCQ error notices), dispatches BYTES_DMAED/primitive/phy/link/timer events, then invalidates the used EDB. BYTES_DMAED copies identify/FIS data into `sas_phy.frame_rcvd`, derives attached SAS addresses for SATA, forms or updates ports, and notifies libsas. Link reset and timer failures turn LEDs off, disconnect libsas phys, deform ports, and may post an enable-phy SCB when retries are exhausted. `asd_control_phy()` translates libsas `phy_func` requests into `CONTROL_PHY` SCBs.

Persistence behavior: mutates in-memory phy/port association, `hw_prof.enabled_phys`, LED state, libsas negotiated linkrate, received frame buffers, and EDB validity. EDBs are recycled only after all buffers in an ESCB have been invalidated and the ESCB is reposted.

Dependencies and integration points: depends on aic94xx register/OOB macros, ASCB allocation/posting, LED helpers, dump helpers, and libsas notifications (`sas_notify_phy_event`, `sas_notify_port_event`, `sas_phy_disconnected`). It calls `asd_update_port_links()` in `aic94xx_seq.c` to update DDB 0.

Risks: many paths run in tasklet/IRQ context and allocate with `GFP_ATOMIC`; missed EDB invalidation can starve event buffers. Port formation relies on SAS address matching and lock discipline. Special sequencer requests walk `seq.pend_q` and abort tasks asynchronously, so races with normal completion are a key risk.

Test signals: hotplug/unplug, OOB error, hard reset primitive, broadcast change, spinup-hold, link-reset retry exhaustion, libsas phy control operations, and repeated empty-buffer recycling. Instrumented tests should watch `frame_rcvd_size`, `phy_mask`, LED changes, and absence of EDB leaks.
