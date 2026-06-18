# sources/distributed-fs/ceph-client/net/nfc/digital_technology.c

## Purpose

`digital_technology.c` implements NFC Digital RF technology discovery and listen flows outside the NFC-DEP transport itself. It probes initiator technologies NFC-A, NFC-B, NFC-F, and ISO15693, performs anti-collision and activation steps for Type 1/2/3/4/5 style targets, handles MIFARE response quirks, and implements target-mode listening responses for NFC-A and NFC-F before handing off to NFC-DEP activation.

## Important APIs, Types, and Functions

Initiator entry points are `digital_in_send_sens_req()`, `digital_in_send_sensb_req()`, `digital_in_send_sensf_req()`, `digital_in_send_iso15693_inv_req()`, and `digital_in_recv_mifare_res()`. ISO-DEP helpers are `digital_in_iso_dep_pull_sod()` and `digital_in_iso_dep_push_sod()`.

NFC-A anti-collision uses `digital_in_send_sdd_req()`, `digital_in_recv_sdd_res()`, `digital_in_send_sel_req()`, `digital_in_recv_sel_res()`, `digital_in_send_rats()`, and `digital_in_recv_ats()`. NFC-B activation uses SENSB and ATTRIB helpers. Target-mode functions include `digital_tg_listen_nfca()`, `digital_tg_listen_nfcf()`, `digital_tg_recv_sens_req()`, `digital_tg_recv_sensf_req()`, `digital_tg_recv_md_req()`, and the static SENS/SDD/SEL/SENSF response builders.

## Control Flow

For NFC-A polling, the stack configures 106A short framing, sends SENS_REQ, validates SENS_RES, then either reports a Jewel target or starts SDD anti-collision. SDD responses append NFCID1 fragments after BCC validation; SEL_REQ selects cascade levels; SEL_RES decides MIFARE, NFC-DEP, or Type 4A. Type 4A sends RATS and uses ATS to set FSC before reporting ISO14443.

For NFC-B, the stack configures 106B, sends SENSB_REQ, validates the response and protocol-info bits, derives FSC, sends ATTRIB_REQ, and reports ISO14443-B after validating ATTRIB_RES. For NFC-F, it sends SENSF_REQ with length prefix and optional software CRC, parses SENSF_RES, copies NFCID2 and response data, and reports either NFC-DEP or FeliCa based on NFCID2 prefix. ISO15693 sends an inventory request and reports a Type 5 target with DSFID and UID.

Target NFC-A listen configures RF/framing, waits for SENS_REQ/ALL_REQ, sends SENS_RES, receives SDD_REQ, sends random NFCID1 SDD_RES, receives SEL_REQ, sends SEL_RES advertising NFC-DEP, and waits for ATR_REQ. Target NFC-F listen validates SENSF_REQ, sends SENSF_RES with NFC-DEP NFCID2 prefix and optional request data, then dispatches follow-up ATR or SENSF requests. MDAA/MD target paths can also use driver-assisted multi-discovery and dispatch based on reported RF technology.

## State and Persistence Behavior

This file fills `struct nfc_target` fields such as SENS_RES, SEL_RES, NFCID1, NFCID2, SENSF response, ISO15693 DSFID/UID, and supported protocol. It mutates `ddev->target_fsc`, `curr_nfc_dep_pni`, and CRC behavior indirectly through `digital_target_found()`. Target-mode response builders generate random NFCIDs for listen mode.

## Dependencies and Integration Points

The file depends on digital core command scheduling, CRC helpers, driver hardware configuration, NFC core target reporting, and NFC-DEP activation in `digital_dep.c`. ISO-DEP data exchange in `digital_core.c` calls the SOD push/pull helpers here for Type 4A/B traffic.

## Risks and Edge Cases

Protocol parsing is strict and many errors fall back to the next polling technology. NFC-A cascade and BCC handling must preserve NFCID1 length correctly. ISO-DEP does not support R-blocks, S-blocks, DID, or chaining in this implementation. MIFARE ACK versus READ response requires software CRC even with driver CRC offload. Target-mode listen often ignores request content beyond minimal validation, which is appropriate for NFC-DEP advertisement but not a full tag implementation.

## Test Signals

Test polling with Type 1, MIFARE/Type 2, FeliCa/Type 3, Type 4A, Type 4B, ISO15693, and NFC-DEP peers. Include malformed SENS/SDD/SEL/ATS/ATTRIB/SENSF/inventory responses, driver CRC offload on/off, target-mode NFC-A and NFC-F listen, and ISO-DEP APDU exchange size limits.
