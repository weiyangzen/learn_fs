# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/panel-common.yaml

Purpose: defines reusable devicetree schema properties for display panel bindings rather than a standalone hardware node: Common Properties for Display Panels.

Important APIs/types/functions: this is a YAML devicetree binding, so the important interfaces are schema keywords rather than executable functions. declared properties: `width-mm`, `height-mm`, `label`, `rotation`, `flip-horizontal`, `flip-vertical`, `panel-timing`, `display-timings`, `port`, `ddc-i2c-bus`, `no-hpd`, `hpd-gpios`, `enable-gpios`, `reset-gpios`, `te-gpios`, `power-supply`, plus 1 more. referenced schemas: standard devicetree scalar/phandle type definitions, display timing schemas, OF graph port/endpoint bindings.

Control flow: dt-schema evaluates `$id`/`$schema`, applies referenced schemas through `allOf`, validates the `compatible` choice, checks required resources, and then applies property constraints such as `maxItems`, `items`, `enum`, `const`, `patternProperties`, and strict `additionalProperties` or `unevaluatedProperties` handling. validation is mostly direct property and required-list checking. `port` uses a single OF graph endpoint.

State and persistence behavior: Runtime state is not stored in this YAML; persistent board state is the DTS node fields such as `power-supply`, `enable-gpios`, `reset-gpios`, `te-gpios`, `backlight`, `ddc-i2c-bus`, `width-mm`, `height-mm`, `rotation`, which drivers later use for power, orientation, timing, or link setup.

Dependencies and integration points: depends on dt-schema core meta-schema; standard devicetree scalar/phandle type definitions, display timing schemas, OF graph port/endpoint bindings; backlight provider bindings; regulator bindings; GPIO controller bindings. It integrates with Linux devicetree validation, board DTS files, and the corresponding DRM panel, bridge, or display controller drivers through compatible strings and OF graph endpoints.

Risks: permissive additional properties can allow misspelled board properties to pass validation; graph endpoint numbering and remote-endpoint links are easy to regress because they encode display pipeline topology; power/reset/backlight sequencing is not modeled procedurally here, so drivers and board DTS files must interpret these properties consistently.

Test signals: `make dt_binding_check` validates the YAML schema itself; downstream signal comes from DTS files using the declared compatible and graph topology; panel driver probe tests are indirect through DRM panel binding matches. No inline example is present, so validation relies on schema review and DTS users.
