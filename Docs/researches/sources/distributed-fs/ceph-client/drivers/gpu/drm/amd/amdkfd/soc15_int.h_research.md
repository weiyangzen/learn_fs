# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/soc15_int.h

## Purpose
Provides KFD interrupt source constants and decode macros for SOC15-style interrupt handler entries.

## Important APIs, Types, And Functions
Defines source IDs for CP end-of-pipe, CP bad opcode, SQ interrupt message, VMC fault, VMC UTCL2 poison, SDMA trap/ECC, and SOC21 SDMA trap/ECC variants. Macros extract client id, source id, ring id, VMID, VMID type, PASID, node id, and context IDs 0 through 3 from little-endian interrupt entry dwords.

## Control Flow
There is no executable control flow. Interrupt handlers include this header to classify and unpack IH entries.

## State And Persistence
No state. Macros decode the caller-provided IH entry array.

## Dependencies And Integration Points
Includes `soc15_ih_clientid.h` and uses `le32_to_cpu`. It integrates with KFD interrupt paths that need PASID, VMID, node, and context data for dispatching faults/traps.

## Risks
Macros assume the IH entry layout and word indexes are correct for the targeted SOC generation. Using SOC15 macros on incompatible entry formats can misroute faults or traps. Lack of bounds checks means callers must provide a valid entry array.

## Test Signals
Unit-style decode tests with known synthetic IH entries, plus hardware fault/trap tests that verify decoded PASID, VMID, source, and node ids match expected events.
