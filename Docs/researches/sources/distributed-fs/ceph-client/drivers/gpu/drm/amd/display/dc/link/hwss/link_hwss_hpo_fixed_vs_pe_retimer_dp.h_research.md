# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_hpo_fixed_vs_pe_retimer_dp.h

## Purpose

`link_hwss_hpo_fixed_vs_pe_retimer_dp.h` declares the HPO DP fixed-VS/PE retimer HWSS selector helpers.

## Important APIs, Types, And Functions

It exposes `requires_fixed_vs_pe_retimer_hpo_link_hwss()` and `get_hpo_fixed_vs_pe_retimer_dp_link_hwss()`. The implementation delegates the requirement check to the DIO fixed-VS helper and returns a static HPO retimer `struct link_hwss`.

## Control Flow

No runtime flow exists in the header. Callers use these declarations when selecting an HPO DP HWSS variant based on link chip capabilities.

## State And Persistence Behavior

No state is held. The implementation mutates retimer, HPO encoder, and trace state.

## Dependencies And Integration Points

It includes `link_service.h` for link and HWSS types. It is consumed by HWSS selection code and the implementation file.

## Risks And Edge Cases

The small interface hides the fact that the implementation depends on DIO fixed-VS helpers. If those helper semantics change, HPO retimer behavior changes too. Build coverage is the main guard for signature drift.

## Test Signals

HPO DP fixed-VS link selection, successful DP 2.x training, PHY pattern programming, and retimer AUX write logs validate this interface indirectly.
