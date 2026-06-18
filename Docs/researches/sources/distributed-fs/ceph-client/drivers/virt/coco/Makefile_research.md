# sources/distributed-fs/ceph-client/drivers/virt/coco/Makefile

## Purpose
Build dispatch for confidential-computing support.

## APIs, Types, and Functions
Selects subdirectories and `tsm-core.o`: `efi_secret/`, `pkvm-guest/`, `sev-guest/`, `tdx-guest/`, `arm-cca-guest/`, `guest/`, and `tsm-core.o`.

## Control Flow and State
No runtime control flow. It maps Kconfig symbols to build artifacts.

## Dependencies and Integration
`CONFIG_TSM_GUEST` pulls in shared report/measurement helpers; vendor drivers select those shared symbols. `CONFIG_TSM` builds the class device used by PCI TSM integrations.

## Risks and Test Signals
Build risk is symbol mismatch or missing subdirectory dependencies. Test by building representative configs with all symbols as built-in and as modules where allowed.
