<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/xilinx/xlnx,zynqmp-firmware.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/xilinx/xlnx,zynqmp-firmware.yaml

## Purpose
This YAML binding defines the Device Tree contract for the firmware service node for Xilinx firmware driver. The zynqmp-firmware node describes the interface to platform firmware. ZynqMP has an interface to communicate with secure firmware. Firmware driver provides an interface to firmware APIs. Interface APIs can be used by any driver to communicate to PMUFW(Platform Management Unit). These requests include clock management, pin control, device control, power management service, FPGA service and other platform management services.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/firmware/xilinx/xlnx,zynqmp-firmware.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Xilinx firmware driver`.
- Compatible strings or compatible constants enumerated by the schema include `xlnx,zynqmp-firmware`, `xlnx,versal-firmware`, `xlnx,versal-net-firmware`.
- Top-level required properties: `compatible`.
- `compatible`: constraints via oneOf.
- `method`: The method of calling the PM-API firmware layer. Permitted values are. - "smc" : SMC #0, following the SMCCC -...; enum `smc`, `hvc`; ref `/schemas/types.yaml#/definitions/string-array`.
- `#power-domain-cells`: const `1`.
- `clock-controller`: The clock controller is a hardware block of Xilinx versal clock tree. It reads required input clock frequencies...; ref `/schemas/clock/xlnx,versal-clk.yaml#`.
- `gpio`: The gpio node describes connect to PS_MODE pins via firmware interface.; ref `/schemas/gpio/xlnx,zynqmp-gpio-modepin.yaml#`.
- `soc-nvmem`: The ZynqMP MPSoC provides access to the hardware related data like SOC revision, IDCODE and specific purpose...; ref `/schemas/nvmem/xlnx,zynqmp-nvmem.yaml#`.
- `pcap`: The ZynqMP SoC uses the PCAP (Processor Configuration Port) to configure the Programmable Logic (PL). The...; ref `/schemas/fpga/xlnx,zynqmp-pcap-fpga.yaml`.
- `pinctrl`: The pinctrl node provides access to pinconfig and pincontrol functionality available in firmware..
- `power-management`: The zynqmp-power node describes the power management configurations. It will control remote suspend/shutdown...; ref `/schemas/power/reset/xlnx,zynqmp-power.yaml#`.
- `reset-controller`: The reset-controller node describes connection to the reset functionality via firmware interface.; ref `/schemas/reset/xlnx,zynqmp-reset.yaml#`.
- `versal-fpga`: Compatible of the FPGA device.; ref `/schemas/fpga/xlnx,versal-fpga.yaml#`.
- `zynqmp-aes`: The ZynqMP AES-GCM hardened cryptographic accelerator is used to encrypt or decrypt the data with provided key and...; ref `/schemas/crypto/xlnx,zynqmp-aes.yaml#`.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.
- Nested conditional keywords present: `else`, `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates firmware-service discovery; runtime clients bind through firmware, mailbox, SCMI, SMC, or memory-region integration depending on the declared properties.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- The binding persists no state by itself; it names firmware endpoints, shared memory, clocks, resets, power domains, or secure-call channels consumed by platform drivers at boot/probe.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/string-array`, `/schemas/clock/xlnx,versal-clk.yaml#`, `/schemas/gpio/xlnx,zynqmp-gpio-modepin.yaml#`, `/schemas/nvmem/xlnx,zynqmp-nvmem.yaml#`, `/schemas/fpga/xlnx,zynqmp-pcap-fpga.yaml`, `/schemas/power/reset/xlnx,zynqmp-power.yaml#`, `/schemas/reset/xlnx,zynqmp-reset.yaml#`, `/schemas/fpga/xlnx,versal-fpga.yaml#`, ....
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Firmware bindings are sensitive to ABI drift because OS drivers and secure/remote firmware must agree on mailbox, shared-memory, SMC, or SCMI protocol details.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/firmware/xilinx/xlnx,zynqmp-firmware.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `xlnx,zynqmp-firmware`, `xlnx,versal-firmware`, `xlnx,versal-net-firmware`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/xilinx/xlnx,zynqmp-firmware.yaml -->
