<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/ibm,p9-sbefifo.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/ibm,p9-sbefifo.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FSI bus/controller/peripheral binding for IBM FSI-attached SBEFIFO engine. The SBEFIFO is an FSI CFAM engine that provides an interface to the POWER processor Self Boot Engine (SBE). This node will always be a child of an FSI CFAM node.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fsi/ibm,p9-sbefifo.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `IBM FSI-attached SBEFIFO engine`.
- Compatible strings or compatible constants enumerated by the schema include `ibm,p9-sbefifo`, `ibm,odyssey-sbefifo`.
- Top-level required properties: `compatible`, `reg`.
- `compatible`: enum `ibm,p9-sbefifo`, `ibm,odyssey-sbefifo`.
- `reg`: 1 ordered items.
- `occ`: ref `ibm,p9-occ.yaml#`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the FSI topology visible to service processors; runtime probing follows FSI master/controller discovery into child engines such as SBEFIFO, SCOM, OCC, or SPI bridges.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent topology is represented by DT child nodes and addressing cells; mutable FSI engine state remains in bus and device drivers.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `ibm,p9-occ.yaml#`.
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fsi/ibm,p9-sbefifo.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `ibm,p9-sbefifo`, `ibm,odyssey-sbefifo`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/ibm,p9-sbefifo.yaml -->
