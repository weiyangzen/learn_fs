# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmsch_v2_0.h

## Purpose

`mmsch_v2_0.h` defines MMSCH 2.0 register offsets and command-table ABI for VCN virtualization. It combines a generated-style register map for the MMSCH block with the init-header and command structures needed to build firmware initialization tables.

## Important APIs, Types, And Functions

The first half defines `mmMMSCH_*` register offsets and base indices for ucode/SRAM access, VF context, mailbox, GPUIOV scheduling/status, scratch, FIFO, NACK, active function, and VM busy registers. The ABI section defines major/minor version macros, `enum mmsch_v2_0_command_type`, `struct mmsch_v2_0_init_header`, command header structs, direct write/read-modify-write/poll/end/indirect command structs, inline insertion helpers, and macros `MMSCH_V2_0_INSERT_DIRECT_RD_MOD_WT`, `MMSCH_V2_0_INSERT_DIRECT_WT`, and `MMSCH_V2_0_INSERT_DIRECT_POLL`.

## Control Flow

The header itself does not run. VCN code uses register offsets for direct MMSCH programming and uses insertion macros to append commands into an init table. The inline helpers populate fields and `memcpy` structs into the caller's table pointer; macros advance `init_table` and `table_size`.

## State And Persistence Behavior

The register constants describe hardware-visible state. The command structs define a firmware-visible memory layout that persists in the init table until consumed by MMSCH. The macros mutate caller-local table pointers and counters and perform no allocation, locking, or bounds checking.

## Dependencies And Integration Points

`vcn_v2_0.c` includes this header for VCN MMSCH initialization. It depends on fixed register offsets matching the hardware IP and on common kernel types and `memcpy`. Mailbox response and GPUIOV register names align this header with SR-IOV media scheduling.

## Risks

Large register maps are vulnerable to offset drift if copied across IP revisions. Macro hygiene and missing bounds checks mirror v1.0 risks. The command bitfield layout must remain compatible with firmware and compiler packing. Register constants are untyped, so wrong block/base usage in callers will compile.

## Test Signals

Test VCN v2 SR-IOV initialization, MMSCH mailbox communication, command table upload, engine pass status, and VM busy/status polling. Static checks should confirm table sizes and register offsets match the IP headers or hardware spec used by this tree.
