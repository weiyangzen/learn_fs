# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/link-selection.c

Purpose: Provides KUnit coverage for MLO link grading and EMLSR pair eligibility decisions.

Important APIs and functions: `test_link_grading()` validates `iwl_mld_get_link_grade()` under channel-util and active-load inputs. `test_iwl_mld_link_pair_allows_emlsr()` validates `iwl_mld_emlsr_pair_state()` for bandwidth ratio, channel load, low latency, primary-link activity, and same-band restrictions.

Control flow: Tests build synthetic associated MLO/non-MLO VIFs using `utils.c`, attach BSS load IEs or PHY channel load as needed, call production link-selection helpers under the wiphy lock, and compare exact grades or exit-reason bitmasks.

State and persistence: Uses KUnit-allocated VIF/link/chanctx/PHY objects and updates test PHY load fields. State is per-test only.

Dependencies and integration points: Depends on KUnit static stubs, MLD link/interface/PHY/MLO production headers, and shared channel definitions from `utils.h`. It exercises policy logic used by internal MLO scan completion and stats-triggered EMLSR decisions.

Risks: Expected grade values are policy-coupled and will need updates if scoring weights change. The cases cover representative pairs but not every regulatory/channel-width combination or RSSI threshold.

Test signals: Existing tests signal regressions in channel utilization grading, active-link load adjustment, EMLSR channel-load thresholds, low-latency override, bandwidth-ratio gating, and same-band disallow/allow cases.
