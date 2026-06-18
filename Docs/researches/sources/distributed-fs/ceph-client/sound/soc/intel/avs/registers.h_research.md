# sources/distributed-fs/ceph-client/sound/soc/intel/avs/registers.h

Purpose: Centralizes AVS/HDA DSP register offsets, bit masks, SRAM window helpers, and typed MMIO read/write/update/poll macros.

Important APIs/types: Defines PCI power/clock-gating masks, generic ADSP core-control/status bits, IPC register layouts for SKL/CNL/MTL, MTL flag/power registers, SRAM base/window sizes for SKL/APL/MTL, firmware status/error windows, uplink/downlink windows, and `snd_hdac_adsp_*` accessors.

Control flow role: Platform files use these constants to power/stall/reset cores, handle IPC interrupts, load firmware, dump logs, and access SRAM mailboxes. Poll macros wrap kernel `read*_poll_timeout()` for hardware state waits.

State and persistence: No state is owned; macros compute addresses from `adev->dsp_ba` and platform specs.

Dependencies and integration: Includes kernel IO, polling, and size headers; expects `adev` to have `base.core`, `dsp_ba`, and `spec` with SRAM/HIPC metadata.

Risks: Register offsets are hardware ABI. Update macros are read-modify-write without locking; callers must serialize where required. Polling MMIO after device removal or power loss can return invalid values such as `UINT_MAX`, which callers often check inconsistently.

Test signals: Build coverage across all platform ops, hardware smoke tests for each supported generation, fault-injection for timeout paths, and sparse/static analysis for macro side effects.
