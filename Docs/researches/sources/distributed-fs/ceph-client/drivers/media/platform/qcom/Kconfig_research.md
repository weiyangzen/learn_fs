# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/Kconfig

## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/Kconfig

Purpose: Top-level Qualcomm media platform Kconfig menu that groups Qualcomm media drivers and sources submenus for CAMSS, Iris, and Venus.

Important APIs/types/functions: This declarative file creates the `"Qualcomm media platform drivers"` comment and includes `drivers/media/platform/qcom/camss/Kconfig`, `iris/Kconfig`, and `venus/Kconfig`.

Control flow/state: No runtime state. Build configuration state flows from this file into child Kconfig files, making their options visible under the Qualcomm media platform area.

Dependencies/integration: Integrated by the kernel media platform Kconfig hierarchy. It is paired with the top-level Qualcomm Makefile that descends into the same subdirectories.

Risks/test signals: Risks are limited to missing or stale submenu source lines, which would hide drivers from configuration. Test with `make menuconfig` or `scripts/kconfig/conf` to ensure CAMSS/Iris/Venus options remain reachable.
