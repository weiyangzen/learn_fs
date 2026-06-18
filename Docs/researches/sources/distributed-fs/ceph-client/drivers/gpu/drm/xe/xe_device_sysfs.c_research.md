<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device_sysfs.c

## Purpose
`xe_device_sysfs.c` creates PCI-device sysfs attributes for device-level Xe knobs and read-only platform status. It exposes runtime D3cold VRAM threshold control, late-binding fan and voltage-regulator version reporting, and Battlemage PCIe Gen5 auto-link-downgrade capability/status.

## Important APIs, types, and functions
`vram_d3cold_threshold_show()` and `_store()` read and update `xe->d3cold.vram_threshold` through `xe_pm_set_vram_threshold()` under runtime PM. `lb_fan_control_version_show()` and `lb_voltage_regulator_version_show()` query PCODE late-binding capability and version mailboxes and format major.minor.hotfix.build. `late_bind_attr_is_visible()` hides version files unless PCODE reports support. `auto_link_downgrade_capable_show()` reads `BMG_PCIE_CAP`, while `auto_link_downgrade_status_show()` reads DGFX init status through PCODE. `xe_device_sysfs_init()` installs managed attribute groups conditionally.

## Control flow and integration points
Initialization adds the VRAM group only when `xe->d3cold.capable` is true. Battlemage non-VF devices get auto-link-downgrade and late-bind groups. All hardware reads run under `guard(xe_pm_runtime)(xe)` so sysfs access wakes the device safely. The attributes integrate with PM policy, PCODE mailbox definitions, MMIO register definitions, and PCI device kobjects.

## State and persistence behavior
Only the D3cold threshold is mutable persistent driver state; it is protected inside `xe_pm_set_vram_threshold()`. Version and link files are live hardware/firmware views. The groups are devm-managed and are removed with the device.

## Dependencies, risks, and test signals
Dependencies include PCI sysfs, runtime PM, PCODE mailbox APIs, root-tile MMIO, SR-IOV mode, and Battlemage register fields. Risks include exposing attributes on unsupported hardware, failing PCODE reads while sysfs visibility is evaluated, incorrect runtime-PM nesting, and user-visible D3cold policy regressions. Test signals are sysfs presence/absence by platform/VF mode, read/write threshold behavior, PCODE error propagation, link downgrade field decoding, and suspend/resume with sysfs polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device_sysfs.c -->
