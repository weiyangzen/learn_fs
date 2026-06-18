<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_quirks.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_quirks.h

## Purpose
`intel_quirks.h` defines the display quirk IDs and the public API for initializing and querying i915 display quirks.

## Important APIs, Types, And Functions
The key type is `enum intel_quirk_id`, with entries for backlight presence/inversion, LVDS SSC disable, increased panel/DDI delays, PPS backlight hook disable, fast-wake sync length, eDP HBR2 rate limiting, and eDP Panel Replay disable. The API consists of `intel_init_quirks()`, `intel_init_dpcd_quirks()`, `intel_has_quirk()`, and `intel_has_dpcd_quirk()`.

## Control Flow
The header itself has no flow. It lets initialization code populate quirk masks and feature code query those masks before choosing hardware behavior.

## State And Persistence Behavior
No state is defined in the header. Consumers store quirk bits in `display->quirks.mask` or `intel_dp->quirks.mask`.

## Dependencies And Integration Points
It forward-declares `intel_display`, `intel_dp`, and `drm_dp_dpcd_ident`, allowing PCI/DMI and DP probe code to share the same quirk IDs without pulling in full type definitions.

## Risks
Adding enum values changes the bit positions used in masks, so existing values should remain stable. Since masks use `BIT(quirk)`, enum growth must stay within the backing mask width.

## Test Signals
Compile coverage validates API use. Runtime signals include expected quirk bits being visible through consumers and correct behavior on affected hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_quirks.h -->
