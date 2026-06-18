# sources/distributed-fs/ceph-client/net/nfc/digital_dep.c

## Purpose

`digital_dep.c` implements NFC-DEP activation and data exchange for the NFC Digital stack. It handles ATR_REQ/ATR_RES activation, optional PSL_REQ/PSL_RES speed/payload negotiation, DEP_REQ/DEP_RES transport, payload chaining, PNI tracking, ACK/NACK, ATN, RTOX timeout extension, DID checks, and initiator/target role differences.

## Important APIs, Types, and Functions

Protocol structures include `digital_atr_req`, `digital_atr_res`, `digital_psl_req`, `digital_psl_res`, and `digital_dep_req_res`. Key exported entry points are `digital_in_send_atr_req()`, `digital_in_send_dep_req()`, `digital_tg_recv_atr_req()`, and `digital_tg_send_dep_res()`.

Shared helpers include `digital_skb_push_dep_sod()`, `digital_skb_pull_dep_sod()`, `digital_send_dep_data_prep()`, `digital_recv_dep_data_gather()`, payload-size mapping helpers, initiator ACK/NACK/ATN/RTOX resend helpers, and target ACK/ATN/saved-skb helpers.

## Control Flow

Initiator activation sends ATR_REQ with NFCID3, payload-size bits, and optional general bytes. `digital_in_recv_atr_res()` validates CRC and start-of-data, extracts waiting time and remote payload size, stores remote general bytes, optionally sends PSL_REQ to switch to 424F when supported, and calls `nfc_dep_link_is_up()`.

Initiator data exchange wraps outgoing data in DEP_REQ, sets PNI, fragments if larger than `remote_payload_max`, saves a copy for retransmission, and sends. `digital_in_recv_dep_res()` validates SOD/CRC/header/DID/NAD/PNI, handles I-PDU data and chained response gathering, handles ACKs by sending the next chained fragment, rejects NACK responses, replies to RTOX requests, retransmits saved skbs on ATN, and retries NACK/ATN on timeout or I/O errors.

Target activation receives ATR_REQ, determines RF technology from SOD, validates DID and payload size, configures activated framing, sends ATR_RES with local general bytes and payload capabilities, notifies NFC core target mode activation, and then listens for PSL or DEP. PSL requests can reconfigure RF technology and framing before continuing DEP receive.

Target data exchange receives DEP_REQ, validates DID/NAD/PNI, gathers chained input with ACKs, passes completed data to `nfc_tm_data_received()`, sends DEP_RES responses from NFC core, handles incoming ACK/NACK for chained target responses, and handles ATN by resending saved data or sending an ATN response.

## State and Persistence Behavior

The file mutates persistent `nfc_digital_dev` fields: `local_payload_max`, `remote_payload_max`, `dep_rwt`, `curr_nfc_dep_pni`, `curr_rf_tech`, `curr_protocol`, `did`, `saved_skb`, `chaining_skb`, `data_exch`, `nack_count`, and `atn_count`. `saved_skb` preserves the last sent PDU for retransmission. `chaining_skb` stores remaining outgoing data or accumulated incoming data across multiple command completions.

## Dependencies and Integration Points

It depends on digital core command dispatch and CRC function pointers, NFC core DEP and target-mode notifications, LLCP general bytes through core APIs, and RF/framing configuration callbacks in the digital driver. `digital_technology.c` discovers NFC-DEP-capable targets and starts target listening before this file takes over activation.

## Risks and Edge Cases

PNI sequencing, saved-skb lifetime, and chained skb ownership are the highest-risk areas. Error paths must free `data_exch`, `saved_skb`, and `chaining_skb` exactly once. DID and NAD handling is intentionally restrictive. Payload-size negotiation must reject invalid values. RTOX multiplication is bounded by the max waiting time. Some code paths pass `NULL` callback contexts in target mode, so helper behavior must match role.

## Test Signals

Exercise NFC-DEP initiator and target activation, ATR with and without general bytes, PSL to 424F, chained payloads in both directions, ACK/NACK retries, timeout ATN behavior, RTOX handling, DID mismatch rejection, CRC failure, and unregister during pending DEP exchange.
