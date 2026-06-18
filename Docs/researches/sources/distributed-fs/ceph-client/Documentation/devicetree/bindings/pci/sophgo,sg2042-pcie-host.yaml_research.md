<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/sophgo,sg2042-pcie-host.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/sophgo,sg2042-pcie-host.yaml

## Purpose
Sophgo SG2042 PCIe Host (Cadence PCIe Wrapper) is a PCI/PCIe host bridge or root-complex binding. Sophgo SG2042 PCIe host controller is based on the Cadence PCIe core. Maintainers: Chen Wang <unicorn_wang@outlook.com>.

## Important APIs, Types, and Properties
This is a YAML dt-schema document identified by `http://devicetree.org/schemas/pci/sophgo,sg2042-pcie-host.yaml#`. compatible values `sophgo,sg2042-pcie-host`. required properties `compatible`, `reg`, `reg-names`. notable properties `compatible`, `reg`, `reg-names`, `msi-parent`, `vendor-id`, `device-id`. register names `reg`, `cfg`. schema refs `cdns-pcie-host.yaml#`.

## Control Flow
There is no executable runtime control flow; validation flow is dt-schema evaluation. A DTS node is selected by `compatible`, then checked through referenced common schemas; 1 `allOf` layer(s); required properties, property cardinality, enums/consts, and examples are evaluated before the kernel driver ever probes the hardware.

## State and Persistence
The file stores no runtime state. Persistent state is the ABI contract captured in devicetree source: `reg`, `reg-names`. Once a DTB is shipped, those property names and cell layouts become firmware/kernel interface that drivers and boot firmware must preserve.

## Dependencies and Integration Points
Integrates with Linux devicetree binding validation, DTS files under architecture trees, and the matching kernel driver selected by compatible data. Referenced schemas are `cdns-pcie-host.yaml#`; property closure is closed by `unevaluatedProperties: false`.

## Risks
Primary risks are compatible drift can bind the wrong driver data, misordered register regions break MMIO window decoding. Because this is ABI documentation, tightening constraints without checking all DTS users can create false-positive validation failures, while loose constraints let broken board descriptions reach runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/sophgo,sg2042-pcie-host.yaml` and `make dtbs_check` against boards using this binding; the 1 embedded example(s) should compile through dt-schema. Also search DTS users of the listed compatible strings and verify driver probe logs, interrupts, clocks/resets, and link or PHY bring-up match the schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pci/sophgo,sg2042-pcie-host.yaml -->
