# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/cik_structs.h

## Purpose

`cik_structs.h` defines packed-by-convention C structs that mirror Sea Islands/CIK hardware queue context images used by AMD KFD and SDMA queue management. It provides the memory layout for a CIK compute MQD (memory queue descriptor) and an SDMA RLC register save/restore block. The file contains no logic; correctness depends on the field order matching the hardware/kernel queue programming ABI.

## Important APIs, Types, and Macros

The header exports two structs:

- `struct cik_mqd` is the CIK compute queue descriptor. It contains compute dispatch dimensions, program/TBA/TMA addresses, program resources, VMID, resource limits, static thread-management masks, trap/TMP ring settings, user data SGPR fields, HQD queue state, queue base/rptr/wptr/report/poll addresses, doorbell control, queue/IB controls, dequeue and semaphore fields, atomic preop fields, MQD timing/query/connect accounting fields, IQ timer packet data, reserved gaps, and sixteen queue doorbell IDs.
- `struct cik_sdma_rlc_registers` mirrors SDMA RLC queue register state: ring buffer control/base/read/write pointers, write-pointer polling and report addresses, IB state, skip/context/doorbell/virtual-address fields, APE1/doorbell log, reserved padding through index 125, and driver-internal `sdma_engine_id` plus `sdma_queue_id` in the final two slots.

There are no helper functions, enums, or macros beyond the include guard.

## Control Flow

The header has no internal control flow. Runtime flow is implemented in KFD queue management. CIK KFD code allocates GTT memory sized to `sizeof(struct cik_mqd)` and aligned as required by hardware, zeroes the MQD, fills fields from `queue_properties`, maps queue ring and write-pointer report addresses, programs VMID/doorbell/HQD fields, and passes the MQD to HIQ/HQD load paths. Queue update paths modify selected MQD fields, while dump/debug paths copy out `sizeof(struct cik_mqd)`. SDMA queue management can save or restore the SDMA RLC register image using `struct cik_sdma_rlc_registers`.

## State and Persistence Behavior

Instances of these structs are runtime state objects, usually allocated in GPU-accessible memory or used as CPU-side snapshots. `struct cik_mqd` persists for the lifetime of a compute queue and represents both software-owned queue metadata and hardware-consumed HQD state. Queue pointer fields track ring/IB progress and write-pointer polling/reporting. Doorbell IDs bind user-mode or kernel queue writes to a hardware queue. The SDMA RLC register block persists as a save/restore image; the last two fields are explicitly repurposed for driver-internal engine and queue identity rather than hardware registers.

The header itself persists no data.

## Dependencies

The file assumes `uint32_t` is available from the includer or kernel build environment. It is consumed by CIK-specific KFD code and must match CIK CP/HQD and SDMA register definitions. No external headers are included.

## Integration Points

The primary direct consumer is `drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_cik.c`. That code casts MQD memory to `struct cik_mqd`, initializes fields, updates queue properties, checks queue activity, destroys MQDs, dumps MQD contents, and exposes `mqd_size = sizeof(struct cik_mqd)` through CIK MQD manager operations.

## Risks and Edge Cases

- Field order and size are hardware ABI. Adding padding, changing types, or reordering fields will corrupt queue descriptors.
- The structure is not explicitly packed, so it relies on all fields being `uint32_t` and naturally contiguous.
- MQD memory must satisfy hardware alignment and accessibility requirements; the consumer aligns allocation to 256 bytes.
- Reserved fields are intentional layout placeholders. Removing or reusing them can shift later hardware fields.
- The final SDMA fields are driver-internal repurposed reserved slots. Treating them as hardware state during raw save/restore could leak software metadata into assumptions about register images.
- Doorbell, VMID, queue base, and pointer fields are security-sensitive. Incorrect values can cause queue hangs or cross-process memory access faults.

## Test Signals

Compile KFD CIK support and verify `sizeof(struct cik_mqd)` remains the expected MQD size used by `kfd_mqd_manager_cik.c`. Queue creation, update, eviction/restore, and destruction tests on CIK hardware validate the MQD layout. KFD compute dispatch tests exercise program address, resource, ring, VMID, doorbell, and HQD fields. Queue dump/debug paths should copy exactly `sizeof(struct cik_mqd)` without truncation. SDMA queue tests should validate ring pointer progression and save/restore behavior, including preservation of driver-internal engine/queue IDs.
