# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/samsung/samsung,exynos-hdmi-ddc.yaml

Purpose: validates devicetree nodes for Samsung Exynos SoC HDMI DDC, including SoC-specific integration resources and graph links.

Important APIs/types/functions: this is a YAML devicetree binding, so the important interfaces are schema keywords rather than executable functions. compatible selector(s): `samsung,exynos4210-hdmiddc`, `samsung,exynos5-hdmiddc`. required properties: `compatible`, `reg`. declared properties: `compatible`, `reg`.

Control flow: dt-schema evaluates `$id`/`$schema`, applies referenced schemas through `allOf`, validates the `compatible` choice, checks required resources, and then applies property constraints such as `maxItems`, `items`, `enum`, `const`, `patternProperties`, and strict `additionalProperties` or `unevaluatedProperties` handling. selection branches constrain alternative compatible/property combinations. no graph port is central to this schema.

State and persistence behavior: The schema has no mutable runtime state; it validates persistent hardware description fields `reg` that platform drivers map to registers, clocks, interrupts, resets, power domains, and graph endpoints.

Dependencies and integration points: depends on dt-schema core meta-schema. It integrates with Linux devicetree validation, board DTS files, and the corresponding DRM panel, bridge, or display controller drivers through compatible strings and OF graph endpoints.

Risks: strict unknown-property rejection can break DTS users when a legitimate board property is omitted from the schema; driver and DTS compatibility depends on keeping the compatible list aligned with kernel panel/display driver match tables.

Test signals: `make dt_binding_check` validates the YAML schema itself; inline examples are compiled and checked by dt-schema; downstream signal comes from DTS files using the declared compatible and graph topology; DRM/KMS platform driver probe and display pipeline tests are the practical runtime signal. Includes devicetree examples that exercise the intended node shape and are compiled by dt-schema checks.
