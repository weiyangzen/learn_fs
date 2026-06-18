# sources/distributed-fs/ceph-client/drivers/fwctl/bnxt/Makefile

## Purpose
This Kbuild file builds the Broadcom BNXT fwctl provider.

## Important Entries
`obj-$(CONFIG_FWCTL_BNXT) += bnxt_fwctl.o` and `bnxt_fwctl-y += main.o` map the Kconfig symbol to the provider implementation.

## Control Flow and State
No runtime behavior is defined here.

## Dependencies and Integration Points
The object depends on the parent `bnxt_en` driver infrastructure and the fwctl core namespace.

## Risks and Test Signals
Configuration-only risks include provider build breakage when BNXT internal headers change. Test with `FWCTL_BNXT=m` and parent BNXT built as both module and built-in where supported.
