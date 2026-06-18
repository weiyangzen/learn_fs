<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/peci/peci-aspeed.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/peci/peci-aspeed.yaml

## Purpose
Aspeed PECI Bus is a PECI controller/common binding. The file documents the allowed devicetree node shape for this hardware block. Maintainers: Iwona Winiarska <iwona.winiarska@intel.com>, Jae Hyun Yoo <jae.hyun.yoo@linux.intel.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/peci/peci-aspeed.yaml#`. compatible values `aspeed,ast2400-peci`, `aspeed,ast2500-peci`, `aspeed,ast2600-peci`. required properties `compatible`, `reg`, `interrupts`, `clocks`, `resets`. notable properties `compatible`, `reg`, `interrupts`, `clocks`, `resets`, `cmd-timeout-ms`, `clock-frequency`. schema refs `peci-controller.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `clocks`, `resets`, `interrupts`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `peci-controller.yaml#`; property closure is closed by `additionalProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/peci/peci-aspeed.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/peci/peci-aspeed.yaml -->
