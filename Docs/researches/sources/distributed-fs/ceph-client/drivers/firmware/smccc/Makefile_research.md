# sources/distributed-fs/ceph-client/drivers/firmware/smccc/Makefile

## Purpose
The Makefile maps SMCCC discovery and SOC_ID configuration to object files.

## Important Build Rules
- `obj-$(CONFIG_HAVE_ARM_SMCCC_DISCOVERY) += smccc.o kvm_guest.o`
- `obj-$(CONFIG_ARM_SMCCC_SOC_ID) += soc_id.o`

## Control Flow And Integration
Generic SMCCC discovery and KVM guest service discovery are linked together. SOC bus registration is independent but depends on discovery through Kconfig.

## State And Persistence
No runtime state; linkage only.

## Risks
Missing `kvm_guest.o` with discovery would break PSCI's call to `kvm_init_hyp_services()`. Missing `soc_id.o` only removes sysfs SoC identity.

## Test Signals
Successful link should resolve SMCCC global discovery and KVM service functions referenced by PSCI and architecture code.
