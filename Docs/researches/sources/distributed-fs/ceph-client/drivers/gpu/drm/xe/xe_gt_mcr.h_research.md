# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_mcr.h

## Purpose
Declares MCR initialization, steering lookup, MCR register accessors, diagnostics, and DSS steering iteration helpers.

## Important APIs
- Init/defaults: `xe_gt_mcr_init_early`, `xe_gt_mcr_init`, `xe_gt_mcr_set_implicit_defaults`.
- Accessors: unicast read-any, explicit unicast read/write, and multicast write.
- Steering conversion: `xe_gt_mcr_get_nonterminated_steering`, `xe_gt_mcr_get_dss_steering`, `xe_gt_mcr_steering_info_to_dss_id`.
- `for_each_dss_steering` wraps topology DSS iteration with steering conversion.

## Integration and Risks
Callers must hold appropriate forcewake domains before MCR MMIO access. The API is PF/native only; implementation asserts against SR-IOV VF use. `for_each_dss_steering` depends on initialized GT topology and steering layout.
