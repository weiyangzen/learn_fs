# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine.c

Purpose: discovers, filters, initializes, controls, and snapshots physical hardware engines for a GT. It maps engine IDs to classes/MMIO bases/IRQ offsets/forcewake domains, applies workarounds and tuning, enables rings, handles engine IRQs, and exposes lookup/utility helpers.

Important functions/types: static `engine_infos`, `xe_hw_engines_init_early`, `xe_hw_engines_init`, `hw_engine_init_early`, `hw_engine_init`, `xe_hw_engine_enable_ring`, `xe_hw_engine_setup_default_lrc_state`, `xe_hw_engine_mmio_read32/write32`, fuse readers for media/copy/compute engines, GSC availability and configfs filtering, `xe_hw_engine_handle_irq`, snapshot capture/free/print, reservation checks, class string conversion, timestamp read, forcewake domain lookup, and UAPI class-instance lookup.

Control flow: early init reads fuses and software disable masks, disables unavailable GSC engine, fills each valid `struct xe_hw_engine`, initializes scheduling defaults per class, processes tuning/workaround/register whitelist state, and prepares default register save/restore tables. Full init applies register state, creates an HWSP BO, creates execlist ports when GuC is disabled or enables rings when GuC is enabled, adjusts IDLEDLY, registers cleanup, computes logical instances, and sets up hardware engine groups.

State/persistence: each engine persists GT pointer, class/instance/logical instance, MMIO base, IRQ offset, forcewake domain, HWSP BO, execlist port or GuC ring state, per-class scheduling interface, register state tables, optional IRQ handler, and group pointer. `gt->info.engine_mask` is destructively filtered by fuses/config before engine objects are initialized.

Dependencies/integration: integrates registers, forcewake, MMIO, BO/HWSP allocation, execlist backend, GuC/GSC support, GT topology, CCS mode, configfs engine disabling, tuning/workaround/RTP frameworks, hw fences, IRQ dispatch, devcoredump/GuC capture, and UAPI engine class mapping.

Risks/test signals: engine mask filtering affects user-visible engine availability. Forcewake must be held for engine-relative MMIO helpers. GSC engine timeout and availability logic are platform-sensitive. Snapshot code has different behavior for VF and GuC capture availability. Test fuse combinations, configfs engine masks, GuC versus execlist init, MSI-X IRQ offsets, compute/copy/media engine masks, reserved engines (OTHER, CCS mode, USM BCS), ring enable register writes, and lookup bounds/nospec behavior.
