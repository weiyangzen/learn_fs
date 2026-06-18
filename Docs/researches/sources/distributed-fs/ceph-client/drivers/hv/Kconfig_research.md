# sources/distributed-fs/ceph-client/drivers/hv/Kconfig

## Purpose
Defines build configuration for Microsoft Hyper-V guest and root/VTL support drivers.

## Important APIs, Types, and Functions
Kconfig options include `HYPERV`, `HYPERV_VTL_MODE`, `HYPERV_TIMER`, `HYPERV_UTILS`, `HYPERV_BALLOON`, `HYPERV_VMBUS`, `MSHV_ROOT`, and `MSHV_VTL`.

## Control Flow
The menu exposes core hypervisor support first, then dependent drivers. `HYPERV_VMBUS` defaults to `HYPERV`; utilities, balloon, root partition, and VTL drivers depend on core VMBus or VTL-mode capabilities.

## State and Persistence
No runtime state. The selected `.config` controls which Hyper-V objects are built and whether core support is built in.

## Dependencies and Integration Points
Depends on architecture/hypervisor symbols, paravirt, local APIC or ARM64 constraints, connector/NLS/PTP for utilities, page reporting for ballooning, and memory-management features for root/VTL drivers.

## Risks and Test Signals
Risks include invalid architecture combinations, VTL-mode assumptions, and page-size constraints for root partition support. Test signals include build coverage for x86_64 and ARM64, VMBus built-in default behavior, and dependency resolution for utility/balloon/root/VTL modules.
