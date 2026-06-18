# sources/distributed-fs/ceph-client/drivers/scsi/libfc/fc_encode.h

Purpose: inline construction library for libfc ELS, name-server CT, and FDMI management CT request payloads.

Important APIs and types: `FC_FCTL_REQ` and `FC_FCTL_RESP` define common frame-control flags. `struct fc_ct_req` overlays supported CT request payloads. Helpers include `fc_adisc_fill()`, `fc_ct_hdr_fill()`, `fc_ct_ns_fill()`, `fc_ct_ms_fill()`, `fc_ct_fill()`, `fc_plogi_fill()`, `fc_flogi_fill()`, `fc_fdisc_fill()`, `fc_logo_fill()`, `fc_rtv_fill()`, `fc_rec_fill()`, `fc_prli_fill()`, `fc_scr_fill()`, and dispatcher `fc_els_fill()`.

Control flow: ELS helpers zero the frame payload and populate command-specific fields from `fc_lport` identity, service parameters, exchange IDs, and timeout values. Name-server CT supports GPN_FT/GPN_ID and registration of FC-4 type, features, node name, port symbolic name, and node symbolic name. FDMI CT builds RHBA, RPA, DPRT, and DHBA payloads with many fixed-length attributes from FC host sysfs attributes, OS name/release, and port state. `fc_ct_fill()` chooses management service for `FC_FID_MGMT_SERV`, otherwise directory service.

State and persistence: functions write only into the provided frame payload. They snapshot lport/host fields such as WWPN, WWNN, port ID, speed, symbolic names, and FDMI version.

Dependencies and integration: depends on FC protocol headers, unaligned big-endian helpers, `fc_frame_payload_get()`, SCSI FC host attribute accessors, and `init_utsname()`.

Risks and test signals: payload length math and fixed FDMI attribute stepping are easy to break. Test buffer sizing for FDMI v1/v2, symbolic-name truncation and zero-fill, endian encoding of IDs/WWNs, invalid opcode returns, and that ELS/CT headers match expected R_CTL/type values when sent through `fc_elsct_send()`.
