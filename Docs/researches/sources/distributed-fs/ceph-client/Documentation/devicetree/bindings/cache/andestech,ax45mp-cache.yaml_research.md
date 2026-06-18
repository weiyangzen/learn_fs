# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/andestech,ax45mp-cache.yaml

## Purpose
A level-2 cache (L2C) is used to improve the system performance by providing a large amount of cache line entries and reasonable access delays. It is a cache-controller binding used for cache-controller description for CPU/system cache drivers and cache hierarchy validation. The binding is maintained by Lad Prabhakar <prabhakar.mahadev-lad.rj@bp.renesas.com> and gives dt-schema a canonical contract for nodes matching `andestech,qilai-ax45mp-cache`, `renesas,r9a07g043f-ax45mp-cache`, `andestech,ax45mp-cache`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `interrupts` (items ?..1), `cache-line-size` (const 64), `cache-level` (const 2), `cache-sets` (enum 1024, 2048), `cache-size` (enum 131072, 262144, 524288, 1048576...), `cache-unified`, `next-level-cache`. Required properties are `compatible`, `reg`, `interrupts`, `cache-line-size`, `cache-level`, `cache-sets`, `cache-size`, `cache-unified`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s), 1 conditional `if` branch(es). Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/interrupt-controller/irq.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=cache/andestech,ax45mp-cache.yaml`
- run `make dtbs_check` on DTS files using `andestech,qilai-ax45mp-cache`, `renesas,r9a07g043f-ax45mp-cache`, `andestech,ax45mp-cache`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
