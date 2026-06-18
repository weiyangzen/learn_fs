# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/panel-simple-lvds-dual-ports.yaml

Purpose: collects validation rules for a family of simple display panel nodes under `panel-simple-lvds-dual-ports.yaml`; the title is Simple LVDS panels with one power supply and dual LVDS ports.

Important APIs/types/functions: this is a YAML devicetree binding, so the important interfaces are schema keywords rather than executable functions. compatible selector(s): `auo,g133han01`, `auo,g156han04`, `auo,g185han01`, `auo,g190ean01`, `auo,t215hvn01`, `boe,av123z7m-n17`, and 6 more. required properties: `compatible`, `power-supply`. declared properties: `compatible`, `ports`. referenced schemas: /schemas/display/lvds-dual-ports.yaml#, panel-common shared physical/control properties, OF graph port/endpoint bindings.

Control flow: dt-schema evaluates `$id`/`$schema`, applies referenced schemas through `allOf`, validates the `compatible` choice, checks required resources, and then applies property constraints such as `maxItems`, `items`, `enum`, `const`, `patternProperties`, and strict `additionalProperties` or `unevaluatedProperties` handling. validation is mostly direct property and required-list checking. `ports` uses the OF graph multi-port model.

State and persistence behavior: Runtime state is not stored in this YAML; persistent board state is the DTS node fields such as `compatible` and graph linkage, which drivers later use for power, orientation, timing, or link setup.

Dependencies and integration points: depends on dt-schema core meta-schema; /schemas/display/lvds-dual-ports.yaml#, panel-common shared physical/control properties, OF graph port/endpoint bindings. It integrates with Linux devicetree validation, board DTS files, and the corresponding DRM panel, bridge, or display controller drivers through compatible strings and OF graph endpoints.

Risks: strict unknown-property rejection can break DTS users when a legitimate board property is omitted from the schema; driver and DTS compatibility depends on keeping the compatible list aligned with kernel panel/display driver match tables; conditional `allOf` rules must stay synchronized with SoC or panel-specific hardware differences; graph endpoint numbering and remote-endpoint links are easy to regress because they encode display pipeline topology; power/reset/backlight sequencing is not modeled procedurally here, so drivers and board DTS files must interpret these properties consistently.

Test signals: `make dt_binding_check` validates the YAML schema itself; inline examples are compiled and checked by dt-schema; downstream signal comes from DTS files using the declared compatible and graph topology; panel driver probe tests are indirect through DRM panel binding matches. Includes devicetree examples that exercise the intended node shape and are compiled by dt-schema checks.
