# sources/distributed-fs/ceph-client/sound/soc/sof/ops.c

Purpose: Implements non-inline SOF operation helpers for PCI/register bit updates and DSP panic handling.

Important APIs: `snd_sof_pci_update_bits()` updates PCI config dword bits under `sdev->hw_lock`. `snd_sof_dsp_update_bits_unlocked()`, `snd_sof_dsp_update_bits64_unlocked()`, locked 32/64-bit variants, and `snd_sof_dsp_update_bits_forced()` perform MMIO read-modify-write through ops wrappers. `snd_sof_dsp_panic()` records/validates panic offset, dumps debug information, marks fatal panics as `SOF_FW_CRASHED`, and notifies tracing.

Control flow: Update helpers compute `(old & ~mask) | (value & mask)`, skip writes if unchanged except forced update, and lock only in public locked variants. Panic handling stores `dsp_oops_offset` if unset, warns if offsets disagree, resets dump state, performs fatal or recoverable dump, and on fatal sets firmware state crashed and calls `sof_fw_trace_fw_crashed()`.

Dependencies and integration: Used by platform drivers, loader, PM, IPC exception paths, and MediaTek boot/clock code. Depends on PCI devices for PCI update, SOF MMIO ops for DSP update, `hw_lock`, and debug dump callbacks.

State and persistence: Mutates hardware registers, `dsp_oops_offset`, `dbg_dump_printed`, and firmware state.

Risks: Unlocked helpers require caller-side locking. PCI helper assumes `sdev->dev` is a PCI device. Panic offset disagreement may indicate firmware/kernel layout mismatch but only warns. Forced update is needed for RWC registers, but using normal update on RWC bits can lose events.

Test signals: Register bit updates with changed/unchanged values, 64-bit registers, forced RWC writes, concurrent callers, fatal and recoverable panic paths, and PCI-only helper use on PCI devices.
