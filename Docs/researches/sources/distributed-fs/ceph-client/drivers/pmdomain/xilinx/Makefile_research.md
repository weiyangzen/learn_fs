<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/xilinx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/xilinx/Makefile

Purpose: Kbuild rule for Xilinx pmdomain support.

Important APIs/types/functions: maps `CONFIG_ZYNQMP_PM_DOMAINS` to `zynqmp-pm-domains.o`.

Control flow/state: build-time only.

Dependencies/integration: paired with the local Kconfig and Xilinx firmware driver.

Risks: config/object mismatch would omit PM domains.

Test signals: compile with `CONFIG_ZYNQMP_PM_DOMAINS=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/xilinx/Makefile -->
