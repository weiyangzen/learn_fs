# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_regs.h

## Purpose
`hclge_regs.h` declares the PF register-dump interface implemented in `hclge_regs.c`. It keeps the ethtool/debug register dump entry points visible without exposing the internal TLV tags, static address lists, or DFX parsing helpers.

## Important APIs
- `hclge_query_bd_num_cmd_send(struct hclge_dev *hdev, struct hclge_desc *desc)` issues the DFX BD-count command and is available for code that needs raw diagnostic sizing.
- `hclge_get_regs_len(struct hnae3_handle *handle)` computes the required dump buffer size.
- `hclge_get_regs(struct hnae3_handle *handle, u32 *version, void *data)` writes the live register dump.

## State, Dependencies, And Integration
The header includes Linux types and `hclge_comm_cmd.h` for descriptor definitions, forward-declares PF device and HNAE3 handle types, and integrates with the PF operation table. Callers are responsible for passing a buffer sized by `hclge_get_regs_len()`.

## Risks And Test Signals
The main risk is contract mismatch between the length and fill functions if firmware dynamic counts differ or callers ignore negative length errors. Build tests should catch signature drift; runtime tests should compare returned length against actual TLV traversal and confirm graceful behavior on command failures.
