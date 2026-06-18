# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/panel-common-dual.yaml

Purpose: defines reusable devicetree schema properties for display panel bindings rather than a standalone hardware node: Common Properties for Dual-Link Display Panels.

Important APIs/types/functions: this is a YAML devicetree binding, so the important interfaces are schema keywords rather than executable functions. declared properties: `ports`. referenced schemas: panel-common shared physical/control properties, OF graph port/endpoint bindings.

Control flow: dt-schema evaluates `$id`/`$schema`, applies referenced schemas through `allOf`, validates the `compatible` choice, checks required resources, and then applies property constraints such as `maxItems`, `items`, `enum`, `const`, `patternProperties`, and strict `additionalProperties` or `unevaluatedProperties` handling. selection branches constrain alternative compatible/property combinations. `ports` uses the OF graph multi-port model.

State and persistence behavior: The schema persists no runtime state; it describes board-authored panel metadata that dt-schema validates before the kernel consumes it.

Dependencies and integration points: depends on dt-schema core meta-schema; panel-common shared physical/control properties, OF graph port/endpoint bindings. It integrates with Linux devicetree validation, board DTS files, and the corresponding DRM panel, bridge, or display controller drivers through compatible strings and OF graph endpoints.

Risks: strict unknown-property rejection can break DTS users when a legitimate board property is omitted from the schema; conditional `allOf` rules must stay synchronized with SoC or panel-specific hardware differences; graph endpoint numbering and remote-endpoint links are easy to regress because they encode display pipeline topology; power/reset/backlight sequencing is not modeled procedurally here, so drivers and board DTS files must interpret these properties consistently.

Test signals: `make dt_binding_check` validates the YAML schema itself; downstream signal comes from DTS files using the declared compatible and graph topology; panel driver probe tests are indirect through DRM panel binding matches. No inline example is present, so validation relies on schema review and DTS users.
