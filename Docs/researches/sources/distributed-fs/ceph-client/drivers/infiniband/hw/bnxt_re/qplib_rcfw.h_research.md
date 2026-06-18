# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/qplib_rcfw.h

## Purpose
`qplib_rcfw.h` declares the firmware command channel ABI used by qplib slow and fast paths. It defines CMDQ and CREQ slot sizes, BAR offsets, command-slot accounting helpers, cookie flags, firmware state flags, command/response shadow entries, side buffers, QP lookup nodes, RCFW context structures, and the exported RCFW management API.

## Important APIs, types, and functions
Important structures are `bnxt_qplib_cmdqe`, `bnxt_qplib_crsbe`, `bnxt_qplib_crsqe`, `bnxt_qplib_rcfw_sbuf`, `bnxt_qplib_qp_node`, `bnxt_qplib_cmdq_mbox`, `bnxt_qplib_cmdq_ctx`, `bnxt_qplib_creq_db`, `bnxt_qplib_creq_stat`, `bnxt_qplib_creq_ctx`, `bnxt_qplib_rcfw`, and `bnxt_qplib_cmdqmsg`. Inline helpers prepare command headers, compute CMDQ pages, get and set command slots, fill `cmdqmsg`, and map QP ID to the lookup table index. It declares channel allocation, enable, IRQ, send-message, init/deinit, side-buffer, and QP-error APIs.

## Control flow
Callers build a firmware request, call `bnxt_qplib_rcfw_cmd_prep()`, wrap buffers with `bnxt_qplib_fill_cmdqmsg()`, and submit through `bnxt_qplib_rcfw_send_message()`. The implementation uses `bnxt_qplib_cmdqmsg` fields to copy request bytes to CMDQ slots, direct side-buffer DMA responses, and copy CREQ command status back to the supplied response object. QP async events use `map_qp_id_to_tbl_indx()` to locate qplib QP handles.

## State and persistence
The header describes volatile in-memory channel state: command queue producer/consumer, waitqueue, firmware flags, `last_seen`, CREQ ring state, per-cookie response records, QP table, and inflight command throttle. BAR offsets and command constants are hardware ABI values and must match firmware. `HWRM_VERSION_*` constants gate features used by other files.

## Dependencies and integration points
It includes `qplib_tlv.h` for TLV command sizing and depends on `roce_hsi.h` command structures through including C files. It is consumed by main initialization, qplib fast path, qplib slow path, resource manager, and hardware counters.

## Risks
Cookie and table sizing are central correctness points: `RCFW_MAX_COOKIE_VALUE` assumes CMDQ depth and response table size remain aligned. `map_qp_id_to_tbl_indx()` reserves the last table slot for QP1 and hashes all other QPs by modulo `qp_tbl_size - 2`; collisions are possible unless firmware/user allocation guarantees are compatible with this simple mapping. Slot helpers mutate `cmd_size`, so they must be called in the expected order. Firmware flags are bit positions in an `unsigned long`; misuse can wedge all commands.

## Test signals
Compile tests should include TLV and non-TLV command users. Unit-style checks can validate command slot counts, page-size calculations, cookie masking, QP1 table index mapping, side-buffer size rounding, and initialization flags. Integration tests should pair this header with `qplib_rcfw.c` timeout, interrupt, and firmware-init paths.
