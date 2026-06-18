# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/ntmp_private.h

### Purpose
`ntmp_private.h` defines private command-buffer data formats for the ENETC NETC Table Management Protocol (NTMP). It is a packing contract between ENETC driver code and NETC command BD rings: callers fill request headers and request data buffers for table add/update/query/delete operations, and parse response headers/data returned by hardware.

### Important APIs, Types, And Functions
The central type is `union netc_cbd`, which overlays the command buffer descriptor request header and response header. Request fields include DMA address, encoded request/response lengths via `NTMP_LEN()`, command bits (`NTMP_CMD_ADD`, `NTMP_CMD_UPDATE`, `NTMP_CMD_QUERY`, `NTMP_CMD_DELETE`, and query-update `NTMP_CMD_QU`), access methods (`NTMP_AM_ENTRY_ID`, `NTMP_AM_EXACT_KEY`, `NTMP_AM_SEARCH`, `NTMP_AM_TERNARY_KEY`), table id, header version, CCI/RR bits, and NPF. Response fields include matched count and encoded NTMP error/RR bits. The header also defines common request data (`struct ntmp_cmn_req_data`), query response common data (`struct ntmp_cmn_resp_query`), entry-id requests (`struct ntmp_req_by_eid`), MAC address filter table add/query buffers (`struct maft_req_add`, `struct maft_resp_query`), and RSS table update buffers (`struct rsst_req_update` with flexible `groups[]`).

### Control Flow
There is no executable control flow in the header. Runtime flow is implied: NTMP users allocate or map request/response buffers, fill `union netc_cbd.req_hdr`, select an access method and command, submit the descriptor to a NETC CBD ring, and later inspect `union netc_cbd.resp_hdr` plus table-specific response data. `FIELD_PREP()` and masks from `linux/bitfield.h` centralize bitfield packing so command producers do not hand-code shifts.

### State, Persistence, And Dependencies
The file owns no runtime state. State lives in hardware tables modified by NTMP commands and in DMA buffers described by the CBD. The on-wire/in-memory structures are little-endian and depend on `<linux/fsl/ntmp.h>` for table-specific key/config element structures such as `maft_keye_data`, `maft_cfge_data`, and RSS data semantics.

### Integration Points
This header integrates ENETC NETC command-ring code with NXP's public NTMP table definitions. Expected users are ENETC `ntmp.c`, CBDR helpers, and table-management routines for MAC filters and RSS indirection. The constants `NETC_CBDR_BD_NUM`, `NETC_CBDRCIR_INDEX`, `NETC_CBDRCIR_SBE`, and `NETC_CBDR_CLEAN_WORK` also couple command descriptors to ring management logic.

### Risks
The risk profile is ABI/layout driven. Any structure padding, endianness mismatch, wrong length encoding, or table-version/query-action packing error will cause hardware command rejection or silent table corruption. `struct rsst_req_update` has a flexible array, so callers must size DMA buffers carefully. Command bit combinations are open-coded flags, making invalid combinations possible unless call sites validate them.

### Test Signals
Useful signals are compile-time layout checks where available, NTMP add/query/delete round trips for MAC filter table entries, RSS update verification, command rejection/error code parsing, CBDR wraparound with `NETC_CBDR_BD_NUM`, and endian-sensitive tests on little-endian descriptor fields.
