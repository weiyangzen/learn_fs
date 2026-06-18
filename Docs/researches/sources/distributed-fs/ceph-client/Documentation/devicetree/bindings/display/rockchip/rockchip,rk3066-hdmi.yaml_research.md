# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/rockchip/rockchip,rk3066-hdmi.yaml

Purpose: validates devicetree nodes for Rockchip rk3066 HDMI controller, including SoC-specific integration resources and graph links.

Important APIs/types/functions: this is a YAML devicetree binding, so the important interfaces are schema keywords rather than executable functions. compatible selector(s): `rockchip,rk3066-hdmi`. required properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `pinctrl-0`, `pinctrl-names`, `power-domains`, `rockchip,grf`, `ports`. declared properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `power-domains`, `rockchip,grf`, `#sound-dai-cells`, `ports`. referenced schemas: sound DAI common schema, standard devicetree scalar/phandle type definitions, OF graph port/endpoint bindings.

Control flow: dt-schema evaluates `$id`/`$schema`, applies referenced schemas through `allOf`, validates the `compatible` choice, checks required resources, and then applies property constraints such as `maxItems`, `items`, `enum`, `const`, `patternProperties`, and strict `additionalProperties` or `unevaluatedProperties` handling. validation is mostly direct property and required-list checking. `ports` uses the OF graph multi-port model.

State and persistence behavior: The schema has no mutable runtime state; it validates persistent hardware description fields `reg`, `clocks`, `clock-names`, `interrupts`, `power-domains`, `ports` that platform drivers map to registers, clocks, interrupts, resets, power domains, and graph endpoints.

Dependencies and integration points: depends on dt-schema core meta-schema; sound DAI common schema, standard devicetree scalar/phandle type definitions, OF graph port/endpoint bindings; clock provider bindings; power-domain provider bindings; interrupt-controller bindings. It integrates with Linux devicetree validation, board DTS files, and the corresponding DRM panel, bridge, or display controller drivers through compatible strings and OF graph endpoints.

Risks: strict unknown-property rejection can break DTS users when a legitimate board property is omitted from the schema; driver and DTS compatibility depends on keeping the compatible list aligned with kernel panel/display driver match tables; conditional `allOf` rules must stay synchronized with SoC or panel-specific hardware differences; graph endpoint numbering and remote-endpoint links are easy to regress because they encode display pipeline topology.

Test signals: `make dt_binding_check` validates the YAML schema itself; inline examples are compiled and checked by dt-schema; downstream signal comes from DTS files using the declared compatible and graph topology; DRM/KMS platform driver probe and display pipeline tests are the practical runtime signal. Includes devicetree examples that exercise the intended node shape and are compiled by dt-schema checks.
