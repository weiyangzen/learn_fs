# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmsch_v1_0.h

## Purpose

`mmsch_v1_0.h` defines the version 1 multimedia scheduler command-table ABI used by older virtualized VCE/UVD/VCN paths. It provides table headers, command encodings, and helper macros used by engine code to build initialization command buffers consumed by MMSCH firmware.

## Important APIs, Types, And Functions

The header defines `MMSCH_VERSION 0x1`, `enum mmsch_v1_0_command_type`, `struct mmsch_v1_0_init_header`, `struct mmsch_vf_eng_init_header`, `struct mmsch_v1_1_init_header`, direct and indirect command header structs, write/read-modify-write/poll/end/indirect command structs, inline insertion helpers, and macros `MMSCH_V1_0_INSERT_DIRECT_RD_MOD_WT`, `MMSCH_V1_0_INSERT_DIRECT_WT`, and `MMSCH_V1_0_INSERT_DIRECT_POLL`.

## Control Flow

There is no standalone runtime flow. Caller code allocates an init table, initializes local command templates such as `direct_wt`, `direct_rd_mod_wt`, and `direct_poll`, and invokes insertion macros. Each macro copies a packed command struct into `init_table`, then advances the pointer and `table_size` by the command size in dwords.

## State And Persistence Behavior

The header defines an in-memory binary layout shared with firmware. Persistent effects occur only after caller code submits the populated table to MMSCH. The macros mutate caller-local variables `init_table` and `table_size`, so they rely on names existing in the caller's scope.

## Dependencies And Integration Points

It is included by `uvd_v7_0.c`, `vce_v4_0.c`, and `vcn_v2_5.c`. It relies on `uint32_t` and `memcpy` being available through the include chain. The v1.0 header covers VCE/UVD table offsets and v1.1 generic engine table info for two engines.

## Risks

The bitfield layout is ABI-sensitive and compiler/layout assumptions matter. The macros are not hygienic: they require specific variable names and are statement blocks without `do { } while (0)`. They do not set `command_type`; caller templates must be initialized correctly. Buffer bounds are not checked before `memcpy`, so callers must size tables correctly.

## Test Signals

Build all callers, verify command table sizes and offsets against firmware expectations, boot SR-IOV/media paths that consume v1 tables, and test polling/write/read-modify-write commands by observing successful VCE/UVD/VCN engine initialization.
