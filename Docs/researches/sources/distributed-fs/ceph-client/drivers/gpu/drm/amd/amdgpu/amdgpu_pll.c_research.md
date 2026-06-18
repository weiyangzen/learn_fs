
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_pll.c

## Purpose
Computes pixel PLL divider settings and finds opportunities to share existing PPLLs across CRTCs. This is display clock plumbing for legacy ATOMBIOS/DC paths that need reference, feedback, fractional feedback, and post divider values matching a requested pixel clock.

## Important APIs, Types, and Functions
`amdgpu_pll_compute` is the main exported computation routine. Helpers `amdgpu_pll_reduce_ratio` and `amdgpu_pll_get_fb_ref_div` reduce target/reference ratios and clamp divider values. `amdgpu_pll_get_use_mask` reports active PPLL IDs. `amdgpu_pll_get_shared_dp_ppll` reuses an existing DP PPLL, while `amdgpu_pll_get_shared_nondp_ppll` reuses non-DP PPLLs when connector, mode clock, adjusted clock, and spread-spectrum state match.

## Control Flow
PLL computation derives allowed feedback, reference, and post divider ranges from `struct amdgpu_pll` flags and limits. It scales by ten when fractional feedback is enabled, reduces the target/reference ratio, scans post dividers for the smallest clock error, recomputes final feedback/reference dividers, applies fractional-jitter avoidance, and writes results plus the computed dot clock. Sharing helpers walk `dev->mode_config.crtc_list`, skip the current CRTC, inspect `amdgpu_crtc` encoder and PLL state, and return `ATOM_PPLL_INVALID` when reuse is unavailable.

## State and Persistence Behavior
The file is mostly stateless; it reads CRTC state and PLL descriptors and returns computed values. Persistent state is maintained by callers in `amdgpu_crtc->pll_id`, `adjusted_clock`, connector, encoder, and spread-spectrum fields.

## Dependencies and Integration Points
Depends on DRM CRTC lists, AMDGPU CRTC state, ATOMBIOS encoder mode checks, `struct amdgpu_pll`, Linux `gcd`, and integer division helpers. It feeds display mode setting code that programs hardware PLL registers elsewhere.

## Risks and Test Signals
Risks include divider overflow or underflow when requested clocks sit outside PLL ranges, wrong fractional scaling, family-specific ref divider limits, and accidental PLL sharing across incompatible non-DP modes. Test via mode-setting on DP and non-DP connectors, fractional PLL panels, spread-spectrum changes, multi-CRTC clone setups, low/high pixel clocks, and debug KMS divider logs.
