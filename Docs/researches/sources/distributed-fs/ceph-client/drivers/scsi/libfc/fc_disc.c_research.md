# sources/distributed-fs/ceph-client/drivers/scsi/libfc/fc_disc.c

Purpose: implements libfc target discovery for FC-4/FCP ports, including full fabric name-server scans, RSCN handling, single-port rediscovery, retry, and remote-port login/logoff decisions.

Important APIs and functions: `fc_disc_init()` initializes mutex, delayed work, and rport list. `fc_disc_config()` installs transport-template callbacks for start/stop/final-stop/request receive. Internally, `fc_disc_start()` and `fc_disc_restart()` launch discovery; `fc_disc_gpn_ft_req()` sends GPN_FT through `elsct_send`; `fc_disc_gpn_ft_resp()` parses multi-frame CT responses; `fc_disc_single()` and `fc_disc_gpn_id_req()` handle RSCN port-specific checks; `fc_disc_done()` reconciles rport generations.

Control flow: full discovery increments nonzero odd `disc_id`, sends GPN_FT for FCP, parses returned FIDs/WWPNs, creates or updates rports with the current generation, and on completion logs in current rports or logs off stale ones. RSCN validates payload pages, accepts the ELS, builds a temporary list of changed port IDs for GPN_ID when possible, and falls back to full rediscovery for area/domain/fabric notifications or allocation/error cases. Errors retry up to three times with delay, treating name-server “FC-4 type not registered” as success.

State and persistence: `struct fc_disc` holds `pending`, `requested`, retry count, generation `disc_id`, partial GPN_FT record buffer, sequence count, delayed work, callback, and rport list. State is live only and protected by `disc_mutex`.

Dependencies and integration: depends on libfc local-port readiness, ELS/CT transport, FC name-server structures, rport lifecycle, delayed work, and libfc locking order.

Risks and test signals: partial CT response parsing, discovery restart during callbacks, and rport kref handling are high-risk. Test RSCN malformed frames, full and partial GPN_FT sequences, timeout/retry exhaustion, zoning rejection, WWPN change on same FCID, stop/final-stop flushing, and lockdep for disc/rport/lport ordering.
