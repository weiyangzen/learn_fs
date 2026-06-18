# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/novatek,nt36523.yaml

Purpose: validates devicetree nodes for the dedicated panel hardware described by Novatek NT36523 based DSI display Panels.

Important APIs/types/functions: this is a YAML devicetree binding, so the important interfaces are schema keywords rather than executable functions. compatible selector(s): `xiaomi,elish-boe-nt36523`, `xiaomi,elish-csot-nt36523`, `novatek,nt36523`, `lenovo,j606f-boe-nt36523w`, `novatek,nt36523w`. required properties: `compatible`, `reg`, `vddio-supply`, `reset-gpios`, `port@1`. declared properties: `compatible`, `reg`, `reset-gpios`, `vddio-supply`. referenced schemas: panel-common shared physical/control properties.

Control flow: dt-schema evaluates `$id`/`$schema`, applies referenced schemas through `allOf`, validates the `compatible` choice, checks required resources, and then applies property constraints such as `maxItems`, `items`, `enum`, `const`, `patternProperties`, and strict `additionalProperties` or `unevaluatedProperties` handling. 1 conditional schema branches tune clocks, resets, interrupts, ports, or allowed properties by compatible. nested graph `port@N` nodes define display pipeline links.

State and persistence behavior: Runtime state is not stored in this YAML; persistent board state is the DTS node fields such as `vddio-supply`, `reset-gpios`, which drivers later use for power, orientation, timing, or link setup.

Dependencies and integration points: depends on dt-schema core meta-schema; panel-common shared physical/control properties; regulator bindings; GPIO controller bindings. It integrates with Linux devicetree validation, board DTS files, and the corresponding DRM panel, bridge, or display controller drivers through compatible strings and OF graph endpoints.

Risks: strict unknown-property rejection can break DTS users when a legitimate board property is omitted from the schema; driver and DTS compatibility depends on keeping the compatible list aligned with kernel panel/display driver match tables; conditional `allOf` rules must stay synchronized with SoC or panel-specific hardware differences; power/reset/backlight sequencing is not modeled procedurally here, so drivers and board DTS files must interpret these properties consistently.

Test signals: `make dt_binding_check` validates the YAML schema itself; inline examples are compiled and checked by dt-schema; downstream signal comes from DTS files using the declared compatible and graph topology; panel driver probe tests are indirect through DRM panel binding matches. Includes devicetree examples that exercise the intended node shape and are compiled by dt-schema checks.
