<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_utils.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_utils.h

Purpose: provides tiny atomic flag helpers used throughout the Atlantic driver to set, clear, and test object state bits.

Important APIs/functions: `aq_utils_obj_set`, `aq_utils_obj_clear`, and `aq_utils_obj_test` operate on `atomic_t` flag words and 32-bit masks.

Control flow: set/clear use compare-exchange loops to avoid losing concurrent flag updates. Test returns the current masked bits. NIC and hardware code use these helpers for readiness, link-down, PTP datapath, unplug, and hardware-error flags.

State and persistence: no independent state. The helpers mutate caller-provided atomic flag fields.

Dependencies and integration: includes `aq_common`; used in NIC lifecycle, PTP filter state, hardware error/unplug handling, and other driver modules.

Risks: masks must fit the atomic flag layout; callers still need higher-level synchronization for compound state transitions; test returns a boolean interpretation of any matching bit, not an exact equality. Test signals include concurrent link/service/IRQ paths and fault paths that set or clear readiness/error bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_utils.h -->
