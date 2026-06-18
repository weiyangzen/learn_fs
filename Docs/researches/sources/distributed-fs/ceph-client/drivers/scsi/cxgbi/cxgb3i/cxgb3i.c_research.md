# sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb3i/cxgb3i.c

## Purpose

This file is the Chelsio T3 iSCSI offload driver. It registers as a cxgb3 offload client, exposes a libiscsi transport, creates SCSI hosts through libcxgbi, manages offloaded TCP connection setup/teardown over CPL messages, sends and receives iSCSI PDUs, and programs T3 pagepod/DDP resources.

## Important APIs, Types, And Functions

Module parameters include `dbg_level`, `cxgb3i_rcv_win`, `cxgb3i_snd_win`, `cxgb3i_rx_credit_thres`, `cxgb3i_max_connect`, and `cxgb3i_sport_base`. Important global objects are `t3_client`, `cxgb3i_host_template`, `cxgb3i_iscsi_transport`, `cxgb3i_stt`, and `cxgb3i_cpl_handlers`.

Connection transmit/control helpers include `send_act_open_req()`, `send_close_req()`, `send_abort_req()`, `send_abort_rpl()`, `send_rx_credits()`, `make_tx_data_wr()`, and `push_tx_frames()`. CPL receive handlers include `do_act_establish()`, `do_act_open_rpl()`, `do_peer_close()`, `do_close_con_rpl()`, `do_abort_req()`, `do_abort_rpl()`, `do_iscsi_hdr()`, and `do_wr_ack()`. Device/DDP lifecycle flows through `cxgb3i_ofld_init()`, `cxgb3i_ddp_init()`, `cxgb3i_dev_open()`, `cxgb3i_dev_close()`, and module init/exit.

## Control Flow

Module init registers the iSCSI transport with libcxgbi and registers `t3_client` with cxgb3. When a T3 offload device opens, `cxgb3i_dev_open()` allocates a `cxgbi_device`, fills port/PCI/MTU/transport fields, initializes DDP/pagepod resources, installs offload operation callbacks, creates HBA hosts, and captures per-port private IPv4 addresses.

Endpoint connect uses libcxgbi routing to create a `cxgbi_sock`, then `init_act_open()` updates the adapter-private IPv4 address, obtains an L2T entry, allocates an ATID, prepares an active-open CPL, initializes windows/credits/MSS, and sends `CPL_ACT_OPEN_REQ`. Establish/open-failure CPLs convert hardware status into socket state, retry connection-exists cases briefly, or fail the endpoint. Once established, queued PDUs are pushed by `push_tx_frames()`, which consumes WR credits, prepends TX_DATA WRs, updates sequence numbers, and sends through L2T.

Receive flow enters CPL handlers. `do_iscsi_hdr()` validates connection state, parses coalesced iSCSI header/DDP status trailers, sets skb control flags for digest/padding/DDP status, queues the PDU to `receive_queue`, and notifies libcxgbi. Close and abort CPLs delegate state transitions to shared `cxgbi_sock_*` helpers. DDP setup writes pagepods with ULP memory I/O WRs and configures TCB page index/digest fields.

## State And Persistence

Persistent runtime state is held in `struct cxgbi_device`, `struct cxgbi_hba`, `struct cxgbi_sock`, T3 ATID/TID tables, L2T entries, WR queues, preallocated close/abort CPL skbs, pagepod manager state in `t3dev->ulp_iscsi`, and private IPv4 fields in cxgb3 `port_info`. No disk persistence exists. Hardware state includes TCBs, offload connection ids, DDP pagepod memory, iSCSI parameter limits, and firmware/client registrations.

## Dependencies And Integration Points

The driver depends on cxgb3 Ethernet offload APIs (`t3cdev`, CPL handlers, L2T, ATID/TID management, adapter control calls), `libcxgbi`, `libiscsi_tcp`, SCSI host/transport templates, Chelsio pagepod library, Linux networking skbs/routes, and iSCSI userspace transport operations. It is built only when Kconfig enables Chelsio T3 and iSCSI attrs.

## Risks

The connection state machine is race-sensitive: active open retry timers, abort requests/replies, close replies, and peer close can arrive in different orders. `abort_status_to_errno()` takes `need_rst` but does not use it, suggesting either stale API or incomplete reset-status handling. `do_iscsi_hdr()` assumes coalesced CPL layout and aborts on malformed lengths; firmware or skb format drift can kill connections. DDP/pagepod programming is asynchronous and can partially fail under skb allocation pressure. Private IPv4 address mutation in netdev private data must stay synchronized with HBA/session setup.

## Test Signals

Signals include module load/unload, cxgb3 client add/remove, HBA creation per port, login/logout through open-iscsi, active-open errors for ARP miss/TCAM full/connection exists, high-throughput TX WR credit recovery, RX digest/DDP error reporting, abort/close races, adapter reset events, DDP enabled/disabled paths, pagepod allocation/tagmask correctness, and cleanup of ATID/TID/L2T/CPL skb resources.
