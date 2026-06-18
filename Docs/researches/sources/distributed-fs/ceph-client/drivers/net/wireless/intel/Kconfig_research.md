# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/Kconfig

Purpose: Provides the top-level Kconfig menu gate for Intel wireless drivers.

Important APIs/configs: `WLAN_VENDOR_INTEL` is a boolean menu option defaulting to `y`. When enabled, it sources the `ipw2x00`, `iwlegacy`, and `iwlwifi` Kconfig files.

Control flow and state: Kconfig flow only. Disabling this option hides Intel driver prompts without directly changing object selection elsewhere unless dependent symbols are unreachable.

Dependencies and integration: Integrated from the wireless vendor Kconfig hierarchy. It controls visibility of Intel legacy and modern driver configuration. Risks include confusing default behavior, hidden symbols when vendor gate is off, and source path mismatches if driver directories move. Test signals include `menuconfig` visibility, randconfig coverage with vendor gate on/off, and Kconfig dependency checks for sourced subtrees.
