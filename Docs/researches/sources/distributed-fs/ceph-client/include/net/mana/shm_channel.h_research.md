<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mana/shm_channel.h -->
# sources/distributed-fs/ceph-client/include/net/mana/shm_channel.h

## Purpose
`shm_channel.h` defines the shared-memory bootstrap channel used by MANA to initialize or tear down the hardware communication channel before normal GDMA queues are available.

## Important APIs, types, and functions
It defines aperture geometry constants, `struct shm_channel`, and public functions `mana_smc_init`, `mana_smc_setup_hwc`, and `mana_smc_teardown_hwc`.

## Control flow
The driver initializes a shared-memory channel with a device and MMIO base, then uses setup to pass HWC EQ/CQ/RQ/SQ DMA addresses and an MSI-X index to firmware. Teardown optionally resets the VF and dismantles HWC bootstrap state.

## State and persistence
State is the device pointer and MMIO base plus firmware-visible bootstrap registers. There is no persistent software store; hardware retains setup until teardown or reset.

## Dependencies and integration points
It depends on MMIO access in the implementation and is included by GDMA context setup. It integrates PCI BAR shared-memory windows with HWC queue creation.

## Risks and test signals
Risks include aperture-size assumptions, wrong queue DMA addresses, reset-vs-no-reset teardown semantics, and MMIO ordering. Tests should cover VF bootstrap, teardown, reset paths, and invalid or missing shared-memory BAR mappings.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mana/shm_channel.h` completely for this pass (27 lines, 796 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mana/shm_channel.h -->
