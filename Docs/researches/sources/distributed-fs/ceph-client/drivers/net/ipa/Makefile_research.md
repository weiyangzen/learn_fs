# sources/distributed-fs/ceph-client/drivers/net/ipa/Makefile

## Purpose
`ipa/Makefile` defines the object composition for the Qualcomm IPA driver. It builds the core IPA object from common driver sources plus versioned IPA, GSI, and SoC data objects.

## Important APIs, types, and functions
The important build variables are `IPA_REG_VERSIONS`, `GSI_REG_VERSIONS`, and `IPA_DATA_VERSIONS`, which expand into `reg/ipa_reg-v%.o`, `reg/gsi_reg-v%.o`, and `data/ipa_data-v%.o`. `obj-$(CONFIG_QCOM_IPA) += ipa.o` ties the composite object to Kconfig.

## Control flow
When `CONFIG_QCOM_IPA` is enabled, Kbuild creates `ipa.o` from core objects such as `ipa_main.o`, `ipa_power.o`, `gsi.o`, endpoint/command/modem/QMI/sysfs code, all listed IPA register descriptions, all listed GSI register descriptions, and all listed IPA data descriptions.

## State and persistence
There is no runtime state. The file is build metadata; its persistent effect is which version tables and support modules are linked into the IPA driver.

## Dependencies and integration points
The Makefile integrates Kconfig with the source layout under `drivers/net/ipa`, including `reg/` and `data/` generated/static version files. It must remain synchronized with version enums and lookup code in the core driver.

## Risks and test signals
Risks include adding a new version file without updating the corresponding version list, listing data without matching runtime selection logic, or removing a core object needed by module init/probe. Test signals include incremental and clean builds for `CONFIG_QCOM_IPA=m/y`, link checks for every versioned object, and probe tests for SoCs matching each `ipa_data-v*.o`.
