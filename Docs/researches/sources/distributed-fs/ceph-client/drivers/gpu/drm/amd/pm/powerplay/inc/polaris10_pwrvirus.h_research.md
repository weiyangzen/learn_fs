# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/polaris10_pwrvirus.h

## Purpose

`polaris10_pwrvirus.h` embeds a Polaris10-specific synthetic high-power workload setup as static register-write and DFY data tables. It is a hardware validation payload rather than normal policy code, intended for consumers that can write the listed CP, RLC, TCC, TCP, MEC, HQD, MQD, and SRBM registers.

## Important APIs, Types, And Functions

The exported structures are `PWR_Command_Table`, a `{ data, reg }` register write tuple, and `PWR_DFY_Section`, a descriptor containing DFY control, high/low target address, data size, and a flexible `dfy_data[]` payload. The file defines hypervisor MEC microcode register offsets `mmCP_HYP_MEC1_UCODE_ADDR/DATA` and `mmCP_HYP_MEC2_UCODE_ADDR/DATA`.

The main data exports are `pwr_virus_table_pre`, six `pwr_virus_sectionN` DFY sections, and `pwr_virus_table_post`. The pre table disables or programs RLC/CP/MEC/TCC/TCP state, writes repeated MEC1/MEC2 microcode words, and ends with `{0, 0xFFFFFFFF}`. DFY sections carry payloads at hard-coded GPU addresses and sizes of 416, 16, 7440, 240, 384, and 1024 dwords. The post table programs MQD/HQD queue bases, PQ controls, active bits, read/write pointers, SRBM instances, and polling control.

## Control Flow And Data Flow

There is no C control flow. Consumers must apply `pwr_virus_table_pre`, copy each DFY section to the requested GPU memory/register window according to its control and address fields, then apply `pwr_virus_table_post` to activate queues. Data flows directly from static arrays to MMIO/register-indexed writes and queue memory consumed by CP/MEC hardware.

## State And Persistence Behavior

All state lives in GPU hardware after the tables are applied. The payload changes microcode ports, queue descriptors, active HQDs, polling addresses, command processor controls, and memory-backed payload areas. Effects persist until teardown, queue reset, CP reset, GPU reset, or power-cycle. The header itself stores read-only constants in the kernel image.

## Dependencies And Integration Points

The file relies on many `mm*` register macros supplied by ASIC register headers included by the consuming C file. It integrates with Polaris10 hwmgr/power-containment test logic, CP/MEC queue setup, SRBM instance selection, and low-level register-write helpers.

## Risks And Edge Cases

This is high-risk hardware programming data. Running it on the wrong ASIC, firmware revision, queue topology, memory map, or register header can corrupt command-processor state or hang the GPU. The sentinel must be honored exactly. DFY sizes must match payload lengths. Pre/post ordering matters. Hard-coded addresses and selectors assume a specific Polaris10 environment.

## Test Signals

Validation needs Polaris10-only compile coverage, register macro resolution, controlled lab execution, GPU hang/reset recovery checks, thermal and power telemetry correlation, queue activity observation, CP/MEC status polling, and confirmation that normal graphics/compute submission recovers after teardown or reset.
