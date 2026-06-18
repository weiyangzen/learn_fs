
# sources/distributed-fs/ceph-client/include/linux/nvme-fc-driver.h

Purpose: defines the low-level driver API between Fibre Channel LLDDs and the NVMe-FC host and target transports.

Important APIs/types/functions: common LS structures `nvmefc_ls_req` and `nvmefc_ls_rsp` describe DMA buffers, timeouts, private areas, and completion callbacks. Host-side types include `nvme_fc_port_info`, `nvmefc_fcp_req`, `nvme_fc_local_port`, `nvme_fc_remote_port`, and `nvme_fc_port_template`; APIs register/unregister local and remote ports, rescan remote ports, set dev-loss timeout, receive LS requests, and obtain request UUID/appid. Target-side types include `nvmet_fc_port_info`, `nvmefc_tgt_fcp_req`, `nvmet_fc_target_port`, and `nvmet_fc_target_template`; APIs register/unregister target ports, receive LS and FCP requests, invalidate hosts, and report FCP aborts.

Control flow: an LLDD registers a local host port or target port with a template of mandatory callbacks. Host transport issues LS requests and FCP I/O through LLDD callbacks, and the LLDD completes via provided `done` callbacks. Target transport accepts received LS/FCP requests from the LLDD, then calls back into the LLDD to transmit LS responses, perform read/write data movement, send responses, abort commands, and release exchange contexts.

State and persistence: port objects store static WWNN/WWPN/role numbers, dynamic port IDs/states, dev-loss timeout, and LLDD private memory allocated alongside transport objects. Request structures hold transient DMA/exchange state until completion/release.

Dependencies and integration points: depends on scatterlists, blk-mq queue maps, DMA addresses, FC BA_RJT definitions, device model, and NVMe-FC protocol structures. It integrates SCSI/FC LLDDs, NVMe host transport, NVMe target transport, block queue mapping, dev-loss recovery, discovery, and appid/UUID tagging.

Risks and test signals: risks include failing mandatory callbacks, calling `done` twice or never, using request/exchange structures after transport release, unregister races with pending LS responses, wrong transferred-length/fcp-error reporting, queue affinity mismatches, and hosthandle lifetime mistakes after invalidation. Test signals include host login/create association/create queue flows, target read/write/response flows, LS abort and FCP abort tests, remote-port dev-loss/reconnect tests, unregister with outstanding exchanges, queue mapping tests, and FC-NVMe interoperability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvme-fc-driver.h -->
