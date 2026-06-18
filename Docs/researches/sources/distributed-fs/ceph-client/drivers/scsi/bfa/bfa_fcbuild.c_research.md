# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcbuild.c

## Purpose
`bfa_fcbuild.c` implements Fibre Channel link-service, basic-link-service, CT generic-service, name-server, management-server, and FDMI frame construction helpers plus a few response parsers. It turns the wire structs from `bfa_fc.h` into initialized FC headers and payloads used by FCS/login/discovery modules.

## Important APIs and Functions
`fcbuild_init` initializes static templates for ELS requests/responses, BLS responses, BA_ACC, PLOGI, PRLI, RRQ, and FCP headers. Public builders include FLOGI/PLOGI/PLOGI ACC, PRLI/PRLI ACC, LOGO/LOGO ACC, ADISC/ADISC ACC, LS_ACC/LS_RJT, BA_ACC, PRLO ACC, RNID ACC, RPSC2, RPSC ACC, SCR, GID_PN, GPN_ID, GID_FT, RFT_ID, RFF_ID, RSPN_ID, RSNN_NN, RNN_ID, GS reject, FDMI request header, GMAL, and GFN. Parsers include `fc_plogi_parse`, `fc_prli_rsp_parse`, `fc_adisc_rsp_parse`, and `fc_logout_params_pages`.

## Control Flow and State
Most functions copy a prebuilt template or zero a payload, fill destination/source IDs, exchange IDs, command codes, and protocol fields, then return the payload length. ELS request and response builders centralize header setup; CT helpers centralize generic-service headers. `fc_plogi_x_build` handles both PLOGI request and accept by switching on ELS code. Name-server helpers build CT payloads after setting the FC header to the well-known name server; management helpers target the management server.

## State and Persistence Behavior
The file holds static in-memory templates initialized once by `fcbuild_init`; callers depend on that initialization before building frames. It does not persist state, but constructed payloads carry persistent identity data such as WWNs, symbolic names, FC4 feature registration, RNID topology records, and management-server WWN queries.

## Dependencies and Integration Points
It depends on `bfa_fcbuild.h`, `bfa_fc.h`, `bfa_defs_fcs.h`, common endian helpers, and string helpers from the driver environment. FCS modules use these builders when sending FCXP exchanges for fabric login, port login, discovery, name-server registration, RSCN registration, speed reporting, and management queries.

## Risks and Test Signals
Risks include missing `fcbuild_init`, endian mistakes around IDs/exchange ids, insufficient buffer sizing for variable-length PRLO/TPRLO/RPSC2/FDMI payloads, unchecked name truncation, role parameters ignored in some builders, and limited parser validation. Test with golden packet byte comparisons, invalid PLOGI/PRLI/ADISC responses, name truncation, multiple PRLO pages, RPSC2 pid counts, and all well-known address builders.
