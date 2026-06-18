# `sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_fc.c`

## Purpose

`zfcp_fc.c` implements Fibre Channel service logic above FSF transport: FC event posting, name-server CT requests, incoming ELS handling, remote-port discovery and validation, ADISC link tests, WKA generic-service port lifecycle, symbolic port-name synchronization, and FC BSG CT/ELS passthrough. It bridges the zfcp hardware command layer with Linux FC transport semantics.

## Important APIs And Functions

- Module parameters:
  - `no_auto_port_rescan` disables automatic port rescans unless inverse conditional scan is requested.
  - `port_scan_backoff` and `port_scan_ratelimit` throttle and jitter port scanning.
- Port scan helpers:
  - `zfcp_fc_port_scan_backoff()`, `zfcp_fc_conditional_port_scan()`, and `zfcp_fc_inverse_conditional_port_scan()`.
  - `zfcp_fc_scan_ports()` sends GPN_FT through the directory service WKA port and attaches/removes ports.
- FC event handling:
  - `zfcp_fc_enqueue_event()` allocates an event in IRQ context and queues work.
  - `zfcp_fc_post_event()` posts queued events via `fc_host_post_event()`.
- WKA port lifecycle:
  - `zfcp_fc_wka_port_get()` opens a WKA port on demand and increments refcount.
  - `zfcp_fc_wka_port_put()` schedules delayed close after refcount drops to zero.
  - `zfcp_fc_wka_port_offline()` sends close-port after a short idle delay.
  - `zfcp_fc_wka_ports_force_offline()`, `zfcp_fc_gs_setup()`, and `zfcp_fc_gs_destroy()` initialize/tear down generic-service WKA ports.
- Incoming ELS:
  - `zfcp_fc_incoming_els()` traces ELS and dispatches PLOGI, LOGO, and RSCN.
  - RSCN handling tests matching known ports and triggers scans; PLOGI/LOGO force reopen by WWPN.
- Name-server lookup:
  - `zfcp_fc_ns_gid_pn_request()` sends GID_PN for a port's WWPN.
  - `zfcp_fc_port_did_lookup()` runs in workqueue, updates D_ID, and reopens or fails the port.
  - `zfcp_fc_trigger_did_lookup()` queues that work with a port device reference.
- Link test:
  - `zfcp_fc_test_link()` queues `zfcp_fc_link_test_work()`.
  - `zfcp_fc_adisc()` sends ADISC to cached D_ID and clears D_ID before send to force fresh lookup on failure.
  - `zfcp_fc_adisc_handler()` validates WWPN/open state and triggers forced or normal port recovery as needed.
- Discovery:
  - `zfcp_fc_eval_gpn_ft()` parses GPN_FT response pages, skips WKA/local ports, enqueues new ports, reopens them, waits for ERP, and unregisters invalid no-escape ports.
- Symbolic name:
  - `zfcp_fc_sym_name_update()` reads current symbolic name with GSPN_ID and, in NPIV mode, writes a Linux-specific name with RSPN_ID.
- BSG:
  - `zfcp_fc_exec_bsg_job()` dispatches FC_BSG ELS/CT jobs.
  - `zfcp_fc_exec_els_job()` resolves rport or host D_ID and sends ELS.
  - `zfcp_fc_exec_ct_job()` opens the proper WKA port and sends CT.
  - `zfcp_fc_timeout_bsg_job()` returns `-EAGAIN` because hardware timeout tracking owns the timeout.

## Control Flow

Adapter recovery schedules scans and name updates after a successful open. Port scanning first rate-limits the next scan time, opens the directory-service WKA port, allocates SG pages for GPN_FT, retries transient name-server rejections, evaluates returned ports, and releases the WKA port. New ports are marked `NOESC` while being validated; ports still no-escape and without class/unit evidence after the scan are moved to a remove list, shut down, and unregistered.

Incoming ELS from FSF status-read buffers can trigger targeted recovery. RSCN maps FC address-format ranges to masks and ADISC-tests matching known ports; broad RSCNs also retry failed ports with missing D_ID and schedule a scan. PLOGI/LOGO find by WWPN and force reopen.

WKA ports are demand-opened with a mutex-protected state machine (`OFFLINE`, `OPENING`, `ONLINE`, `CLOSING`) and wait queues for open/close completion signaled by FSF handlers. Refcounting keeps WKA ports open across CT users; delayed close avoids churn.

## State And Persistence

Persistent runtime state includes adapter scan throttle (`next_port_scan`), `adapter->events` list and lock, WKA port state/refcount/handle/work, port D_ID/WWNN/capability fields, and work items for GID_PN/ADISC/rport. FC request objects are allocated from `zfcp_fc_req_cache` or mempools and may be freed in async handlers.

## Dependencies And Integration

The file depends on Linux workqueues, kmem cache, random backoff, BSG, libfc/FC ELS/NS structures, SCSI FC transport, FSF CT/ELS APIs, ERP recovery APIs, zfcp debug tracing, and adapter workqueue infrastructure. It is called by FSF status-read handling for incoming ELS and by ERP after adapter recovery.

## Risks And Edge Cases

- D_ID caching is inherently racy. ADISC clears `port->d_id` before sending to force lookup if the port changes, but comments note open-port response data can be stale.
- WKA open/close waits depend on FSF handlers always waking the proper wait queue.
- Event allocation uses `GFP_ATOMIC`; allocation failure silently drops FC events.
- GPN_FT response parsing spans chained SG pages; page/entry arithmetic must stay aligned with `ZFCP_FC_GPN_FT_ENT_PAGE`.
- `zfcp_fc_sg_setup_table()` error cleanup passes the current SG pointer with count of already allocated entries; changes here need careful leak testing.
- BSG job timeout units are converted with `job->timeout / HZ`; very small timeouts could become zero.
- `zfcp_fc_job_wka_port()` returns NULL for unsupported CT GS types; callers must not put a NULL WKA port.

## Test Signals

Useful signals include:

- Port scan attaches new non-local, non-WKA FCP ports and unregisters stale no-escape ports.
- RSCN/PLOGI/LOGO incoming ELS paths trigger ADISC, forced reopen, or rescan as expected.
- WKA port refcount opens once for concurrent users and closes after the delayed idle path.
- GID_PN lookup sets D_ID and reopens the target port, or marks it ERP failed if no D_ID is found.
- BSG CT jobs release WKA refs on completion and ELS jobs choose rport D_ID or host-request D_ID correctly.
- NPIV symbolic name update reads GSPN, appends device/node information, and sends RSPN.
