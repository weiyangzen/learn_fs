# sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_dbf.c

Purpose: implements zfcp debug feature tracing for HBA/FSF events, recovery, SAN requests/responses, SCSI command/error handling, and payload records.

Important APIs and functions: module parameters `dbfsize` and `dbflevel` size and filter debug areas. HBA tracing includes `zfcp_dbf_hba_fsf_res()`, `zfcp_dbf_hba_fsf_fces()`, `zfcp_dbf_hba_fsf_reqid()`, `zfcp_dbf_hba_fsf_uss()`, `zfcp_dbf_hba_bit_err()`, and `zfcp_dbf_hba_def_err()`. Recovery tracing includes `zfcp_dbf_rec_trig()`, `zfcp_dbf_rec_trig_lock()`, `zfcp_dbf_rec_run_lvl()`, and `zfcp_dbf_rec_run_wka()`. SAN/SCSI tracing includes `zfcp_dbf_san_req()`, `zfcp_dbf_san_res()`, `zfcp_dbf_san_in_els()`, `zfcp_dbf_scsi_common()`, and `zfcp_dbf_scsi_eh()`. Adapter registration uses `zfcp_dbf_adapter_register()` and `zfcp_dbf_adapter_unregister()`.

Control flow: each trace path checks debug level where useful, locks the matching per-area spinlock, zeroes a reusable record buffer, fills common and event-specific fields, optionally emits payload chunks through `zfcp_dbf_pl_write()`, and calls `debug_event()`. SAN response logging caps GPN_FT directory-service payloads after the last advertised entry to avoid logging stale scatterlist data. Adapter registration allocates one `struct zfcp_dbf`, initializes locks, registers rec/hba/pay/san/scsi debug areas, sets views and levels, and attaches it to the adapter.

State and persistence: per-adapter debug state contains debug area handles, reusable record buffers, and spinlocks. Debug records are retained in s390 debug feature buffers sized by module parameter, not persistent storage. Payload counters split long records across multiple debug events.

Dependencies and integration: depends on s390 `debug_register()` infrastructure, zfcp FSF/QDIO/FC/SCSI data structures, scatterlists, Fibre Channel CT/GPN_FT formats, adapter ERP locks, and SCSI command/FCP response layouts.

Risks: trace functions run in error and interrupt-adjacent contexts, so locking and bounded copying are important. Record buffers are shared per adapter and must be protected by the correct spinlock. Payload copying from scatterlists assumes valid mapped entries. GPN_FT cap logic is format-specific; incorrect matching can over-truncate or expose stale response bytes. Debug registration failure must unregister all earlier areas.

Test signals: debug area registration/unregistration, dbflevel filtering, long payload chunking and counters, FSF response payload log offsets, unsolicited status with and without payload, recovery traces with ERP lock held and lock wrapper, SAN request/response payloads including GPN_FT cap cases, SCSI command and TMF traces with/without FSF response, and failure injection for partial debug area registration.
