# sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-telemetry.h

## Purpose
Defines the IPC4 exception telemetry/coredump binary headers used by firmware and the debugfs telemetry reader.

## APIs, Types, and Functions
Declares `enum sof_ipc4_coredump_tgt_code`, coredump magic/header constants, Xtensa-specific constants, packed `struct sof_ipc4_coredump_hdr`, packed `struct sof_ipc4_coredump_arch_hdr`, packed/flexible `struct sof_ipc4_telemetry_slot_data`, and the prototype `sof_ipc4_create_exception_debugfs_node()`.

## Control Flow, State, and Persistence
The header has no executable control flow. It defines the persistent crash-slot layout: a separator word, generic coredump header with target, pointer size, flags and reason, architecture-specific block header, and variable architecture data. Firmware writes this into a telemetry debug slot, while `ipc4-telemetry.c` exposes it as a raw debugfs binary range after skipping the first separator word.

## Dependencies and Integration
Used by IPC4 telemetry code and any decoder that consumes the debugfs `exception` binary. The Xtensa constants identify Intel ADSP/Zephyr/XCC dump format details expected in `arch_data`.

## Risks and Test Signals
Risks include packed-structure ABI drift, endian/width assumptions in external parsers, and new target architectures needing enum/header extensions. Test signals are compile-time layout compatibility, parsing real Xtensa exception dumps, validation of `ZE` and `A` identifiers, and graceful decoder behavior for unknown target codes.
