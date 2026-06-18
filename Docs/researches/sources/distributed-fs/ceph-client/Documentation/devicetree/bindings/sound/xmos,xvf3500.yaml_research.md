<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/xmos,xvf3500.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/xmos,xvf3500.yaml

## Purpose
Devicetree binding schema for XMOS XVF3500 VocalFusion Voice Processor in the Linux ASoC sound subsystem. It documents and validates nodes matched by `usb20b1,0013`. The schema description narrows this to: The XMOS XVF3500 VocalFusion Voice Processor is a low-latency, 32-bit multicore controller for voice processing. https://www.xmos.com/xvf3500/

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `reset-gpios`, `vdd-supply`, `vddio-supply`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `/schemas/usb/usb-device.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `reset-gpios`, `vdd-supply`, `vddio-supply`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with Linux ASoC machine, codec, CPU DAI, DAI-link, clock, GPIO, regulator, and routing schemas; many fields are consumed by ASoC card or component drivers through OF matching. Referenced schemas include `/schemas/usb/usb-device.yaml#`. Maintainer metadata routes binding review to Javier Carrasco <javier.carrasco@wolfvision.net>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `reset-gpios`, `vdd-supply`, `vddio-supply`) will make example or board DTs fail validation and can prevent driver probe; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=sound/xmos,xvf3500.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/xmos,xvf3500.yaml -->
