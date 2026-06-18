# sources/distributed-fs/ceph-client/drivers/ufs/host/ufshcd-pci.c

## Purpose
`ufshcd-pci.c` is the PCI bus glue for UFS host controllers. It maps PCI BAR resources, allocates and initializes `ufs_hba`, selects vendor-specific variant operations for QEMU and Intel platforms, manages PCI runtime/system PM, and implements Intel-specific DSM reset, LTR latency tolerance, debugfs, quirks, crypto enablement, and link-resume handling.

## Important APIs, Types, And Functions
The file registers `ufshcd_pci_driver` with `ufshcd_pci_probe()` and `ufshcd_pci_remove()`. `struct intel_host` stores ACPI DSM function bits, active/idle LTR cache, saved system PM level, debugfs root, and optional reset GPIO. Intel helper families include DSM (`intel_dsm_init()`, `intel_dsm()`), link and LCC callbacks, LKF power-change/device-quirk logic, LTR/debugfs (`intel_ltr_set()`, `intel_add_debugfs()`), reset (`ufs_intel_device_reset()`), common init/exit, and per-platform init functions for CNL/EHL/LKF/ADL/MTL.

QEMU MCQ support is implemented by `ufs_qemu_get_hba_mac()`, `ufs_qemu_mcq_config_resource()`, and `ufs_qemu_op_runtime_config()`. The PCI ID table maps Red Hat/QEMU and multiple Intel device IDs to variant ops.

## Control Flow And State
Probe enables the PCI device, sets bus mastering, maps BAR0 with `pcim_iomap_region()`, allocates an HBA, assigns variant ops from `id->driver_data`, and calls `ufshcd_init()`. Remove forbids runtime PM, grabs the device without resume, and removes the HBA.

Intel common init enables runtime autosuspend, allocates `intel_host`, probes ACPI DSM support, chooses DSM reset or reset GPIO, exposes PM QoS latency tolerance, and creates debugfs LTR files. Platform-specific init adds quirks and caps: EHL/CNL handle broken auto-Hibern8, LKF adds crypto and reset-focused PM levels, ADL performs link startup once and WriteBooster, MTL adds crypto/WriteBooster with shallower PM levels. Resume exits Hibern8 if necessary or forces link-off for full recovery. System suspend preparation temporarily raises Intel non-s2idle suspend to power-off level 5 and restores the saved level on complete.

## Dependencies And Integration Points
This file depends on PCI core, runtime PM, PM QoS, suspend state, debugfs, ACPI DSM, GPIO descriptors, and UFS core APIs. Intel ACPI DSM GUID functions provide reset capability discovery and execution. QEMU MCQ integration reads standard MCQ config offsets from emulated registers.

## Risks And Edge Cases
If no variant ops are supplied for a PCI ID, the HBA falls back to no vendor ops, which may be acceptable only for standard controllers. Intel reset behavior depends on DSM result semantics or optional active-low GPIO. LTR writes are made under runtime PM get/put and update cached debugfs values; failures in PM resume could affect latency requests. Suspend preparation mutates `hba->spm_lvl` and must restore it on both failure and completion. QEMU MCQ uses a fixed stride of 48 and assumes emulated offset registers are valid.

## Test Signals
Test PCI probe/remove, BAR mapping, runtime PM enable/disable, QEMU MCQ operation queues, Intel DSM discovery/reset, GPIO reset fallback, debugfs LTR readback, PM QoS latency writes, s2idle versus non-s2idle suspend behavior, Hibern8 resume failure recovery, LKF lane/TACTIVATE quirks, and crypto enablement after HCE on LKF/MTL.
