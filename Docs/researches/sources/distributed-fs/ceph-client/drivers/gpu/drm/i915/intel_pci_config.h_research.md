# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_pci_config.h

Purpose: defines legacy Intel graphics PCI configuration offsets, BAR indices, and bit fields used by i915 setup and chipset control paths.

Important APIs/macros: provides BAR constants for gen2/gen3/gen4+ and gen12 LMEM, `intel_mmio_bar(graphics_ver)`, MCHBAR offsets and enable bits, reset-domain fields, legacy clock-control fields, display/render clock masks, OpRegion ASLE/ASLS, SWSCI bits, and backlight mode register `LBPC`.

Control flow: the only executable helper maps graphics version to the MMIO BAR: gen2 uses `GEN2_MMADR_BAR`, gen3 uses `GEN3_MMADR_BAR`, and later versions use `GEN4_GTTMMADR_BAR`.

State and persistence: no software state; macros describe PCI config space fields that persist in hardware/firmware configuration until changed by driver/platform.

Dependencies and integration: consumed by PCI probe, MMIO mapping, reset, clock, OpRegion, and legacy platform setup code.

Risks: generation-specific BAR indices are critical; using the wrong BAR maps the wrong resource. Several fields are legacy or empirically documented, so platform guards matter.

Test signals: device probe on gen2/3/4+ platforms, PCI resource mapping logs, reset-domain tests, and legacy display/backlight behavior.
