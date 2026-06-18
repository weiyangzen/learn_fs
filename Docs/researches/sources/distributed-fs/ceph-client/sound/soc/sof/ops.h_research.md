# sources/distributed-fs/ceph-client/sound/soc/sof/ops.h

Purpose: Defines the central inline dispatch layer from generic SOF code to platform-specific `snd_sof_dsp_ops`.

Important APIs: Probe/remove/shutdown wrappers, DSP run/stall/reset, core get/put reference counting, pre/post FW run, platform extended manifest parsing, BAR/mailbox/window lookup, suspend/resume/runtime PM, clock setting, power state serialization, MMIO and mailbox IO, block IO, IPC send/data, PCM platform ops, firmware load, machine driver hooks, chain DMA query, and `snd_sof_dsp_read_poll_timeout()`.

Control flow and state: Most wrappers check optional callbacks and return 0/default when absent. Mandatory operations are expected to be verified during probe. Core get/put validates core index, reference counts `sdev->dsp_core_ref_count`, calls platform power callbacks only on 0-to-1 and 1-to-0 transitions, and maintains `enabled_cores_mask`. `snd_sof_dsp_set_power_state()` serializes with `power_state_access`. Register IO falls back to raw read/write accessors if ops are absent.

Dependencies and integration: Included across SOF core, IPC, PM, PCM, topology, and platform drivers. It is the compatibility layer that lets PCI, OF, ACPI, Intel, AMD, and MediaTek drivers plug into common SOF flows.

Risks: Default no-op behavior can hide missing optional callbacks. Core put pre-decrements refcount and does not guard underflow if callers are imbalanced. Raw read/write fallbacks assume `sdev->bar[bar]` is valid. Poll macro reads once more on timeout and returns based on final condition, so side-effect registers need care.

Test signals: Probe validation for mandatory ops, core refcount balance including errors, power-state serialization, fallback IO paths, optional callback absence, mailbox/window offset errors, and poll timeout/success behavior.
