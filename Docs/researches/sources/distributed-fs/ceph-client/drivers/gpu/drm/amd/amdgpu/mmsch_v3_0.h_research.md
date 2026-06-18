# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmsch_v3_0.h

## Purpose

`mmsch_v3_0.h` defines the MMSCH 3.0 firmware init-table ABI for VCN generation 3 media engines. It drops the large v2 register map and focuses on versioned table layout and command construction macros.

## Important APIs, Types, And Functions

It includes `amdgpu_vcn.h`, defines `MMSCH_VERSION_MAJOR 3`, `MMSCH_VERSION_MINOR 0`, `MMSCH_VERSION`, and `MMSCH_V3_0_VCN_INSTANCES 0x2`. It declares `enum mmsch_v3_0_command_type`, `struct mmsch_v3_0_table_info`, `struct mmsch_v3_0_init_header`, direct/indirect command header structs, direct write/read-modify-write/poll/end/indirect command structs, and insertion macros including `MMSCH_V3_0_INSERT_END`.

## Control Flow

Callers build an init table by maintaining `table_loc`, `table_size`, `size`, and `size_dw`. Each macro computes the structure size, fills a command template, copies it into `table_loc`, advances `table_loc` by dwords, and increments `table_size`. `MMSCH_V3_0_INSERT_END` appends the preinitialized end command.

## State And Persistence Behavior

The ABI state is the firmware table in memory. The init header has a total size and per-VCN-instance table info array, allowing two VCN instances to be described. The macros mutate caller-local variables and assume command structs are already zeroed or have `command_type` set as needed.

## Dependencies And Integration Points

`vcn_v3_0.c` uses this header when building VCN MMSCH init tables. It depends on `amdgpu_vcn.h` for surrounding VCN definitions and on firmware interpreting version `3.0` layouts.

## Risks

The macros are scope-dependent and lack bounds checks. Failing to initialize the `end` command or command-type fields will produce malformed tables. `MMSCH_V3_0_VCN_INSTANCES` is fixed at two, so callers must not use this layout for hardware with a different instance model.

## Test Signals

Boot VCN v3 hardware, verify MMSCH table upload and engine init status for both instances, confirm end markers are present, and run encode/decode workloads after SR-IOV/media initialization. Build tests should include all macro callers.
