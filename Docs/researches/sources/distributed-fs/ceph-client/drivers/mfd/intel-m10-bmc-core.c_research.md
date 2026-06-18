# sources/distributed-fs/ceph-client/drivers/mfd/intel-m10-bmc-core.c

Purpose: common Intel MAX 10 BMC core used by SPI and PMCI transports. It provides system-register access helpers, sysfs identification attributes, firmware-update handshake protection, and MFD child registration.

Important APIs/types/functions: `m10bmc_fw_state_set()`, `m10bmc_sys_read()`, `m10bmc_sys_update_bits()`, `m10bmc_dev_init()`, `m10bmc_dev_groups`, `struct intel_m10bmc`, and `struct intel_m10bmc_platform_info`.

Control flow: transport drivers initialize `intel_m10bmc` and call `m10bmc_dev_init()`. The core stores platform info, attaches drvdata, initializes `bmcfw_lock`, and registers configured child cells. Sysfs attributes read BMC firmware/build and MAC information through `m10bmc_sys_read()`.

State and persistence: `bmcfw_state` is protected by an rwsem and gates access to handshake register ranges during secure update phases. No persistent state is written; it exposes hardware state via sysfs.

Dependencies and integration: integrates with regmap, MFD core, MAX10 CSR maps, and downstream hwmon/retimer/security-update child drivers. Exported symbols use namespace `INTEL_M10_BMC_CORE`.

Risks: handshake register access must return `-EBUSY` during prepare/write secure-update phases to avoid firmware collisions. CSR maps must match hardware generation. MAC formatting assumes N3000 field layout for exposed registers.

Test signals: sysfs reads for version and MAC data, child-device creation per platform, secure-update transitions that block handshake registers, and regmap error propagation from both SPI and PMCI transports.
