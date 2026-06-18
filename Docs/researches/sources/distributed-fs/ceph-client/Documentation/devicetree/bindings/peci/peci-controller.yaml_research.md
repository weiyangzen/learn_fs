<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/peci/peci-controller.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/peci/peci-controller.yaml

## Purpose
Generic for PECI is a PECI controller/common binding. PECI (Platform Environment Control Interface) is an interface that provides a communication channel from Intel processors and chipset components to external monitoring or control devices. Maintainers: Iwona Winiarska <iwona.winiarska@intel.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/peci/peci-controller.yaml#`. required properties none declared. notable properties `$nodename`, `cmd-timeout-ms`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through a direct property/required-list schema; required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: compatible strings and node topology. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are none beyond core dt-schema behavior; property closure is open for inherited/vendor properties.

## Risks
Primary risks are schema/property drift can allow invalid DTS nodes or reject existing boards. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/peci/peci-controller.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/peci/peci-controller.yaml -->
