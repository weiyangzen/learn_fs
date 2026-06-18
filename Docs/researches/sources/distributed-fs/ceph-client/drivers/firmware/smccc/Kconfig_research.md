# sources/distributed-fs/ceph-client/drivers/firmware/smccc/Kconfig

## Purpose
This Kconfig file declares generic ARM SMCCC support, discovery support, and optional SoC bus registration through SMCCC `ARCH_SOC_ID`.

## Important Symbols
- `HAVE_ARM_SMCCC`: base architecture support for SMC/HVC instructions.
- `HAVE_ARM_SMCCC_DISCOVERY`: depends on `ARM_PSCI_FW`, defaults yes, and enables PSCI-mediated SMCCC v1.1+ discovery.
- `ARM_SMCCC_SOC_ID`: bool SoC bus device for SMCCC SOC_ID, depends on discovery, defaults yes, and selects `SOC_BUS`.

## Control Flow And Integration
PSCI initializes SMCCC version/conduit discovery. When discovery support is enabled, `smccc.o` and `kvm_guest.o` are built; SOC_ID support adds `soc_id.o`.

## State And Persistence
No runtime state is stored in Kconfig. The symbols determine whether SMCCC global version, KVM hypervisor service discovery, TRNG device registration, and SOC bus registration are available.

## Risks
Without PSCI firmware discovery, later SMCCC features are unavailable even if firmware implements them. SOC_ID depends on firmware returning valid version and revision.

## Test Signals
Build output should include SMCCC objects when enabled. Runtime logs and sysfs SoC device attributes validate discovery and SOC_ID behavior.
