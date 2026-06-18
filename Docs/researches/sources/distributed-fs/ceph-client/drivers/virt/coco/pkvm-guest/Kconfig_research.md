# sources/distributed-fs/ceph-client/drivers/virt/coco/pkvm-guest/Kconfig

## Purpose
Declares arm64 pKVM protected guest support.

## APIs, Types, and Functions
`ARM_PKVM_GUEST` is a bool depending on `ARM64` and `DMA_RESTRICTED_POOL`.

## Control Flow and State
Build-time only. The driver registers memory encryption/decryption and optional MMIO guard hooks at runtime.

## Dependencies and Integration
Integrates with arm64 protected KVM SMCCC services and DMA restricted-pool support.

## Risks and Test Signals
Build-test arm64 protected guest configs and ensure unsupported systems leave the hooks unregistered.
