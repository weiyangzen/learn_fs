# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_4_offset.h

## Purpose

This generated header provides the MP 13.0.4 register offsets and base-index selectors for the AMD management processor register interface. It is the address companion to `mp_13_0_4_sh_mask.h`. Consumers use its `reg...` macros to build MMIO/SMN addresses through SOC15 AMDGPU helpers, while the matching mask header describes bit-level layout.

The file covers two address blocks: `mp_SmuMp0_SmnDec` and `mp_SmuMp1_SmnDec`. The MP0 block exposes C2PMSG mailboxes 32 through 127 plus MP0 interrupt helper registers. The MP1 block exposes C2PMSG mailboxes 32 through 103, MP1 interrupt helper registers, `MP1_SMN_FPS_CNT`, and `MP1_SMN_EXT_SCRATCH0` through `MP1_SMN_EXT_SCRATCH7`.

## Important APIs, Types, And Macros

The public surface is C preprocessor register-address macros guarded by `_mp_13_0_4_OFFSET_HEADER`. Each register has two definitions: `reg<NAME>` for the block-relative register offset and `reg<NAME>_BASE_IDX` for the base segment index. There are no functions, types, enums, or variables.

Important MP0 offsets include `regMP0_SMN_C2PMSG_32` at `0x0060`, continuing sequentially through `regMP0_SMN_C2PMSG_127` at `0x00bf`, with interrupt helper registers at `0x00c1` through `0x00c3`. Important MP1 offsets include `regMP1_SMN_C2PMSG_32` at `0x0260`, continuing through `regMP1_SMN_C2PMSG_103` at `0x02a7`, then MP1 interrupt helper registers at `0x02c1` through `0x02c3`, `regMP1_SMN_FPS_CNT` at `0x02c4`, and MP1 scratch registers `0x0340` through `0x0347`.

All base indices in this file are `1`. That is a key integration detail: display and SOC15 helpers use the index to choose the correct segment from an IP base table. A consumer using an MP 13.0.5-style base table or base index would address the wrong segment for this ASIC revision.

Inventory signal: the header contains 366 register/base-index macro definitions.

## Control Flow

There is no executable control flow. The include guard is the only compile-time gate. Runtime control flow appears in consumers that combine these constants with AMDGPU register helpers. The primary direct consumer is `amdgpu/psp_v13_0_4.c`, which includes both this offset header and `mp_13_0_4_sh_mask.h`. It waits for the bootloader on `MP0_SMN_C2PMSG_35`, writes firmware buffer addresses to `MP0_SMN_C2PMSG_36`, checks SOS sign-of-life through `MP0_SMN_C2PMSG_81`, and uses mailbox registers such as `MP0_SMN_C2PMSG_64`, `67`, `69`, `70`, `71`, `101`, `102`, and `103` for ring and command traffic.

## State And Persistence Behavior

The header stores no state. It describes the address map for hardware state owned by MP0/MP1 firmware and the GPU register fabric. Consumer reads and writes alter or observe firmware mailboxes, bootloader state, command responses, interrupt helper registers, and scratch data. Persistence is limited to hardware register lifetime. A bad offset can persistently disrupt a boot sequence during a driver session because every subsequent poll or write targets the wrong register.

## Dependencies

The file depends only on the C preprocessor, but it is meaningful only with the AMDGPU register access framework. Consumer code usually passes these `reg...` macros to `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, or local display `REG()` macros that add a base segment selected by `reg..._BASE_IDX`. It is generated in the same style as neighboring `mp_13_0_x_offset.h` files and should be treated as ASIC specification data rather than hand-maintained logic.

## Integration Points

The direct include site found for this exact file is `drivers/gpu/drm/amd/amdgpu/psp_v13_0_4.c`. That PSP implementation declares firmware modules for PSP 13.0.4 and uses MP0 mailbox addresses for TOC/TA initialization, bootloader component loading, ring stop/create, register programming, and command response handling. The matching mask header is included in the same file, though most PSP accesses use full-register command values and response masks from broader PSP definitions rather than field extraction from this header.

## Risks

The base index of `1` is the highest-value risk. It differs from MP 13.0.5, where equivalent registers use base index `0`. Any copy/paste or include mismatch between ASIC revisions can compile cleanly but address the wrong register segment. Another risk is mailbox range mismatch: this header provides MP0 C2PMSG 32-127 but MP1 C2PMSG only 32-103, so consumers must not assume identical MP0/MP1 ranges. Because these constants are generated, manual edits risk diverging from AMD hardware definitions.

## Test Signals

Compile-time tests should verify the PSP 13.0.4 translation unit builds with this header and the matching mask header. Runtime validation requires PSP 13.0.4 hardware or emulation: bootloader wait should complete, SOS sign-of-life should become nonzero, firmware component loading should succeed, and ring setup/teardown should avoid mailbox timeouts. Static comparison against the source register database should confirm sequential MP0/MP1 C2PMSG offsets and base index `1` for every register in this file.
