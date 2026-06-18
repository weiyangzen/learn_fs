# sources/distributed-fs/ceph-client/include/linux/soc/qcom/socinfo.h

Purpose: This header defines the Qualcomm SMEM socinfo layout and feature-code/product-code helpers.

Important APIs/types/functions: It defines SMEM item and string lengths, `SOCINFO_MAJOR`, `SOCINFO_MINOR`, `SOCINFO_VERSION`, packed `struct socinfo` fields for format/version/build IDs/chip IDs/serial/platform/PMIC/feature data, `enum qcom_socinfo_feature_code`, and product-code helpers such as `SOCINFO_PCn`.

Control flow: The socinfo driver reads the SMEM socinfo item, interprets fields by format version, publishes SoC identity, and exposes feature/product codes to other drivers.

State and persistence: Data is bootloader/firmware-populated SMEM state, usually persistent for the boot lifetime.

Dependencies and integration: Integrates with `qcom_smem_get`, Linux soc bus registration, debugfs/sysfs style identity reporting, and Qualcomm driver quirk selection.

Risks and test signals: Format-version changes require careful bounds checks; reading fields not present in older formats can misreport identity. Test old/new socinfo formats, feature-code decode, build/chip ID strings, and SMEM absence handling.
