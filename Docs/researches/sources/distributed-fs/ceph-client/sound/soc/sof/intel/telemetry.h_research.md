<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/telemetry.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/telemetry.h

## Purpose
Internal Intel IPC4 telemetry header defining the firmware Xtensa architecture block layout read from telemetry debug slots.

## Important APIs, Types, and Functions
Defines packed `struct xtensa_arch_block` with SOC, version, toolchain, PC, exception cause/address, SAR, PS, compare register, AR register array, and loop registers. Declares `sof_ipc4_intel_dump_telemetry_state()`.

## Control Flow, State, and Persistence
No runtime logic. The packed struct is an ABI contract with firmware telemetry payloads; fields are copied into the generic SOF Xtensa oops format during dump handling.

## Dependencies and Integration
Includes IPC4 telemetry definitions and relies on Xtensa constants such as `XTENSA_CORE_AR_REGS_COUNT`. Used by `telemetry.c` and Intel HDA IPC4 dump code.

## Risks and Test Signals
Risks are layout and endian assumptions in a packed firmware-facing struct. Test signals are successful parsing of real firmware core dumps, struct-size compatibility with debug slot payloads, and compile-time coverage when Xtensa register count changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/telemetry.h -->
