# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_snps_hdmi_pll.h

## Purpose
`intel_snps_hdmi_pll.h` declares the public Synopsys HDMI PLL calculators used by i915 display PHY code.

## Important APIs, Types, And Functions
- Forward declarations: `struct intel_c10pll_state` and `struct intel_mpllb_state`.
- `intel_snps_hdmi_pll_compute_mpllb(struct intel_mpllb_state *pll_state, u64 pixel_clock)` calculates DG2/SNPS MPLLB state for an HDMI pixel clock.
- `intel_snps_hdmi_pll_compute_c10pll(struct intel_c10pll_state *pll_state, u64 pixel_clock)` calculates C10 PLL state for an HDMI pixel clock.

## Control Flow
The header has no runtime control flow. It provides a narrow interface so callers can compute PLL state without depending on the internal curve tables and helper math in the C file.

## State And Persistence
The header owns no state. Its functions write into caller-owned state structures.

## Dependencies And Integration Points
It depends on Linux integer types. It is included by `intel_snps_hdmi_pll.c` and by PHY code that needs HDMI PLL fallback or C10 PLL programming.

## Risks And Edge Cases
The API does not return a status code, so callers assume the supplied pixel clock is in range and that the calculator can always produce a usable state. Any future validation failure would require an API shape change or a sentinel in the output state.

## Test Signals
Build coverage should ensure both callers see complete declarations. Runtime correctness is validated through the C file's golden PLL-state tests and HDMI modeset PLL-lock behavior.
