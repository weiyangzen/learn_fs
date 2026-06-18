<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/core.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/catpt/core.h

## Purpose
Private coordination header for the Intel CATPT LPT/WPT AudioDSP driver. It ties together device-level state, IPC state, SRAM allocation, DMA helpers, firmware boot/context preservation, DSP power control, ALSA platform registration, and stream runtime tracking.

## APIs, Types, and Functions
Defines `struct catpt_dev`, `struct catpt_ipc`, `struct catpt_ipc_msg`, `struct catpt_spec`, `struct catpt_module_type`, and `struct catpt_stream_runtime`. Public internal entry points include SRAM helpers `catpt_sram_init()`, `catpt_sram_free()`, `catpt_request_region()`, IPC initialization and send helpers, DMA setup/copy helpers, DSP power/clock/IRQ helpers, firmware boot and context-store helpers, `catpt_coredump()`, ALSA component registration, stream lookup and position update helpers, and `catpt_arm_stream_templates()`. `CATPT_IPC_RET()` normalizes positive firmware status codes to `-EREMOTEIO`.

## Control Flow, State, and Persistence
`struct catpt_dev` persists the whole driver instance: MMIO bases, IRQ, platform spec, firmware-ready completion, DRAM/IRAM resource trees, scratch allocation, mixer metadata, loaded module metadata, SSP device formats, stream list, mutexes, Dx context, and coherent Dx buffer. `struct catpt_ipc` persists mailbox sizing, firmware-ready config, reply buffer, completions, and serialization locks. Stream runtime state persists per ALSA substream, including DSP stream info, persistent memory allocation, page-table buffer, and allocated/prepared flags.

## Dependencies and Integration
Includes `messages.h` and `registers.h`, Linux DW DMA definitions, IRQ types, ALSA memalloc/uapi headers, and exposes `catpt_attr_groups` for device registration. It is included by all CATPT implementation files and forms the private ABI between the ACPI platform driver, DSP/loader/IPC code, and PCM component.

## Risks and Test Signals
Risks include shared state coupling across PM, IPC, firmware restore, and PCM paths; positive firmware return codes leaking without `CATPT_IPC_RET()`; resource-tree lifetime bugs; and stream-list locking assumptions during Dx transitions. Test signals are build coverage of all CATPT objects, successful probe/firmware boot, suspend/resume with streams, ALSA stream open/close, IPC timeout paths, and coredump generation after firmware fault.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/core.h -->
