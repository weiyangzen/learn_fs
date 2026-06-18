# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funcore/fun_hci.h

## Purpose
Defines the host-controller interface wire format for Fungible devices. It contains admin opcodes, request/response common headers, resource create/destroy/read/write commands, queue creation descriptors, port commands, RSS/VI/Ethernet commands, software upgrade, kTLS, data operation descriptors, Ethernet Tx/Rx descriptors, CQE metadata, and ADI configuration.

## Important APIs, Types, And Functions
Core structures include `fun_admin_req_common`, `fun_admin_rsp_common`, `fun_admin_epcq_req`, `fun_admin_epsq_req`, `fun_admin_port_req/rsp`, `fun_admin_rss_req`, `fun_admin_vi_req`, `fun_admin_eth_req`, `fun_admin_swu_req/rsp`, `fun_admin_ktls_*`, `fun_req_common`, `fun_rsp_common`, `fun_cqe_info`, `fun_eth_tx_req`, and `fun_eth_cqe`. Macros such as `FUN_ADMIN_REQ_COMMON_INIT2`, `FUN_ADMIN_EPCQ_CREATE_REQ_INIT`, `FUN_ADMIN_EPSQ_CREATE_REQ_INIT`, and many field extractors centralize endian packing.

## Control Flow
Other sources instantiate these structs, fill them through init macros, submit them on admin or I/O queues, then parse responses by common header and subop union. Queue creation commands are issued by `fun_queue.c`; generic resource and bind commands by `fun_dev.c`; port/RSS/VI/Ethernet/ADI/kTLS command formats are consumed by the Ethernet driver.

## State And Persistence
This header defines serialized device protocol state, not storage. Almost every multi-byte field is big-endian because it is sent to or received from device firmware. Data operation descriptors describe immediate, gather, scatter, SGL, and RQ-buffer data movement.

## Dependencies And Integration Points
Depends on Linux integer/endian helpers being available to consumers. It integrates the core queue/admin layer with funeth features: port capabilities/speed/FEC, RSS tables, Ethernet offloads, Rx checksum classification, TLS offload, VF ADI attributes, and firmware upgrade handles.

## Risks
Protocol structs are packed by convention through fixed field types and unions; any size or endian mistake breaks firmware compatibility. Flexible arrays require callers to allocate exact sizes and set `len8` correctly. The file has broad blast radius because many drivers share the same constants. Unknown firmware revisions may add opcodes or fields not represented here.

## Test Signals
Build-time size/offset checks would be valuable. Runtime signals include successful admin queue creation, port create/read/write, RSS creation, VI/Eth creation, queue creation, kTLS setup, and parsing of Rx CQEs/offload classifications with known firmware responses.
