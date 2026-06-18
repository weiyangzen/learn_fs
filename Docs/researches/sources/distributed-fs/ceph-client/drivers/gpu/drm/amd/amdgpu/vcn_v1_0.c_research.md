# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v1_0.c

## Purpose

`vcn_v1_0.c` implements the first AMD VCN IP generation. It manages one VCN instance with one decode ring, two encode rings, JPEG v1.0 integration, firmware/MC programming, static and dynamic power-gating modes, ring packet emission, secure-submission BO validation for Raven encrypted buffers, IRQ handling, and IP state dumping.

## Important APIs, Types, And Functions

The exported block is `vcn_v1_0_ip_block`, backed by `vcn_v1_0_ip_funcs`. Lifecycle functions initialize ring/IRQ tables, call common VCN firmware helpers, create decode/encode rings, integrate JPEG, allocate an IP dump buffer, test rings, and suspend/resume common VCN firmware state. `vcn_v1_0_start_spg_mode()` and `vcn_v1_0_start_dpg_mode()` are the central boot paths; `vcn_v1_0_stop_spg_mode()` and `vcn_v1_0_stop_dpg_mode()` are the stop paths. `vcn_v1_0_pause_dpg_mode()` pauses or unpauses non-JPEG and JPEG DPG domains and restores ring registers.

Decode ring helpers emit packet0 sequences to VCN internal registers: start/end, fences/traps, IB setup, register waits, VM flushes, register writes, and NOP padding. Encode helpers emit `VCN_ENC_CMD_*` packets. `vcn_v1_0_validate_bo()` and `vcn_v1_0_ring_patch_cs_in_place()` move encrypted VCN message BOs to VRAM on Raven secure submissions.

## Control Flow

Early init sets two encoder rings, installs the per-instance powergate callback, hooks ring/IRQ functions, calls JPEG early init, then common VCN early init. Software init registers decode and encode IRQs, resumes firmware, initializes rings and register offsets, hooks the DPG pause callback, optionally initializes firmware logging, initializes JPEG software, and allocates register dump storage. Hardware init runs tests for decode, both encoders, and JPEG.

The start path selects DPG when `AMD_PG_SUPPORT_VCN_DPG` is set. SPG disables static powergating, marks VCN busy, disables clock gating, programs cache windows and tiling registers, boots VCPU, waits for idle, enables interrupts, initializes RBC decode and encoder ring registers, and starts JPEG. DPG writes an SRAM-backed programming sequence, enables dynamic PG, programs cache/ring state, and starts JPEG in DPG mode. Idle work counts outstanding fences, updates DPG pause state, and gates VCN/JPEG when no work remains.

## State And Persistence

State is in `adev->vcn.inst[0]`: firmware BOs, `fw_shared`, decode and encode rings, register offset aliases, pause state, idle work, current PG state, IRQ source, and the JPEG coordination mutex. `adev->vcn.ip_dump` stores sampled registers for diagnostics. Ring write pointers are mirrored in hardware registers and scratch state for DPG restore.

## Dependencies And Integration Points

The file depends on common VCN firmware/session helpers, SOC15 register accessors, VCN 1.0 and MMHUB 9.1 registers, JPEG v1.0, AMDGPU PM/DPM, VM/GMC flush helpers, ring scheduler/fence helpers, DRM IRQ registration, and TTM BO validation. It integrates with the generic `vcn_set_powergating_state()` wrapper and common VCN/JPEG ring tests.

## Risks And Test Signals

Risks include DPG pause races with JPEG, incorrect ring restore after DPG pause, firmware boot timeout/reset loops, encrypted BO migration failures, IP dump reads while powered off, and mismatched packet dword counts in ring frame sizes. Test signals include decode/encode/JPEG ring tests, secure Raven submissions using encrypted GTT BOs, SPG and DPG suspend/resume, idle work gating under mixed JPEG/VCN workloads, interrupt routing for source IDs 124/119/120, and debug dump output for active and inactive instances.
