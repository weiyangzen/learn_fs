# sources/distributed-fs/ceph-client/drivers/iommu/amd/quirks.c

Purpose: applies DMI-based AMD IVRS quirks for systems whose firmware reports incorrect IOAPIC device IDs.

Important APIs, types, and functions: `struct ivrs_quirk_entry` stores IOAPIC ID to device ID pairs; `ivrs_ioapic_quirk_cb()` calls `add_special_device()` for each pair; `amd_iommu_apply_ivrs_quirks()` runs `dmi_check_system()`. The quirk table covers Dell Inspiron 7375, Dell Latitude 5495, Acer Aspire A315-41, and Lenovo ideapad 330S-15ARR.

Control flow: during AMD IOMMU init, `amd_iommu_apply_ivrs_quirks()` scans DMI matches. On match, the callback injects special IOAPIC mappings before normal IVRS-derived interrupt-remapping setup consumes them.

State and persistence: no runtime mutable state beyond the global special-device maps updated by `add_special_device()`. Tables are `__initconst`, and the public function is `__init`.

Dependencies and integration points: compiled only with `CONFIG_DMI`, depends on AMD IVRS parsing helpers from `amd_iommu.h`, and affects x86 interrupt remapping because IOAPIC source IDs must map to the right IOMMU device IDs.

Risks: overly broad DMI matches could change interrupt-remapping IDs on unrelated machines. Missing quirks leave affected systems with broken IOAPIC interrupt remapping. The callback treats zero as the sentinel, so quirk entries cannot use zero-valued id/devid pairs.

Test signals: boot logs on listed systems should show corrected IOAPIC mapping behavior; regression tests are mainly DMI match audits and interrupt-remapping smoke tests on affected hardware.
