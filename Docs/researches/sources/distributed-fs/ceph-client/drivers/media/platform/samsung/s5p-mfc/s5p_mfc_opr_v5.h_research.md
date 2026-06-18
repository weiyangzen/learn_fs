# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_opr_v5.h

Purpose: declares v5 operation-table initialization and defines v5 firmware shared-memory offsets.

Important APIs and types: `enum MFC_SHM_OFS` lists offsets for decode status, frame tags, timestamps, crop info, encoder extended control, parameter-change fields, metadata, allocated DPB sizes, VOP timing, HEC period, batch addresses, aspect ratio fields, debug history, hierarchical QP, and frame-packing SEI. The header exports `s5p_mfc_init_hw_ops_v5`.

Control flow: v5 operation code uses these offsets with `s5p_mfc_write_info_v5` and `s5p_mfc_read_info_v5` to exchange sideband information with firmware in the per-context shared-memory buffer.

State and persistence: no header-owned state. The enum defines the layout of `ctx->shm`, whose contents are volatile firmware/driver command state.

Dependencies and integration points: includes MFC common and operation headers. It tightly couples the v5 backend to firmware shared-memory ABI values; generic code sees only the returned `struct s5p_mfc_hw_ops`.

Risks: misspelled enum names such as `EXTENEDED_DECODE_STATUS` are ABI-neutral but easy to misuse. Any offset drift from firmware expectations breaks codec behavior. The include guard closing comment names `S5P_MFC_OPR_H_`, which is inconsistent but not functional.

Test signals: v5 build coverage; firmware command tests validating crop, QP, frame-rate, metadata, and frame-packing fields; and shared-memory dump checks during encode/decode.
