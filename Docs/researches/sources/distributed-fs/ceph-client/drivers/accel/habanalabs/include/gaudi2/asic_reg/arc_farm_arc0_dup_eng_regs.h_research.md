<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_arc0_dup_eng_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_arc0_dup_eng_regs.h

## Purpose
`arc_farm_arc0_dup_eng_regs.h` is the generated address map for the Gaudi2 `ARC_FARM_ARC0_DUP_ENG` duplicate-engine block, prototype `ARC_DUP_ENG`. It exposes 276 register address macros in the 0x4E89000-0x4E896B0 region that let ARC farm firmware or the driver duplicate/route engine transactions across TPC, MME, NIC, EDMA, PDMA, ROT, and reserved engine slots.

## Important APIs, types, and functions
This header exports `mmARC_FARM_ARC0_DUP_ENG_*` macros only. Major groups are per-engine duplicate address tables for 25 TPCs, 4 MMEs, 24 NICs, 8 EDMAs, 2 PDMAs, 2 ROTs, and 16 reserved slots; engine mask registers for TPC/MME/EDMA/PDMA/ROT/reserved/NIC groups; multiple `DUP_TRANS_DATA_Q_*_*` queues; `DUP_GENERAL_CFG`, `DUP_BP_CFG`, and 14 group address-offset registers; debug input/status/output counters; 64 ARC context-id registers; and 64 ARC context-id offset registers.

## Control flow
The file contains no executable control flow. Runtime code programs it as a routing table: configure duplicate target addresses and masks, optionally set grouped address offsets and backpressure behavior, then allow ARC firmware or command submission paths to emit duplicated engine transactions. Debug paths can read the group transaction and output request counters to understand whether duplicated traffic is entering and leaving the block.

## State and persistence behavior
All state is hardware-resident and persists until reset or reprogramming. The engine address, mask, queue, context-id, and context-offset registers define how ARC0 traffic is mapped to engine endpoints. Incorrect persisted values can make later command streams target the wrong engine or context even if the command stream itself is valid.

## Dependencies and integration points
The header integrates with generated Gaudi2 base maps, ARC firmware setup, engine discovery/topology code, and debug/recovery code that reasons about ARC farm routing. Consumers depend on the register order and engine counts matching Gaudi2 topology constants elsewhere in the driver.

## Risks and edge cases
The largest risk is topology drift: a count mismatch for TPC, NIC, EDMA, or context-id slots can map a command to the wrong target. Masks and address tables are separate, so enabling a mask before the matching address table is initialized can route traffic into stale or reserved addresses. Reserved-engine slots should remain treated as reserved unless the hardware spec says otherwise.

## Test signals
Test signals include successful ARC farm initialization, command execution across TPC/MME/NIC/EDMA endpoints, no duplicated traffic to disabled engines, expected debug counters during routed work, and reset tests proving duplicate address/mask tables are reinitialized before traffic resumes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_arc0_dup_eng_regs.h -->
