<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soundwire/soundwire-controller.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soundwire/soundwire-controller.yaml

## Purpose
Devicetree binding schema fragment for SoundWire Controller Common Properties in the Linux SoundWire subsystem. It documents reusable node properties rather than a single top-level compatible. The schema description narrows this to: SoundWire busses can be described with a node for the SoundWire controller device and a set of child nodes for each SoundWire slave on the bus.

## Important APIs/types/functions
- Schema property keys observed: `$nodename`, `#address-cells`, `#size-cells`, `compatible`, `reg`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: `^.*@[0-9a-f],[0-9a-f]$`.
- External schema APIs: none declared.

## Control flow
The schema control flow is declarative: validation starts at the top-level property map; then enforces required keys `#address-cells`, `#size-cells`; pattern-matched child/property blocks include `^.*@[0-9a-f],[0-9a-f]$`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `#address-cells`, `#size-cells`, `compatible`, `reg`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SoundWire bus schema and Qualcomm or generic SoundWire controller drivers; child peripherals rely on SoundWire addressing and interrupt/clock/reset resources described here. Maintainer metadata routes binding review to Srinivas Kandagatla <srinivas.kandagatla@linaro.org>, Vinod Koul <vkoul@kernel.org>.

## Risks and edge cases
missing required properties (`#address-cells`, `#size-cells`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=soundwire/soundwire-controller.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soundwire/soundwire-controller.yaml -->
