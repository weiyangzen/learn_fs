# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_bsg.c

Purpose: handles iSCSI BSG host-vendor commands for qla4xxx management operations.

Important APIs/functions: `qla4xxx_bsg_request()` dispatches `ISCSI_BSG_HST_VENDOR` to `qla4xxx_process_vendor_specific()`. Vendor handlers cover flash read/update, ACB state, NVRAM read/update, restore defaults, get ACB, generic diagnostic mailbox commands, and loopback diagnostics with pre/post port configuration.

Control flow: each operation obtains the `scsi_qla_host`, rejects offline PCI channels or reset-active adapters, validates adapter family and payload length, copies data between BSG scatterlists and coherent DMA buffers when needed, calls firmware/mailbox helper APIs, sets `DID_OK`, `DID_ERROR`, or `DID_TIME_OUT`, and completes the BSG job. Loopback diagnostics temporarily set internal/external loopback, wait for IDC and link completions, execute mailbox diagnostics, then restore DCBX/default port config.

State and persistence: flash/NVRAM/default updates persist on the adapter. Runtime state includes `flash_state`, reset flags, loopback flags, IDC/link completion flags, firmware state, and reply payload lengths.

Dependencies and integration: depends on iSCSI BSG request/reply layouts, SCSI host private data, PCI DMA, qla4xxx mailbox and flash/NVRAM/ACB helpers, 83xx port config helpers, and qla4xxx reset-state predicates.

Risks: vendor command fields are trusted as offsets/options, concurrent flash state is only guarded by `flash_state`, mailbox diagnostics can be disruptive, loopback restore failures schedule adapter reset, and all paths must call `bsg_job_done()` exactly when ownership completes. Test signals include invalid command dispatch, short payload rejection, reset-active `-EBUSY`, DMA allocation failure, max NVRAM bounds, flash operation serialization, diagnostic mailbox replies, and loopback timeout/restore behavior.
