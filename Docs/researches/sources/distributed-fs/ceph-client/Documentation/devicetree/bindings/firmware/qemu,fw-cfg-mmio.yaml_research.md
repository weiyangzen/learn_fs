<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/qemu,fw-cfg-mmio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/qemu,fw-cfg-mmio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the firmware service node for QEMU Firmware Configuration. Various QEMU emulation / virtualization targets provide the following Firmware Configuration interface on the "virt" machine type: - A write-only, 16-bit wide selector (or control) register, - a read-write, 64-bit wide data register. QEMU exposes the control and data register to guests as memory mapped registers; their location is communicated to the guest's UEFI firmware in the DTB that QEMU places at the bottom of the guest's DRAM. The authoritative guest-side hardware interface documentation to the fw_cfg.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/firmware/qemu,fw-cfg-mmio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `QEMU Firmware Configuration`.
- Compatible strings or compatible constants enumerated by the schema include `qemu,fw-cfg-mmio`.
- Top-level required properties: `compatible`, `reg`.
- `compatible`: const `qemu,fw-cfg-mmio`.
- `reg`: * Bytes 0x0 to 0x7 cover the data register. * Bytes 0x8 to 0x9 cover the selector register. * Further registers...; maxItems 1.
- `dma-coherent` is accepted as a flag/property marker.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates firmware-service discovery; runtime clients bind through firmware, mailbox, SCMI, SMC, or memory-region integration depending on the declared properties.

## State and persistence behavior
- The binding persists no state by itself; it names firmware endpoints, shared memory, clocks, resets, power domains, or secure-call channels consumed by platform drivers at boot/probe.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Firmware bindings are sensitive to ABI drift because OS drivers and secure/remote firmware must agree on mailbox, shared-memory, SMC, or SCMI protocol details.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/firmware/qemu,fw-cfg-mmio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `qemu,fw-cfg-mmio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/qemu,fw-cfg-mmio.yaml -->
