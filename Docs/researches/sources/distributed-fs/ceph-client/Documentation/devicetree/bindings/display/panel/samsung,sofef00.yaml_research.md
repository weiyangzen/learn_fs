# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/samsung,sofef00.yaml

Purpose: validates devicetree nodes for the dedicated panel hardware described by Samsung SOFEF00 AMOLED DDIC.

Important APIs/types/functions: this is a YAML devicetree binding, so the important interfaces are schema keywords rather than executable functions. compatible selector(s): `samsung,sofef00-ams601nt22`, `samsung,sofef00-ams628nw01`, `samsung,sofef00`. required properties: `compatible`, `reset-gpios`, `poc-supply`, `vci-supply`, `vddio-supply`. declared properties: `compatible`, `reg`, `poc-supply`, `vci-supply`, `vddio-supply`. referenced schemas: panel-common shared physical/control properties.

Control flow: dt-schema evaluates `$id`/`$schema`, applies referenced schemas through `allOf`, validates the `compatible` choice, checks required resources, and then applies property constraints such as `maxItems`, `items`, `enum`, `const`, `patternProperties`, and strict `additionalProperties` or `unevaluatedProperties` handling. validation is mostly direct property and required-list checking. no graph port is central to this schema.

State and persistence behavior: Runtime state is not stored in this YAML; persistent board state is the DTS node fields such as `vddio-supply`, which drivers later use for power, orientation, timing, or link setup.

Dependencies and integration points: depends on dt-schema core meta-schema; panel-common shared physical/control properties; regulator bindings. It integrates with Linux devicetree validation, board DTS files, and the corresponding DRM panel, bridge, or display controller drivers through compatible strings and OF graph endpoints.

Risks: strict unknown-property rejection can break DTS users when a legitimate board property is omitted from the schema; driver and DTS compatibility depends on keeping the compatible list aligned with kernel panel/display driver match tables; conditional `allOf` rules must stay synchronized with SoC or panel-specific hardware differences; power/reset/backlight sequencing is not modeled procedurally here, so drivers and board DTS files must interpret these properties consistently.

Test signals: `make dt_binding_check` validates the YAML schema itself; inline examples are compiled and checked by dt-schema; downstream signal comes from DTS files using the declared compatible and graph topology; panel driver probe tests are indirect through DRM panel binding matches. Includes devicetree examples that exercise the intended node shape and are compiled by dt-schema checks.
