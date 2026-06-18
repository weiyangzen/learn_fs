<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/acpi.h -->
# sources/distributed-fs/ceph-client/include/xen/acpi.h

## Purpose
This header connects ACPI sleep and interrupt routing behavior to Xen Dom0/PVH support. It provides hooks for notifying the hypervisor about ACPI sleep and querying or setting up GSI routing.

## Important APIs, Types, And Functions
- `get_gsi_from_sbdf_t` is a callback type for mapping PCI segment/bus/device/function encoding to a GSI.
- Under `CONFIG_XEN_DOM0`, exported functions notify Xen about normal and extended sleep, set up PVH GSI routing, query PCI GSI trigger/polarity, register the SBDF callback, and resolve GSI from SBDF.
- `xen_acpi_suspend_lowlevel()` bypasses native CPU context save because Xen handles CPU context.
- `xen_acpi_sleep_register()` installs Xen ACPI prepare-sleep hooks and low-level suspend only for `xen_initial_domain()`.
- Without Dom0 support, stubs return `-1` or do nothing.

## Control Flow
During ACPI initialization in a Xen initial domain, `xen_acpi_sleep_register()` replaces ACPI prepare-sleep callbacks with Xen-aware versions and points `acpi_suspend_lowlevel` at the Xen suspend helper. PCI/GSI code calls the Xen helpers to communicate routing to the hypervisor.

## State And Persistence
State is in global ACPI callback pointers and the registered SBDF-to-GSI callback in the implementation. Sleep state is communicated to Xen rather than persisted here.

## Dependencies And Integration Points
It depends on ACPI core, Xen domain detection, Xen hypervisor support, PCI devices, and Dom0/PVH interrupt routing code.

## Risks And Edge Cases
Hooks must only be installed in the Xen initial domain. Stub functions returning `-1` require callers to handle non-Xen builds. The function prototype names `pm1b_cnd` in one declaration, likely a typo, but ABI remains by position.

## Test Signals
Signals include ACPI S3 requests notifying Xen, PVH GSI setup succeeding with correct trigger/polarity, SBDF callback registration/use, and non-Xen or non-Dom0 builds taking the stub path safely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/acpi.h -->
