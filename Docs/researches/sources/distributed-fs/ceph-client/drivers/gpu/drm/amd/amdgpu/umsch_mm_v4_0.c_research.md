# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umsch_mm_v4_0.c

## Purpose

This file implements UMSCH MM v4.0 support, wiring the multimedia micro-scheduler to VCN/VPE hardware. It loads scheduler firmware, configures instruction/data memory windows, starts and stops the scheduler ring, initializes aggregated doorbells, and submits scheduler API packets for hardware resources and queue management.

## Important APIs, Types, and Functions

The public entry point is `umsch_mm_v4_0_set_funcs`. Important callbacks are `umsch_mm_v4_0_load_microcode`, `umsch_mm_v4_0_ring_start`, `umsch_mm_v4_0_ring_stop`, `umsch_mm_v4_0_set_hw_resources`, `umsch_mm_v4_0_add_queue`, `umsch_mm_v4_0_remove_queue`, and `umsch_mm_v4_0_set_regs`. It uses API unions from `umsch_mm_4_0_api_def.h`.

## Control Flow

Microcode load allocates code and data buffers, optionally powers DLDO for VCN 4.0.5+, resets/halt-primes MES state, programs instruction/data base and mask registers, primes and invalidates caches, optionally asks PSP to execute the command buffer, and waits for `regVCN_MES_MSTATUS_LO == 0xAAAAAAAA`. API calls fill a frame, set a completion fence address/value, submit the packet, then query the fence.

## State and Persistence Behavior

The code mutates UMSCH firmware BOs, command buffer pointers, VCN/MES registers, ring write pointer, doorbell ranges, scheduler context GPU addresses, fence sync sequence, and firmware-visible queue/resource state. Error paths free allocated firmware buffers.

## Dependencies and Integration Points

Dependencies include AMDGPU core, SOC15/VCN register definitions, NBIO doorbell functions, PSP firmware loading mode, debugfs logging addresses, UMSCH common helpers, VPE collaboration mode, and fence driver GPU addresses.

## Risks

Firmware load sequencing is register-order sensitive. PSP and non-PSP firmware load modes require different base addresses. Missing fence completion indicates firmware/API failure. Doorbell offsets and priority-level aggregated doorbells must match userspace queue setup.

## Test Signals

Signals include successful firmware status magic, no buffer leaks on load failure, valid ring write/read pointer registers, working add/remove queue fence completions, VCN/VPE workload scheduling, correct doorbell interrupts, and clean ring stop/power transitions.
