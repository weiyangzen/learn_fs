<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/fsl,scu-rtc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/fsl,scu-rtc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/fsl,scu-rtc.yaml` is a Linux devicetree YAML schema for the `i.MX SCU Client Device Node - RTC Based on SCU Message Protocol` real-time clock binding. i.MX SCU Client Device Node Client nodes are maintained as children of the relevant IMX-SCU device node. It is not executable Ceph or kernel logic; it is a hardware-description ABI used by DTS authors, dt-schema, and Linux subsystem drivers so that board descriptions match what the driver will parse at probe or early boot.

## Important APIs, Types, and Functions
The public API surface is the schema's accepted node shape. `compatible` uses single `const` and covers 1 compatible token: `fsl,imx8qxp-sc-rtc`. Top-level properties are `compatible`. Across nested schemas and child nodes this file mentions 1 distinct property name; required properties observed at all levels include `compatible`. Node naming is constrained by no explicit node-name constraint. RTC properties declare timekeeping hardware resources: bus/register addressing {join_code(groups['addressing'], 8)}, alarm interrupts and wakeup capability none, clocks or supplies none, and RTC-specific behavior keys none. Required properties are `compatible`; the ABI drives RTC class-device registration, alarm support, and wake-from-suspend behavior.

## Control Flow, State, and Persistence
Control flow is declarative JSON-schema evaluation. `dt-doc-validate`, `dt_binding_check`, and `dtbs_check` load the YAML, expand `$ref` links, match nodes by `compatible` or referenced common-schema use, enforce required properties, evaluate composition/conditional keywords, and validate inline DTS examples. At runtime, RTC drivers bind through I2C/SPI/platform buses, register an RTC class device, program alarms, and coordinate wakeup interrupts and clock inputs. The YAML itself stores no mutable runtime state and writes no persistent data; persistence is the source-controlled devicetree ABI and the DTB blobs built from DTS. External references used in evaluation are `rtc.yaml#`; schema composition/conditional keywords present are `allOf`.

## Dependencies and Integration Points
Maintainers: Dong Aisheng <aisheng.dong@nxp.com>. Integration points include the Linux devicetree core meta-schema, any referenced common binding schemas, in-tree DTS/DTSI users under the Ceph-client kernel source, and driver `of_match_table` entries for the compatible strings. `$ref` dependencies are `rtc.yaml#`; pattern-property child-node APIs are none. The file provides 1 example block that should stay aligned with the schema and driver expectations.

## Risks
Risks are ABI and integration risks. Changing compatible ordering, required keys, resource names, child-node patterns, cell counts, or strictness can reject existing DTS files or let invalid hardware descriptions reach runtime probe. This schema has 1 top-level properties, 1 distinct property names across nested schemas, and this strictness profile: unknown top-level properties are rejected. Conditional branches and shared `$ref` schemas should be checked against all in-tree users because schema-only edits can still break board builds or driver binding.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/fsl,scu-rtc.yaml` for targeted schema and example validation, then `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/fsl,scu-rtc.yaml` against representative DTS users using `fsl,imx8qxp-sc-rtc`. The file contains 1 inline example, so example compilation should be part of the signal. Integration signals include RTC class-device registration, time read/write, alarm IRQ delivery, suspend wake tests, and bus probe coverage for required regulators, clocks, and address cells.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/fsl,scu-rtc.yaml -->
