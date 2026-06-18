<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rng/microchip,pic32-rng.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rng/microchip,pic32-rng.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rng/microchip,pic32-rng.yaml` is a Linux devicetree YAML schema for the `Microchip PIC32 Random Number Generator` hardware random-number generator binding. The PIC32 RNG provides a pseudo random number generator which can be seeded by another true random number generator. It is not executable Ceph or kernel logic; it is a hardware-description ABI used by DTS authors, dt-schema, and Linux subsystem drivers so that board descriptions match what the driver will parse at probe or early boot.

## Important APIs, Types, and Functions
The public API surface is the schema's accepted node shape. `compatible` uses `enum` list and covers 1 compatible token: `microchip,pic32mzda-rng`. Top-level properties are `compatible`, `reg`, `clocks`. Across nested schemas and child nodes this file mentions 3 distinct property names; required properties observed at all levels include `clocks`, `compatible`, `reg`. Node naming is constrained by no explicit node-name constraint. RNG properties declare entropy-provider resources: register ranges {join_code(groups['addressing'], 8)}, clock/reset/power controls `clocks`, interrupts none, and RNG tuning keys `reg`, `clocks`. Required properties are `compatible`, `reg`, `clocks`; runtime consumers are hwrng/crypto drivers that turn these resources into entropy devices.

## Control Flow, State, and Persistence
Control flow is declarative JSON-schema evaluation. `dt-doc-validate`, `dt_binding_check`, and `dtbs_check` load the YAML, expand `$ref` links, match nodes by `compatible` or referenced common-schema use, enforce required properties, evaluate composition/conditional keywords, and validate inline DTS examples. At runtime, hwrng or crypto drivers bind to the node, map registers, enable clocks or resets, and feed entropy to the kernel random subsystem. The YAML itself stores no mutable runtime state and writes no persistent data; persistence is the source-controlled devicetree ABI and the DTB blobs built from DTS. External references used in evaluation are none; schema composition/conditional keywords present are none.

## Dependencies and Integration Points
Maintainers: Joshua Henderson <joshua.henderson@microchip.com>. Integration points include the Linux devicetree core meta-schema, any referenced common binding schemas, in-tree DTS/DTSI users under the Ceph-client kernel source, and driver `of_match_table` entries for the compatible strings. `$ref` dependencies are none; pattern-property child-node APIs are none. The file provides 1 example block that should stay aligned with the schema and driver expectations.

## Risks
Risks are ABI and integration risks. Changing compatible ordering, required keys, resource names, child-node patterns, cell counts, or strictness can reject existing DTS files or let invalid hardware descriptions reach runtime probe. This schema has 3 top-level properties, 3 distinct property names across nested schemas, and this strictness profile: unknown top-level properties are rejected. Conditional branches and shared `$ref` schemas should be checked against all in-tree users because schema-only edits can still break board builds or driver binding.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rng/microchip,pic32-rng.yaml` for targeted schema and example validation, then `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rng/microchip,pic32-rng.yaml` against representative DTS users using `microchip,pic32mzda-rng`. The file contains 1 inline example, so example compilation should be part of the signal. Integration signals include hwrng device registration, entropy reads through `/dev/hwrng` or kernel hwrng tests, clock/reset enablement, and absence of probe-time register/IRQ failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rng/microchip,pic32-rng.yaml -->
