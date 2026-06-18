<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/sirfstar.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/sirfstar.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GNSS receiver binding for SiRFstar GNSS Receiver. The SiRFstar GNSS receivers have incarnated over the years in different chips, starting from the SiRFstarIII which was a chip that was introduced in 2004 and used in a lot of dedicated GPS devices. In 2009 SiRF was acquired by CSR (Cambridge Silicon Radio) and in 2012 the CSR GPS business was acquired by Samsung, while some products remained with CSR. In 2014 CSR was acquired by Qualcomm who still sell some of the SiRF products. SiRF chips can be used over UART, I2C or SPI buses.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gnss/sirfstar.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `SiRFstar GNSS Receiver`.
- Compatible strings or compatible constants enumerated by the schema include `csr,gsd4t`, `csr,csrg05ta03-icje-r`, `fastrax,uc430`, `linx,r4`, `wi2wi,w2sg0004`, `wi2wi,w2sg0008i`, `wi2wi,w2sg0084i`.
- Top-level required properties: `compatible`, `vcc-supply`.
- `compatible`: enum `csr,gsd4t`, `csr,csrg05ta03-icje-r`, `fastrax,uc430`, `linx,r4`, `wi2wi,w2sg0004`, `wi2wi,w2sg0008i`, `wi2wi,w2sg0084i`.
- `reg`: The I2C Address, SPI chip select address. Not required on UART buses..
- `vcc-supply`: Main voltage regulator, pin names such as 3V3_IN, VCC, VDD..
- `reset-gpios`: An optional active low reset line, should be flagged with GPIO_ACTIVE_LOW.; maxItems 1.
- `sirf,onoff-gpios`: GPIO used to power on and off device, pin name ON_OFF.; maxItems 1.
- `sirf,wakeup-gpios`: GPIO used to determine device power state, pin names such as RFPWRUP, WAKEUP.; maxItems 1.
- Uses top-level `allOf` with 2 branch(es) for variant-specific validation.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates a serial or platform GNSS receiver node so the GNSS subsystem can bind transport, regulators, reset lines, and optional backup/enable controls consistently.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- The DT node records hardware wiring and optional regulator/reset/enable policy; live receiver state, fix data, and protocol state are handled by GNSS/serdev drivers.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `gnss-common.yaml#`, `/schemas/serial/serial-peripheral-props.yaml#`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `reset-gpios`.
- Integrates with provider/consumer property `vcc-supply`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gnss/sirfstar.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `csr,gsd4t`, `csr,csrg05ta03-icje-r`, `fastrax,uc430`, `linx,r4`, `wi2wi,w2sg0004`, `wi2wi,w2sg0008i`, ....
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/sirfstar.yaml -->
