# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/output.c

## Purpose
`output.c` manages registered OMAP DSS output devices and provides the indirection layer from output drivers to installed manager operations. It connects outputs to display devices, finds outputs by id/name/OF port/display chain, and exports manager operation wrappers.

## Important APIs, types, and functions
Output APIs include `omapdss_output_set_device`, `omapdss_output_unset_device`, `omapdss_register_output`, `omapdss_unregister_output`, `omap_dss_get_output`, `omap_dss_find_output`, `omap_dss_find_output_by_port_node`, `omapdss_find_output_from_display`, and `omapdss_find_mgr_from_display`. Manager ops APIs include `dss_install_mgr_ops`, `dss_uninstall_mgr_ops`, `dss_mgr_connect`, `dss_mgr_disconnect`, timing/config setters, enable/disable/update, and framedone handler registration wrappers.

## Control Flow
Outputs register onto `output_list`. Set/unset device runs under `output_lock`, verifies single attachment, matching output/display type, and disabled state on unset, then links or clears `out->dst` and `dssdev->src`. Find helpers walk the list or climb `src` pointers. Manager wrappers dispatch through the globally installed `dss_mgr_ops`.

## State and Persistence
Runtime state is the global output list, `output_lock`, and global `dss_mgr_ops` pointer. Link state is stored in `struct omap_dss_device` `src`/`dst` fields. No state persists across driver lifetime.

## Dependencies and Integration Points
The file depends on OMAP DSS device structs, OF graph helper `dss_of_port_get_parent_device`, module exports, and a manager backend that installs `struct dss_mgr_ops`. HDMI, SDI, and VENC output drivers register outputs here.

## Risks
Register/unregister and lookup list walks are mostly unlocked except set/unset, so concurrent registration/removal would be unsafe if it happened after init. Manager wrappers assume `dss_mgr_ops` is installed and valid. `omapdss_find_output_from_display` relies on `id != 0` as an output test.

## Test Signals
Test output registration/removal, type mismatch rejection, duplicate connection rejection, unset while enabled, OF port lookup, display-chain manager lookup, manager ops install `-EBUSY`, and calls before/after manager ops installation.
