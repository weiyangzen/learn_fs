<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/xilinx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/xilinx/Kconfig

Purpose: Build configuration for ZynqMP generic PM domains.

Important APIs/types/functions: `ZYNQMP_PM_DOMAINS` is a default-y bool depending on `PM` and `ZYNQMP_FIRMWARE`, selecting `PM_GENERIC_DOMAINS`.

Control flow/state: build-time only.

Dependencies/integration: ensures the driver is present when Xilinx firmware PM calls are available.

Risks: default-y includes the provider broadly on firmware-enabled ZynqMP builds.

Test signals: enabled config builds `zynqmp-pm-domains.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/xilinx/Kconfig -->
