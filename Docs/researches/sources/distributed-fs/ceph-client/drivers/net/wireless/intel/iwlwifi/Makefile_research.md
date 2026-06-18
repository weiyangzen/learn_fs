# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/Makefile

## Purpose
The top-level `iwlwifi/Makefile` composes the shared Intel wireless module and conditionally includes bus, firmware, configuration, opmode, debug, ACPI/EFI, MEI, MLD, and test objects according to Kconfig symbols.

## Important APIs, Types, and Build Targets
- Main target: `obj-$(CONFIG_IWLWIFI) += iwlwifi.o`.
- Shared objects: IO, driver core, debug, NVM utils/parse, PHY DB, transport, firmware debug/dump/regulatory/pnvm.
- PCI transport objects: context info, driver, utilities, Gen1/2 RX/TX/transport.
- Config tables: DVM-era combined MAC/RF configs for 1000/2000/5000/6000, MVM configs for 7000/8000/9000/22000/AX210/BZ/SC and RF files, MLD configs for BZ/SC/DR and RF files.
- Subdirectories: `dvm/`, `mvm/`, `mei/`, `mld/`, and `tests/`.
- Conditional additions: `iwl-devtrace.o`, ACPI/UEFI helpers, debugfs firmware helpers.

## Control Flow and Integration
Kbuild first builds the common `iwlwifi.o` module from shared objects and selected config table objects. Opmodes are built as subdirectory modules or built-ins based on `IWLDVM`, `IWLMVM`, and `IWLMLD`. `iwlwifi-objs += $(iwlwifi-m)` folds conditional object fragments into the common module.

## State and Persistence Behavior
No runtime state is stored here. The file determines the binary composition of the driver and which exported config structures are present for PCI ID matching and firmware selection.

## Dependencies and Integration Points
It consumes symbols from `Kconfig`, includes headers with `ccflags-y += -I$(src)`, suppresses override-init warnings for `pcie/drv.o`, and wires firmware, transport, config, and opmode subsystems together.

## Risks and Edge Cases
- Duplicate inclusion of shared config files across MVM and MLD must remain intentional and link-safe.
- Missing a new cfg object means PCI IDs may reference unavailable config symbols.
- Feature-specific objects must align with Kconfig dependencies, especially debugfs, ACPI, EFI, tracing, tests, and opmode modularity.

## Test Signals
Run kbuild matrix for all relevant `IWLWIFI`, `IWLDVM`, `IWLMVM`, `IWLMLD`, `IWLMEI`, `ACPI`, `EFI`, `DEBUGFS`, tracing, and KUnit combinations; check modpost for unresolved config symbols and duplicate definitions.
