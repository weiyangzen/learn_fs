<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpss-pci.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpss-pci.c

Purpose: is the PCI front-end for Intel LPSS PWM controllers. It binds PCI IDs, maps BAR0, selects board info, and delegates all waveform logic to the shared LPSS core.

Important APIs/types/functions: `pwm_lpss_probe_pci()` enables the PCI device, ioremaps BAR0 through `pcim_iomap_regions()`, calls `devm_pwm_lpss_probe()`, and stores the returned chip. `pwm_lpss_remove_pci()` calls `pwm_lpss_remove()`. The ID table maps Bay Trail, Braswell, Broxton, and Tangier device IDs to exported `pwm_lpss_*_info` descriptors.

Control flow: module PCI probe performs managed PCI enable/mapping and shared-core registration. Remove asks the LPSS core to stop/remove any registered PWM chip state.

State and persistence: this file owns no waveform state. PCI core and shared `struct pwm_lpss_chip` hold runtime state after probe.

Dependencies and integration: depends on PCI APIs, LPSS shared core and header, module namespace import `PWM_LPSS`, and Intel LPSS device IDs.

Risks and test signals: wrong ID-to-boardinfo mapping changes period limits and channel count. Test each supported PCI ID, BAR mapping failure, remove/unbind while PWM is enabled, and namespace/export linkage with `pwm-lpss.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpss-pci.c -->
