<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_dg_nvm_aux.h -->
# sources/distributed-fs/ceph-client/include/linux/intel_dg_nvm_aux.h

Purpose: Defines auxiliary-bus data for Intel discrete graphics NVM devices.

Important APIs/types/functions: `INTEL_DG_NVM_REGIONS` sets a 13-region limit. `struct intel_dg_nvm_region` stores an MMIO/resource area and identifier. `struct intel_dg_nvm_dev` embeds an auxiliary device, region array/count, and writeable flag. `auxiliary_dev_to_intel_dg_nvm_dev()` maps from aux device to container.

Control flow: Parent graphics drivers populate regions and create an auxiliary device; NVM auxiliary drivers retrieve the container and access regions.

State/persistence: Region descriptors and writeability persist for the aux device lifetime.

Dependencies/integration: Depends on auxiliary bus, resources, container_of, and Intel graphics NVM drivers.

Risks: Region count must not exceed fixed array; incorrect writeable flag exposes unsafe writes.

Test signals: Aux device probe/remove, region enumeration, read-only versus writeable operations, and bounds checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_dg_nvm_aux.h -->
