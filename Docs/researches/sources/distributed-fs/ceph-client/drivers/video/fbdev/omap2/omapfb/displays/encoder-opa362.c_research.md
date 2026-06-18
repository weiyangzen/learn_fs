# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/encoder-opa362.c

## Purpose
`encoder-opa362.c` models the OPA362 analog video amplifier as an OMAP DSS ATV output. It forwards analog TV operations to an upstream VENC source and controls an optional enable GPIO.

## Important APIs, Types, And Functions
- `struct panel_drv_data` stores the output DSS device, upstream source, optional enable GPIO, and timings.
- `opa362_atv_ops` implements ATV connect/disconnect, enable/disable, timing operations, and type selection.
- `opa362_set_type()` warns unless the requested VENC type is composite.

## Control Flow
Probe requires OF, requests optional `enable` GPIO default-low, finds the upstream source, fills `dssdev` with ATV ops and VENC output type, and registers it as an output. Connect forwards to upstream ATV connect and links `dst->src`/`dssdev->dst`. Enable sets timings, enables upstream ATV, asserts enable GPIO, and marks active. Disable clears GPIO, disables upstream, and marks disabled. Remove unregisters output, warns and tears down if still enabled/connected, and drops the source reference.

## State And Persistence
Connection pointers, state, timing copy, and GPIO value are runtime-only.

## Dependencies And Integration Points
The file depends on OF graph source lookup, GPIO descriptors, and OMAP DSS ATV output registration.

## Risks
The output only supports composite semantics but cannot enforce all downstream type uses beyond a warning. Removal handles enabled/connected states defensively but relies on correct `dst` pointers. Missing optional GPIO means power control is entirely upstream/external.

## Test Signals
Enable should produce upstream VENC output plus asserted OPA362 enable GPIO. Composite connector chains should connect/disconnect without stale `src`/`dst` links.
