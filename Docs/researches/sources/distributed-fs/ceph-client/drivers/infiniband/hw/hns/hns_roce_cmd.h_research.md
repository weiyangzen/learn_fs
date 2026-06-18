# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_cmd.h

Purpose: Defines mailbox size/timeout constants, hardware command opcodes, and command helper prototypes for HNS RoCE.

Important APIs/types/functions: `HNS_ROCE_MAILBOX_SIZE` is 4096 bytes and `HNS_ROCE_CMD_TIMEOUT_MSECS` is 10000. The opcode enums cover base-address table operations for QPC/CQC/MPT/SRQC/SCCC/timer contexts, EQ context commands, query/modify commands, and object lifecycle commands for MPT, CQ, QP, and SRQ. Prototypes expose mailbox command submission and command mailbox allocation.

Control flow: Callers pass an opcode plus input/output DMA parameters and tag to `hns_roce_cmd_mbox()`. Higher-level wrappers create or destroy hardware contexts by combining a mailbox DMA address with a command and object index.

State and persistence: No runtime state is stored here. The opcode definitions are a stable hardware ABI contract.

Dependencies and integration: Included by command implementation and object-management files such as CQ, MR, QP, SRQ, and HEM users. The enum values must match firmware/hardware mailbox definitions.

Risks: Wrong opcode values can corrupt hardware context tables. The file has two anonymous enums with potentially overlapping values by command domain, so call sites must use the correct command for the firmware path. Test signals include firmware command compatibility, create/destroy/query coverage for each object type, and build checks for all prototypes.
