# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcbuild.h

## Purpose
`bfa_fcbuild.h` declares the FC frame-building/parsing API implemented by `bfa_fcbuild.c` and provides small protocol utility helpers. It is the interface FCS and login/discovery modules use to construct ELS, BLS, CT, name-server, management-server, FDMI, and logout frames.

## Important APIs and Types
Utility macros and inlines include `wwn_is_equal`, `fc_roundup`, `fc_get_ctresp_pyld_len`, `fc_rpsc_operspeed_to_bfa_speed`, and `fc_bfa_speed_to_rpsc_operspeed`. `enum fc_parse_status` standardizes parser results beyond simple success/failure for length, accept, WWN, receive-size, FCP type, and process-associator validation failures. `struct fc_templates_s` names the major frame templates. Declarations cover all frame builders for FLOGI/PLOGI/PRLI/ADISC/LOGO/SCR/RNID/RPSC/name-server/FDMI/GMAL/GFN/BA_ACC/PRLO/TPRLO plus parser APIs.

## Control Flow and State
Callers generally allocate or point to an FC header and payload buffer, call the relevant builder, transmit the returned byte count through an FC exchange, then parse the response with the matching parser where one exists. Speed conversion helpers bridge `enum bfa_port_speed` from service definitions and RPSC on-wire speed values from `bfa_fc.h`.

## State and Persistence Behavior
The header itself owns no mutable state. It exposes `fcbuild_init`, which initializes static templates inside the implementation. Frame builders carry identity/configuration state supplied by callers, such as WWNs, PIDs, symbolic names, roles, FC4 features, and speed info.

## Dependencies and Integration Points
It includes `bfad_drv.h`, `bfa_fc.h`, and `bfa_defs_fcs.h`, binding Linux driver types, wire-format structs, and FCS role definitions. The API is a narrow integration point between higher-level FCS state machines and lower-level FCXP send paths.

## Risks and Test Signals
Risks include callers passing undersized payload buffers, forgetting `fcbuild_init`, mismatch between declared builders and implementation coverage, ambiguous endian expectations for `u16` versus `__be16` exchange IDs, and parse statuses not being handled distinctly. Test signals include compile coverage for every declared builder, golden frame fixtures, speed conversion round-trips, response length underflow for `fc_get_ctresp_pyld_len`, and negative parser status propagation.
