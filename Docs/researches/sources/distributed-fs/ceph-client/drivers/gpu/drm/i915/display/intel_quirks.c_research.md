<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_quirks.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_quirks.c

## Purpose
`intel_quirks.c` applies platform, subsystem, DMI, and sink-DPCD-specific display quirks for known machines and panels. Quirks compensate for incorrect firmware tables, board-specific electrical needs, panel bugs, or feature incompatibilities.

## Important APIs, Types, And Functions
The exported functions are `intel_init_quirks()`, `intel_init_dpcd_quirks()`, `intel_has_quirk()`, and `intel_has_dpcd_quirk()`. Internal data structures are `struct intel_quirk` for PCI device/subsystem matches, `struct intel_dpcd_quirk` for PCI plus sink OUI/device ID matches, and `struct intel_dmi_quirk` for DMI match tables. Hook functions set bits in `display->quirks.mask` or `intel_dp->quirks.mask`.

## Control Flow
At display initialization, `intel_init_quirks()` iterates `intel_quirks[]` and applies hooks whose PCI device, subsystem vendor, and subsystem device match, then evaluates DMI tables. During DP probe, `intel_init_dpcd_quirks()` additionally matches the current PCI IDs and DP sink identity before applying DPCD-scoped hooks. Query helpers test the bitmasks.

## State And Persistence Behavior
Applied quirks persist in bitmasks attached to `struct intel_display` or `struct intel_dp` for the device lifetime. They are not stored to disk. DPCD quirks are per-DP object and depend on sink identity observed during probe.

## Dependencies And Integration Points
The file uses Linux DMI matching, PCI IDs via `to_pci_dev()`, DRM logging, and i915 display/DP types. Quirk consumers include backlight setup, LVDS SSC/refclock paths, panel power sequencing, eDP link-rate limiting, fast-wake programming, and Panel Replay gating.

## Risks
Quirk matching is deliberately specific, but false positives can disable features or change electrical/timing behavior on unrelated systems. False negatives leave known-bad hardware paths active. DPCD sink-device matching treats an all-zero sink device ID in the table as wildcard, so additions must choose OUI/device matching carefully. Hook logging is useful but can become noisy if a broad match is added.

## Test Signals
Signals include boot logs showing expected quirk application, DMI/PCI matching tests on affected machines, panel/backlight behavior, eDP link-rate selection, PSR/Panel Replay availability on quirked sinks, and regression checks on systems sharing subsystem IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_quirks.c -->
