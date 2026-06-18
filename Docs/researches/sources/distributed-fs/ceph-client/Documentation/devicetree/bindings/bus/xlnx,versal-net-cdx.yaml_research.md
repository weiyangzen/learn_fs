# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/xlnx,versal-net-cdx.yaml

## Purpose
CDX bus controller for AMD devices is implemented to dynamically detect CDX bus and devices using the firmware. It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Nipun Gupta <nipun.gupta@amd.com>, Nikhil Agarwal <nikhil.agarwal@amd.com> and gives dt-schema a canonical contract for nodes matching `xlnx,versal-net-cdx`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const xlnx,versal-net-cdx), `#address-cells` (enum 1, 2), `#size-cells` (enum 1, 2), `ranges`, `iommu-map`, `msi-map`, `xlnx,rproc` (ref phandle; phandle to the remoteproc_r5 rproc node using which APU interacts with remote processor.). Required properties are `compatible`, `iommu-map`, `msi-map`, `xlnx,rproc`, `ranges`, `#address-cells`, `#size-cells`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/phandle. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/xlnx,versal-net-cdx.yaml`
- run `make dtbs_check` on DTS files using `xlnx,versal-net-cdx`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
