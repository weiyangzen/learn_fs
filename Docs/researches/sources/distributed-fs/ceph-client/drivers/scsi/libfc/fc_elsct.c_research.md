# sources/distributed-fs/ceph-client/drivers/scsi/libfc/fc_elsct.c

Purpose: provides the libfc helper for sending ELS and CT requests with the proper payload encoding, FC header fields, exchange allocation, response callback, and timeout.

Important APIs and functions: `fc_elsct_send()` is exported and selected into `lport->tt.elsct_send` by `fc_elsct_init()`. `fc_els_resp_type()` turns ELS/CT response frames or encoded exchange errors into diagnostic strings.

Control flow: `fc_elsct_send()` classifies opcodes in the ELS range and calls `fc_els_fill()`, otherwise calls `fc_ct_fill()`, allowing CT fill to rewrite destination to directory or management service. On encoding failure it frees the frame. On success it fills the FC header with request F_CTL and sends through `fc_exch_seq_send()`, which creates the exchange and arms the response timeout. `fc_els_resp_type()` inspects `IS_ERR` values, FC frame type, ELS opcode, or CT command to return accept/reject/timeout/unknown descriptions.

State and persistence: no standalone state; state is carried in the frame, local port, exchange manager, callback argument, and timeout.

Dependencies and integration: depends on `fc_encode.h`, FC ELS/GS/NS headers, `fc_fill_fc_hdr()`, and exchange manager APIs. Used by discovery, local-port login, remote-port flows, and FDMI/name-server registration code.

Risks and test signals: opcode classification must stay aligned with FC definitions, and CT destination rewrite is essential for management versus directory service. Test each ELS helper, common CT NS and FDMI opcodes, frame-free on invalid op, timeout callback, and response-type strings for short CT frames.
