# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/panel-simple.yaml

Purpose: collects validation rules for a family of simple display panel nodes under `panel-simple.yaml`; the title is Simple panels with one power supply.

Important APIs/types/functions: this is a YAML devicetree binding, so the important interfaces are schema keywords rather than executable functions. compatible selector(s): `ampire,am-1280800n3tzqw-t00h`, `ampire,am-480272h3tmqw-t01h`, `ampire,am-800480l1tmqw-t00h`, `ampire,am800480r3tmqwa1h`, `ampire,am800600p5tmqw-tb8h`, `auo,b101aw03`, and 154 more. required properties: `compatible`, `power-supply`. declared properties: `compatible`. referenced schemas: panel-common shared physical/control properties, LVDS data-mapping schema.

Control flow: dt-schema evaluates `$id`/`$schema`, applies referenced schemas through `allOf`, validates the `compatible` choice, checks required resources, and then applies property constraints such as `maxItems`, `items`, `enum`, `const`, `patternProperties`, and strict `additionalProperties` or `unevaluatedProperties` handling. validation is mostly direct property and required-list checking. no graph port is central to this schema.

State and persistence behavior: Runtime state is not stored in this YAML; persistent board state is the DTS node fields such as `compatible` and graph linkage, which drivers later use for power, orientation, timing, or link setup.

Dependencies and integration points: depends on dt-schema core meta-schema; panel-common shared physical/control properties, LVDS data-mapping schema. It integrates with Linux devicetree validation, board DTS files, and the corresponding DRM panel, bridge, or display controller drivers through compatible strings and OF graph endpoints.

Risks: strict unknown-property rejection can break DTS users when a legitimate board property is omitted from the schema; driver and DTS compatibility depends on keeping the compatible list aligned with kernel panel/display driver match tables; conditional `allOf` rules must stay synchronized with SoC or panel-specific hardware differences; power/reset/backlight sequencing is not modeled procedurally here, so drivers and board DTS files must interpret these properties consistently.

Test signals: `make dt_binding_check` validates the YAML schema itself; inline examples are compiled and checked by dt-schema; downstream signal comes from DTS files using the declared compatible and graph topology; panel driver probe tests are indirect through DRM panel binding matches. Includes devicetree examples that exercise the intended node shape and are compiled by dt-schema checks.
