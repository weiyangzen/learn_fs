# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/panel-timing.yaml

Purpose: defines the reusable timing subnode schema used by fixed-mode panel bindings: panel timing.

Important APIs/types/functions: this is a YAML devicetree binding, so the important interfaces are schema keywords rather than executable functions. required properties: `clock-frequency`, `hactive`, `vactive`, `hfront-porch`, `hback-porch`, `hsync-len`, `vfront-porch`, `vback-porch`, `vsync-len`. declared properties: `clock-frequency`, `hactive`, `vactive`, `hfront-porch`, `hback-porch`, `hsync-len`, `vfront-porch`, `vback-porch`, `vsync-len`, `hsync-active`, `vsync-active`, `de-active`, `pixelclk-active`, `syncclk-active`, `interlaced`, `doublescan`, plus 1 more. referenced schemas: standard devicetree scalar/phandle type definitions.

Control flow: dt-schema evaluates `$id`/`$schema`, applies referenced schemas through `allOf`, validates the `compatible` choice, checks required resources, and then applies property constraints such as `maxItems`, `items`, `enum`, `const`, `patternProperties`, and strict `additionalProperties` or `unevaluatedProperties` handling. selection branches constrain alternative compatible/property combinations. no graph port is central to this schema.

State and persistence behavior: The schema persists no runtime state; it describes board-authored panel metadata that dt-schema validates before the kernel consumes it.

Dependencies and integration points: depends on dt-schema core meta-schema; standard devicetree scalar/phandle type definitions. It integrates with Linux devicetree validation, board DTS files, and the corresponding DRM panel, bridge, or display controller drivers through compatible strings and OF graph endpoints.

Risks: strict unknown-property rejection can break DTS users when a legitimate board property is omitted from the schema.

Test signals: `make dt_binding_check` validates the YAML schema itself; downstream signal comes from DTS files using the declared compatible and graph topology; panel driver probe tests are indirect through DRM panel binding matches. No inline example is present, so validation relies on schema review and DTS users.
