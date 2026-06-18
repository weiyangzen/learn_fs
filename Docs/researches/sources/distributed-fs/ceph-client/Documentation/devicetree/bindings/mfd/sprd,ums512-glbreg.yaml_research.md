# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/sprd,ums512-glbreg.yaml

Purpose: Binding for Unisoc UMS512 global register/syscon blocks that expose miscellaneous system control registers and child simple-MFD devices.

Important schema surface and control flow: `compatible` is an ordered list ending in `syscon` and `simple-mfd`; `reg`, `#address-cells = 1`, `#size-cells = 1`, and `ranges` are required. Pattern properties permit child nodes by unit address and rely on their own schemas for specific functionality. Additional properties are closed around the syscon/simple-MFD bus contract.

State, dependencies, and integration: DT state describes a memory-mapped global register window used as a regmap-backed syscon and as a parent bus for child devices. Dependencies include syscon conventions, simple-mfd child probing, address translation via `ranges`, and child-specific schemas. Risks include using an incomplete compatible list, omitting `ranges` so child registers cannot translate, and letting unrelated register fields leak into ad hoc child nodes. Test signals are binding checks, child node schema validation, syscon regmap lookup, and runtime child device creation.
