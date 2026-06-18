# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/powertip,st7272.yaml

Purpose: validates devicetree nodes for the dedicated panel hardware described by Powertip Electronic Technology Co. 320 x 240 LCD panel.

Important APIs/types/functions: this is a YAML devicetree binding, so the important interfaces are schema keywords rather than executable functions. compatible selector(s): `powertip,st7272`. declared properties: `compatible`, `height-mm`, `panel-timing`, `port`, `power-supply`, `width-mm`. referenced schemas: panel-dpi.yaml#.

Control flow: dt-schema evaluates `$id`/`$schema`, applies referenced schemas through `allOf`, validates the `compatible` choice, checks required resources, and then applies property constraints such as `maxItems`, `items`, `enum`, `const`, `patternProperties`, and strict `additionalProperties` or `unevaluatedProperties` handling. validation is mostly direct property and required-list checking. `port` uses a single OF graph endpoint.

State and persistence behavior: Runtime state is not stored in this YAML; persistent board state is the DTS node fields such as `power-supply`, `width-mm`, `height-mm`, which drivers later use for power, orientation, timing, or link setup.

Dependencies and integration points: depends on dt-schema core meta-schema; panel-dpi.yaml#; regulator bindings. It integrates with Linux devicetree validation, board DTS files, and the corresponding DRM panel, bridge, or display controller drivers through compatible strings and OF graph endpoints.

Risks: strict unknown-property rejection can break DTS users when a legitimate board property is omitted from the schema; driver and DTS compatibility depends on keeping the compatible list aligned with kernel panel/display driver match tables; conditional `allOf` rules must stay synchronized with SoC or panel-specific hardware differences; graph endpoint numbering and remote-endpoint links are easy to regress because they encode display pipeline topology; power/reset/backlight sequencing is not modeled procedurally here, so drivers and board DTS files must interpret these properties consistently.

Test signals: `make dt_binding_check` validates the YAML schema itself; downstream signal comes from DTS files using the declared compatible and graph topology; panel driver probe tests are indirect through DRM panel binding matches. No inline example is present, so validation relies on schema review and DTS users.
