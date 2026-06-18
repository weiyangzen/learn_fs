# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fdls_fc.h

## Purpose

`fdls_fc.h` defines Fibre Channel and FCoE constants, frame classification macros, field accessors, and packed wire-format structures used by FNIC FDLS and FIP code. It is the shared vocabulary for building and decoding FLOGI/PLOGI, ELS accept/reject, ADISC, RLS, ABTS, PRLI, name-server CT requests, FDMI requests, GPN_FT responses, RSCN, LOGO, and Ethernet/FCoE header offsets.

## Important APIs, Types, and Definitions

- Service parameter and FC constants: FNIC FCP service parameters, unassigned OX/RX IDs, ELS/FCP/ABTS F_CTL values, FC-PH version, buffer-to-buffer credit, default receive data field size, frame-size limits, timeout unit conversion, and PRLI target function bit.
- `FNIC_LOGI_*` macros: get/set FLOGI/PLOGI common service parameters, port name, node name, R_A_TOV, E_D_TOV, and receive data field size.
- `FNIC_STD_SET_*` and `FNIC_STD_GET_*` macros: write/read FC frame header fields, FC IDs, OX/RX IDs, WWNs, and CT commands using the proper unaligned big-endian helpers where needed.
- `FNIC_FC_FRAME_*` macros: classify unsolicited frames, solicited data/control replies, F_CTL patterns, FC type, CS_CTL, ELS, BLS, and FC-GS frames.
- Packed structures such as `fc_std_flogi`, `fc_std_els_acc_rsp`, `fc_std_els_rjt_rsp`, `fc_std_els_adisc`, `fc_std_rls_acc`, `fc_std_abts_ba_acc`, `fc_std_abts_ba_rjt`, `fc_std_els_prli`, `fc_std_rpn_id`, `fc_std_fdmi_rhba`, `fc_std_fdmi_rpa`, `fc_std_rft_id`, `fc_std_rff_id`, `fc_std_gpn_ft`, `fc_gpn_ft_rsp_iu`, `fc_std_rls`, `fc_std_scr`, `fc_std_rscn`, and `fc_std_logo`.
- `FNIC_ETH_FCOE_HDRS_OFFSET`: offset from an Ethernet frame start to the FC header/payload after Ethernet and FCoE headers.

## Control Flow and Design Role

This header does not implement a state machine. Instead, senders in `fdls_disc.c` allocate a frame, offset to `FNIC_ETH_FCOE_HDRS_OFFSET`, cast to one of these packed structures, and fill header/payload fields with the provided macros. Receivers in FDLS validate frame type and fields with the classification macros, then cast to the appropriate structure for response-specific parsing.

## State and Persistence Behavior

There is no local state. The structures describe transient FC/FCoE frames. Their exact layout persists as an interoperability contract with fabrics, FCFs, targets, name server, management server, and the Linux FC header definitions.

## Dependencies and Integration Points

The header depends on Linux SCSI FC/FCoE UAPI headers, FC ELS/GS/NS/MS definitions, Ethernet headers, and unaligned/big-endian helpers. It is included by `fdls_disc.c`, `fip.h`, and FNIC initialization paths that need frame pool sizing. Its structures are the direct payloads passed to `fnic_send_fcoe_frame()` and parsed by `fnic_fdls_recv_frame()`.

## Risks and Edge Cases

- Many macros write multi-byte fields in big-endian FC order; using plain assignment in callers would break wire format.
- The F_CTL setters and classifiers operate on byte arrays and sometimes shift constants before writing 24-bit fields, so callers must use the expected constant form.
- Packed wire structures rely on external FC header definitions remaining compatible.
- GPN_FT response parsing depends on `struct fc_gpn_ft_rsp_iu` matching the CT response list element exactly, including the `ctrl` last-entry bit.
- `FNIC_ETH_FCOE_HDRS_OFFSET` must match the actual receive/transmit buffer layout used by frame allocation and hardware.

## Test Signals

Useful validation includes frame captures for FLOGI/PLOGI/PRLI/SCR/RPN/RFT/RFF/GPN_FT/FDMI/RSCN/LOGO/ADISC/RLS/ABTS, checks for correct S_ID/D_ID/OX_ID/RX_ID/F_CTL values, big-endian WWN and FCID encoding, GPN_FT multi-entry parsing, and interoperability with fabrics that send ECHO/RRQ, malformed RSCN, or different class-3 service parameter values.
