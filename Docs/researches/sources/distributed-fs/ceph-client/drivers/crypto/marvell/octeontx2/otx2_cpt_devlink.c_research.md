# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_devlink.c Research

## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_devlink.c

### Purpose
`otx2_cpt_devlink.c` exposes OcteonTX2 CPT PF runtime controls and firmware-version reporting through devlink. It lets users create/delete custom engine groups, toggle a hardware `t106_mode` bit when safe, and report running AE/SE/IE microcode versions.

### Important APIs, Types, And Functions
Public APIs are `otx2_cpt_register_dl()` and `otx2_cpt_unregister_dl()`. Devlink parameter handlers include `otx2_cpt_dl_egrp_create()`, `otx2_cpt_dl_egrp_delete()`, `otx2_cpt_dl_uc_info()`, `otx2_cpt_dl_t106_mode_get()`, and `otx2_cpt_dl_t106_mode_set()`. Info reporting uses `otx2_cpt_dl_info_firmware_version_put()` and `otx2_cpt_devlink_info_get()`. Driver params are `egrp_create`, `egrp_delete`, and `t106_mode`.

### Control Flow, State, And Persistence
Registration allocates a devlink instance with private `struct otx2_cpt_devlink`, links it to the PF state, registers driver params, and registers the devlink object. Engine-group create/delete params forward string contexts to PF microcode helpers. `t106_mode_get` reads `CPT_AF_CTL` through the AF/PF mailbox; `set` refuses changes when VFs are enabled or engine groups exist, then updates bit 18 only on devices with SGV2 support. Info-get scans engine groups for reserved engines of each type and emits running firmware versions as `fw.ae`, `fw.se`, and `fw.ie`. Unregister reverses devlink and parameter registration.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on devlink, PF state, PF microcode helpers, AF register mailbox functions, engine group data, and SGV2 feature gating. Risks include devlink parameter side effects using string set operations, missing extack messages on failures, reading AF registers without checking return in get, ensuring `t106_mode` is immutable once VFs/groups exist, and firmware-version reporting when groups are mirrored or absent. Test signals include devlink param registration, create/delete custom groups, t106 get/set before and after VF enable, devlink info reporting with AE/SE/IE firmware, register failure injection, and unregister on PF remove.
