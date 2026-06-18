# sources/distributed-fs/ceph-client/include/uapi/scsi/fc/fc_fs.h

## Purpose
`fc_fs.h` defines Fibre Channel Framing and Signalling wire constants: the FC frame header layout, routing-control values, well-known fabric IDs, frame type values, exchange ID bounds, frame-control bits, basic-link-service accept/reject payloads, port/fabric reject codes, and default timeout values. It is the foundational UAPI header used by FC protocol parsing and frame construction.

## Important APIs, Types, and Constants
`struct fc_frame_header` is the core 24-byte FC frame header, with `FC_FRAME_HEADER_LEN`, `FC_MAX_PAYLOAD`, `FC_MAX_FRAME`, and minimum payload/frame constants documenting expected sizes. `enum fc_rctl` and `FC_RCTL_NAMES_INIT` identify data, ELS, FC-4 ELS, optional headers, basic link service, and link-control routing categories.

`enum fc_well_known_fid` defines fabric service addresses such as broadcast, FLOGI, fabric controller, directory server, management server, multicast server, and domain manager base. `enum fc_fh_type` and `FC_TYPE_NAMES_INIT` identify payload protocols including BLS, ELS, IP over FC, SCSI FCP, FC-CT, ILS, and FC-NVME.

Exchange and sequence semantics are represented by `FC_XID_UNKNOWN`, `FC_XID_MIN/MAX`, and `FC_FC_*` frame-control bit masks. BLS response structures include `struct fc_ba_acc`, `struct fc_ba_rjt`, `enum fc_ba_rjt_reason`, and `enum fc_ba_rjt_explan`. Port/fabric rejects use `struct fc_pf_rjt` and `enum fc_pf_rjt_reason`. Default timing uses `FC_DEF_E_D_TOV` and `FC_DEF_R_A_TOV`.

## Control Flow and State
There is no executable code. Runtime control flow is frame parsing: consumers inspect `fh_r_ctl` and `fh_type` to dispatch payloads to BLS, ELS, FC-CT, FCP, NVMe-FC, or other handlers; use `fh_f_ctl` bits to decide sequence/exchange state and acknowledgements; and process BLS or reject payload structures for abort and error paths.

## State and Persistence Behavior
The header describes transient wire state: source/destination IDs, sequence IDs/counts, exchange IDs, relative offsets, acknowledgement expectations, abort ranges, and reject reasons. Persistence, if any, is in transport driver exchange tables and fabric login state, not in this header.

## Dependencies and Integration Points
It includes `<linux/types.h>` and supplies constants used by `fc_els.h`, `fc_gs.h`, `fc_ns.h`, FC transport drivers, libfc, FCoE code, BSG FC requests, packet decoders, and userspace diagnostic tools.

## Risks and Test Signals
Risks are exact ABI/wire layout changes, incorrect 24-bit FC_ID byte ordering, and mishandling the three-byte `fh_f_ctl` field as a native integer without explicit conversion. Tests should check `sizeof(struct fc_frame_header) == FC_FRAME_HEADER_LEN`, decode/encode known frame captures, verify reject-code mappings, and exercise abort/reject paths in FC transport integration tests.
