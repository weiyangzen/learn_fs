# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_devlink.h

Purpose: Declares SFC devlink lifecycle functions, EF100 devlink port helpers, and custom devlink info version-name constants.

Important APIs and definitions: Defines names such as `fw.mgmt.suc`, `fw.mgmt.cmc`, `fpga.rev`, `fpga.app`, `coproc.boot`, `coproc.uboot`, `coproc.main`, `coproc.recovery`, `fw.exprom`, and `fw.uefi`, plus `EFX_MAX_VERSION_INFO_LEN`. Declares probe/unlock/fini functions and, under `CONFIG_SFC_SRIOV`, PF and representor devlink port set/unset helpers.

Control flow and integration: Included by PCI core and representor code to bracket devlink registration with devl locking and to associate devlink ports with MAE mports.

State and persistence: Header owns no state. Constants define the stable names users see through `devlink info`.

Dependencies: Includes `net_driver.h` and `<net/devlink.h>`, with optional forward declaration of `struct efx_rep`.

Risks: Renaming version keys changes user-facing devlink ABI. Lifecycle callers must pair lock/unlock and free paths exactly.

Test signals: Build with and without `CONFIG_SFC_SRIOV`, verify `devlink info` key names, and probe/remove PF devices under devlink enabled kernels.
