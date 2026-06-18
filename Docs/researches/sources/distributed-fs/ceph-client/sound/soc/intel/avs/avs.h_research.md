# sources/distributed-fs/ceph-client/sound/soc/intel/avs/avs.h

## Purpose
This is the main private header for the Intel AVS ASoC driver. It defines platform operation tables, platform descriptors, core driver state, IPC message/context structures, platform attributes, helper macros, and cross-file prototypes for DSP control, IPC, firmware resources, firmware loading, component registration, board registration, topology parsing, debug logging, D0ix, and sysfs integration.

## Important APIs, types, and functions
`struct avs_dsp_ops` abstracts per-platform DSP operations such as core power/reset/stall, interrupt handling, firmware/library loading, log handling, coredump, D0ix policy, and log enablement. `struct avs_spec` describes a platform by name, minimum firmware version, boot core mask, attributes, SRAM windows, HIPCI register layout, and operation table. Platform attributes include `AVS_PLATATTR_CLDMA`, `IMR`, `ACE`, and `ALTHDA`.

`struct avs_dev` is the central runtime object and embeds `struct hda_bus`. It owns DSP BAR mapping, spec pointer, IPC context, firmware/hardware/module configuration, module instance ID allocators, pipeline ID allocator, loaded firmware list, core reference counts, library names, L1SEN counter, firmware-ready completion, probe work, component/path lists and locks, trace state, and optional debugfs/probe fields. `struct avs_ipc_msg` and `struct avs_ipc` model request/reply payloads, completions, serialization, recovery, and D0ix state. `AVS_IPC_RET()` converts positive firmware error codes to `-EREMOTEIO`.

## Control flow
The header itself does not execute code. PCI core code selects an `avs_spec`, generic code calls `avs_dsp_op()` for platform-specific operations, IPC code fills `avs_ipc_msg` and uses `avs_ipc` completions, loader code manages firmware entries, topology/path code allocates modules and pipelines, and PCM/control code registers ASoC components and paths.

## State and persistence behavior
All AVS runtime state is in `avs_dev` and `avs_ipc`. Firmware list entries hold requested firmware objects until released. Module and pipeline IDA pools persist while topology paths exist. D0ix and recovery flags persist in the IPC context. Debug trace buffers are in-memory only, except coredumps emitted through kernel devcoredump.

## Dependencies and integration points
The header depends on Linux device, firmware, kfifo, debugfs, HD-audio, and ASoC component APIs plus local `messages.h` and `registers.h`. It is included by most AVS implementation files and defines the internal ABI for the module.

## Risks and edge cases
Because this header centralizes cross-file contracts, signature drift affects many objects in `Makefile`. `avs_dsp_op()` assumes the platform operation pointer exists. `to_avs_dev()` assumes device driver data is an HD-audio bus. IPC callers must consistently apply `AVS_IPC_RET()` after consuming firmware error codes. Optional debugfs fields must only be used under `CONFIG_DEBUG_FS`.

## Test signals
Compile all AVS objects and platform variants. Runtime signals include PCI platform descriptor selection, firmware boot, IPC request/reply completions, recovery and D0ix state transitions, module/pipeline ID allocation/free, board/component registration, trace/debugfs behavior when enabled, and disabled-debugfs builds.
