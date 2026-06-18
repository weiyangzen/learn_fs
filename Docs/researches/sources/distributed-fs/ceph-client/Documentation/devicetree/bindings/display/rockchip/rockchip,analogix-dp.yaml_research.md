# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/rockchip/rockchip,analogix-dp.yaml

Purpose: validates devicetree nodes for Rockchip specific extensions to the Analogix Display Port, including SoC-specific integration resources and graph links.

Important APIs/types/functions: this is a YAML devicetree binding, so the important interfaces are schema keywords rather than executable functions. compatible selector(s): `rockchip,rk3288-dp`, `rockchip,rk3399-edp`, `rockchip,rk3588-edp`. required properties: `compatible`, `clocks`, `clock-names`, `resets`, `reset-names`, `rockchip,grf`. declared properties: `compatible`, `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names`, `rockchip,grf`, `aux-bus`. referenced schemas: standard devicetree scalar/phandle type definitions, /schemas/display/dp-aux-bus.yaml#, /schemas/display/bridge/analogix,dp.yaml#.

Control flow: dt-schema evaluates `$id`/`$schema`, applies referenced schemas through `allOf`, validates the `compatible` choice, checks required resources, and then applies property constraints such as `maxItems`, `items`, `enum`, `const`, `patternProperties`, and strict `additionalProperties` or `unevaluatedProperties` handling. 1 conditional schema branches tune clocks, resets, interrupts, ports, or allowed properties by compatible. nested graph `port@N` nodes define display pipeline links.

State and persistence behavior: The schema has no mutable runtime state; it validates persistent hardware description fields `clocks`, `clock-names`, `resets`, `reset-names`, `power-domains` that platform drivers map to registers, clocks, interrupts, resets, power domains, and graph endpoints.

Dependencies and integration points: depends on dt-schema core meta-schema; standard devicetree scalar/phandle type definitions, /schemas/display/dp-aux-bus.yaml#, /schemas/display/bridge/analogix,dp.yaml#; clock provider bindings; reset-controller bindings; power-domain provider bindings. It integrates with Linux devicetree validation, board DTS files, and the corresponding DRM panel, bridge, or display controller drivers through compatible strings and OF graph endpoints.

Risks: strict unknown-property rejection can break DTS users when a legitimate board property is omitted from the schema; driver and DTS compatibility depends on keeping the compatible list aligned with kernel panel/display driver match tables; conditional `allOf` rules must stay synchronized with SoC or panel-specific hardware differences.

Test signals: `make dt_binding_check` validates the YAML schema itself; inline examples are compiled and checked by dt-schema; downstream signal comes from DTS files using the declared compatible and graph topology; DRM/KMS platform driver probe and display pipeline tests are the practical runtime signal. Includes devicetree examples that exercise the intended node shape and are compiled by dt-schema checks.
