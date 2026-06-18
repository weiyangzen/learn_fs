# sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/57xx_iscsi_hsi.h

## Purpose

`57xx_iscsi_hsi.h` is the iSCSI host/firmware interface layout header. It defines endian-aware C structures for firmware send-queue work entries, completion-queue entries, kernel work/completion queue entries, buffer descriptors, connection offload/update/destroy requests, and iSCSI protocol message variants.

## Important APIs, Types, and Functions

There are no functions. Core ABI structures include `struct iscsi_bd`, `struct bnx2i_cmd_request`, `struct bnx2i_cmd_response`, `struct bnx2i_fw_mp_request`, `struct bnx2i_cleanup_request`, `struct bnx2i_cleanup_response`, `struct iscsi_kcqe`, `struct iscsi_kwqe_header`, `struct iscsi_kwqe_init1`, `struct iscsi_kwqe_init2`, `struct iscsi_kwqe_conn_offload1/2/3`, `struct iscsi_kwqe_conn_update`, `struct iscsi_kwqe_conn_destroy`, `struct bnx2i_login_request/response`, `struct bnx2i_logout_request/response`, `struct bnx2i_nop_in_msg`, `struct bnx2i_nop_out_request`, `struct bnx2i_reject_msg`, `struct bnx2i_tmf_request/response`, `struct bnx2i_text_request/response`, and unions `iscsi_kwqe`, `iscsi_request`, and `iscsi_response`.

Most structures include bit-mask macros colocated with fields, such as ITT index/type fields, final/read/write flags, digest/update flags, response residual flags, connection-update negotiation flags, and page-size/layer-code fields.

## Control Flow

No executable flow exists, but the structures define the runtime data path. `bnx2i_hwi.c` casts SQ memory to request structures before ringing doorbells and casts CQ memory to response structures when KCQ notifications report new completions. The KWQE structures are submitted through CNIC to initialize firmware, offload connections, update negotiated parameters, and destroy contexts.

## State and Persistence Behavior

The header stores no state itself. Its layouts describe DMA-shared state between host and firmware, so field order, width, alignment, and endian-specific placement are effectively persistent ABI contracts across hardware generations.

## Dependencies and Integration Points

The file depends on fixed-width Linux integer types and compile-time `__BIG_ENDIAN`/`__LITTLE_ENDIAN` selection. It is included via `bnx2i.h`. It integrates with libiscsi headers indirectly because runtime code copies between standard iSCSI headers and these firmware-specific WQEs/CQEs.

## Risks and Edge Cases

Endian branches duplicate many fields and masks; a field-order mismatch on one endian target can silently corrupt firmware messages. Several macros are repeated for request and response variants with the same names, so include ordering and local context matter. Flexible protocol state is compressed into packed bit fields, making wrong shifts difficult to diagnose. Runtime code often casts raw queue memory to these types, so size or alignment changes can break real hardware without compiler errors.

## Test Signals

Useful signals include compile testing on little and big endian, firmware init/offload/update/destroy success, successful login/text/logout/NOP/TMF/SCSI command exchange, residual and sense-data handling, protocol error KCQE decoding, and structure size/alignment audits against the firmware specification.
