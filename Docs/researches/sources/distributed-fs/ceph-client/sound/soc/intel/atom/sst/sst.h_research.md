# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst.h

## Purpose
This private header defines the low-level Intel SST driver model: register offsets, firmware state values, stream states, firmware binary layout, IPC wait blocks, stream contexts, memory-copy descriptors, module/library metadata, platform context, hardware operation callbacks, and cross-file function prototypes.

## Important APIs, types, and functions
Key hardware constants include `SST_CSR`, `SST_ISRX`, `SST_IMRX`, `SST_IPCX`, `SST_IPCD`, `MRFLD_FW_VIRTUAL_BASE`, and firmware context sizes. State enums are `sst_states`, `sst_stream_states`, `sst_ram_type`, and `sst_lib_dwnld_status`. IPC synchronization uses `struct sst_block`; per-stream state uses `struct stream_info`; firmware parsing uses `struct sst_fw_header`, `struct fw_module_header`, and `struct fw_block_info`; copy operations use `struct sst_memcpy_list`.

`struct intel_sst_drv` is the central context, owning mapped memories, lists, workqueue, stream array, locks, platform data, firmware cache, QoS, IPC register offsets, library memory manager, and suspend snapshot. `struct intel_sst_ops` is the platform-specific operation table. The header declares the full cross-file API for stream commands, IPC posting, firmware loading, block waits, pvt-id allocation, stream lookup, context lifecycle, PM helpers, and MMIO read/write helpers.

## Control flow
No code runs in this header, but all low-level source files implement functions declared here against the same context. Bus probes allocate and initialize `intel_sst_drv`; firmware loader populates copy lists; IPC code posts/wakes blocks; stream code mutates `streams[]`; PM code saves/restores firmware memories.

## State and persistence behavior
All persistent runtime state is represented in `intel_sst_drv` and `stream_info`. Firmware cache `fw_in_mem` and copy lists survive across runtime power cycles. `fw_save` temporarily persists memory images across system suspend. No data is written to disk.

## Dependencies and integration points
It depends on the Linux firmware API and on platform structures from `asm/platform_sst_audio.h` through implementation files. It is the contract connecting bus enumeration, firmware loading, IPC, stream control, and ASoC platform registration.

## Risks and edge cases
Many fields are shared across IRQ, workqueue, PM, and ALSA callbacks, so lock discipline is critical. Stream array index 0 is reserved. Firmware file/block layouts are trusted by the loader after signature and size checks. `pvt_id` uses a bitset with a small maximum and can exhaust under many simultaneous blocking IPCs.

## Test signals
Build coverage plus runtime coverage of all declared paths: firmware parse/load, IPC block timeout/wakeup, stream allocation/free, PM context save/restore, bus probe/remove, and MMIO helper access on target hardware.
