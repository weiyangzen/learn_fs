# sources/distributed-fs/ceph-client/drivers/nvmem/snvs_lpgpr.c

Purpose: NVMEM provider for i.MX6/i.MX7 SNVS low-power general-purpose registers.

Important APIs/types/functions: `struct snvs_lpgpr_cfg` provides register offsets and size. `snvs_lpgpr_read()` uses regmap bulk read. `snvs_lpgpr_write()` checks high-power and low-power lock bits before regmap bulk write. Probe resolves the parent syscon regmap and registers 4-byte stride NVMEM.

Control flow: probe verifies OF node, gets compatible config, obtains parent node and syscon regmap, stores config, fills embedded NVMEM config, and registers. Writes first read lock registers and return `-EPERM` if software/hardware lock bits are set.

State/persistence: LPGPR registers reside in secure non-volatile/low-power storage and may survive resets depending on SNVS power domain. Driver state is regmap plus per-SoC offsets.

Dependencies/integration: compatibles `fsl,imx6q-snvs-lpgpr`, `fsl,imx6ul-snvs-lpgpr`, and `fsl,imx7d-snvs-lpgpr`; depends on parent syscon node.

Risks: source contains `struct device_d *dev` in private data, which appears unused and likely a typo but does not affect compiled access paths if accepted by the local tree. Writes are word-count based (`bytes / 4`) and rely on NVMEM alignment.

Test signals: lock-bit write rejection, i.MX6 versus i.MX7 offset/size selection, parent syscon lookup failure, and successful regmap read/write.
