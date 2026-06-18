# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/devfreq/nvidia,tegra30-actmon.yaml

## Purpose
NVIDIA Tegra30 Activity Monitor is a devfreq monitor binding under the Linux kernel DeviceTree binding tree. The schema declares the YAML/JSON-schema contract for nodes matched by `nvidia,tegra30-actmon.yaml` and is consumed by dt-schema validation, DTS authors, and kernel drivers. The activity monitor block collects statistics about the behaviour of other components in the system. This information can be used to derive the rate at which the external memory needs to be clocked in order to serve all requests from the monitored clients.

## Important APIs, Types, And Schema Surface
The public API is declarative rather than callable code: `$id` `http://devicetree.org/schemas/devfreq/nvidia,tegra30-actmon.yaml#`, top-level `compatible` values `nvidia,tegra30-actmon`, `nvidia,tegra114-actmon`, `nvidia,tegra124-actmon`, `nvidia,tegra210-actmon`, required properties `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `interrupts`, `interconnects`, `interconnect-names`, `operating-points-v2`, `#cooling-cells`, and top-level properties `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`, `interrupts`, `interconnects`, `interconnect-names`, `operating-points-v2`, `#cooling-cells`.
Key property contracts include: `compatible` (declared by schema); `reg` (maxItems=1); `clocks` (maxItems=2); `clock-names` (declared by schema); `resets` (maxItems=1); `reset-names` (declared by schema); `interrupts` (maxItems=1); `#cooling-cells` (const `2`).

## Control Flow
There is no executable control flow in this file. Validation flow starts when dt-schema loads the `$id`, applies the common core meta-schema, resolves `$ref` links to shared schemas, checks `compatible` selection, enforces `required` and item-count constraints, then validates any nested child-node, graph-port, and conditional `if`/`then`/`else` rules. At runtime the kernel OF core matches the same `compatible` strings against driver tables; the driver then reads the constrained resources such as MMIO `reg`, IRQs, clocks, resets, power domains, DMA channels, PHYs, and graph endpoints.

## State And Persistence Behavior
The binding persists no runtime state. Its durable state is the hardware description ABI encoded in DTS/DTB files: compatible strings, address ranges, phandles, resource ordering, child-node names, and endpoint topology. Once a board DTB ships, these property names and fallback compatible strings must remain compatible with both the schema and existing drivers. Examples embedded in the schema are validation fixtures, not live configuration.

## Dependencies And Integration Points
Integration points include devfreq/event drivers that sample memory-controller or activity-monitor counters; driver matching through compatible strings such as `nvidia,tegra30-actmon`, `nvidia,tegra114-actmon`, `nvidia,tegra124-actmon`, `nvidia,tegra210-actmon`; provider bindings for `clocks`, `clock-names`, `resets`, `reset-names`, `interrupts`.

## Risks
- compatible fallback order is part of the ABI; reordering or dropping fallback strings can prevent the intended driver from probing older or newer SoC variants
- `additionalProperties: false` means board DTS files must not carry undocumented vendor properties
- clock count and `clock-names` order are schema-validated and must match what the driver requests
- reset-name ordering is part of the driver contract

## Test Signals
- run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/devfreq/nvidia,tegra30-actmon.yaml` from the kernel tree or equivalent dt-schema invocation
- build representative DTS files with `make dtbs_check` so board nodes are checked against this schema
- runtime signal is event/devfreq registration and nonzero activity counters under memory or device load
- schema contains 1 example block(s), which should remain valid under `dt_binding_check` after changes

## Source Notes
The source was read in full for this research pass (129 lines). Maintainers listed by the binding: `Dmitry Osipenko <digetx@gmail.com>`, `Jon Hunter <jonathanh@nvidia.com>`, `Thierry Reding <thierry.reding@gmail.com>`.
