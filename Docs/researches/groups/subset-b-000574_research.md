# subset-b-000574 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/nvidia,tegra186-bpmp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/nvidia,tegra186-bpmp.yaml

## Purpose
This YAML binding defines the Device Tree contract for the firmware service node for NVIDIA Tegra Boot and Power Management Processor (BPMP). The BPMP is a specific processor in Tegra chip, which is designed for booting process handling and offloading the power management, clock management, and reset control tasks from the CPU. The binding document defines the resources that would be used by the BPMP firmware driver, which can create the interprocessor communication (IPC) between the CPU and BPMP. This node is a mailbox consumer. See the following files for details of the mailbox subsystem, and the specifiers implemented by the relevant provider(s): -.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/firmware/nvidia,tegra186-bpmp.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `NVIDIA Tegra Boot and Power Management Processor (BPMP)`.
- Compatible strings or compatible constants enumerated by the schema include `nvidia,tegra194-bpmp`, `nvidia,tegra234-bpmp`, `nvidia,tegra264-bpmp`, `nvidia,tegra186-bpmp`.
- Top-level required properties: `compatible`, `mboxes`, `#clock-cells`, `#power-domain-cells`, `#reset-cells`.
- `compatible`: constraints via oneOf.
- `mboxes`: A phandle and channel specifier for the mailbox used to communicate with the BPMP.; maxItems 1.
- `shmem`: List of the phandle to the TX and RX shared memory area that the IPC between CPU and BPMP is based on.; maxItems 2; minItems 2.
- `memory-region`: phandle to reserved memory region used for IPC between CPU-NS and BPMP.; maxItems 1.
- `#clock-cells`: const `1`.
- `#power-domain-cells`: const `1`.
- `#reset-cells`: const `1`.
- `interconnects`: 4 ordered items.
- `interconnect-names`: 4 ordered items.
- `iommus`: maxItems 1.
- `i2c`: generic schema entry.
- `thermal`: generic schema entry.
- Uses top-level `oneOf` with 2 branch(es) for variant-specific validation.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates firmware-service discovery; runtime clients bind through firmware, mailbox, SCMI, SMC, or memory-region integration depending on the declared properties.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- The binding persists no state by itself; it names firmware endpoints, shared memory, clocks, resets, power domains, or secure-call channels consumed by platform drivers at boot/probe.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `mboxes`.
- Integrates with provider/consumer property `shmem`.
- Integrates with provider/consumer property `memory-region`.
- Integrates with provider/consumer property `iommus`.
- Includes 2 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Firmware bindings are sensitive to ABI drift because OS drivers and secure/remote firmware must agree on mailbox, shared-memory, SMC, or SCMI protocol details.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/firmware/nvidia,tegra186-bpmp.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `nvidia,tegra194-bpmp`, `nvidia,tegra234-bpmp`, `nvidia,tegra264-bpmp`, `nvidia,tegra186-bpmp`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/nvidia,tegra186-bpmp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/nxp,imx95-scmi-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/nxp,imx95-scmi-pinctrl.yaml

## Purpose
This YAML binding defines the Device Tree contract for the firmware service node for i.MX System Control and Management Interface (SCMI) Pinctrl Protocol. i.MX System Control and Management Interface (SCMI) Pinctrl Protocol

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/firmware/nxp,imx95-scmi-pinctrl.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `i.MX System Control and Management Interface (SCMI) Pinctrl Protocol`.
- No top-level `required` list is declared; requirements are delegated to referenced schemas, branch logic, or child schemas.
- Pattern child/property schemas: `grp$`.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates firmware-service discovery; runtime clients bind through firmware, mailbox, SCMI, SMC, or memory-region integration depending on the declared properties.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- The binding persists no state by itself; it names firmware endpoints, shared memory, clocks, resets, power domains, or secure-call channels consumed by platform drivers at boot/probe.
- `additionalProperties` is `True`, so the node is open for extra properties or delegated schemas.

## Dependencies and integration points
- References shared schemas: `/schemas/pinctrl/pinctrl.yaml`, `/schemas/types.yaml#/definitions/uint32-matrix`.

## Risks and edge cases
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Firmware bindings are sensitive to ABI drift because OS drivers and secure/remote firmware must agree on mailbox, shared-memory, SMC, or SCMI protocol details.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/firmware/nxp,imx95-scmi-pinctrl.yaml` plus `make dtbs_check` on boards using the compatible strings.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/nxp,imx95-scmi-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/nxp,imx95-scmi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/nxp,imx95-scmi.yaml

## Purpose
This YAML binding defines the Device Tree contract for the firmware service node for i.MX95 System Control and Management Interface(SCMI) Vendor Protocols Extension. i.MX95 System Control and Management Interface(SCMI) Vendor Protocols Extension

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/firmware/nxp,imx95-scmi.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `i.MX95 System Control and Management Interface(SCMI) Vendor Protocols Extension`.
- No top-level `required` list is declared; requirements are delegated to referenced schemas, branch logic, or child schemas.
- `protocol@80`: SCMI LMM protocol which is for boot, shutdown, and reset of other logical machines (LM). It is usually used to...; ref `/schemas/firmware/arm,scmi.yaml#/$defs/protocol-node`.
- `protocol@81`: constraints via allOf, additionalProperties, properties.
- `protocol@82`: SCMI CPU Protocol which allows an agent to start or stop a CPU. It is used to manage auxiliary CPUs in a LM.; ref `/schemas/firmware/arm,scmi.yaml#/$defs/protocol-node`.
- `protocol@84`: ref `/schemas/firmware/arm,scmi.yaml#/$defs/protocol-node`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates firmware-service discovery; runtime clients bind through firmware, mailbox, SCMI, SMC, or memory-region integration depending on the declared properties.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- The binding persists no state by itself; it names firmware endpoints, shared memory, clocks, resets, power domains, or secure-call channels consumed by platform drivers at boot/probe.
- `additionalProperties` is `True`, so the node is open for extra properties or delegated schemas.

## Dependencies and integration points
- References shared schemas: `/schemas/firmware/arm,scmi.yaml#/$defs/protocol-node`, `/schemas/input/input.yaml#`, `/schemas/types.yaml#/definitions/uint32-matrix`.

## Risks and edge cases
- Firmware bindings are sensitive to ABI drift because OS drivers and secure/remote firmware must agree on mailbox, shared-memory, SMC, or SCMI protocol details.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/firmware/nxp,imx95-scmi.yaml` plus `make dtbs_check` on boards using the compatible strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/nxp,imx95-scmi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/qcom,scm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/qcom,scm.yaml

## Purpose
This YAML binding defines the Device Tree contract for the firmware service node for QCOM Secure Channel Manager (SCM). Qualcomm processors include an interface to communicate to the secure firmware. This interface allows for clients to request different types of actions. These can include CPU power up/down, HDCP requests, loading of firmware, and other assorted actions.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/firmware/qcom,scm.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `QCOM Secure Channel Manager (SCM)`.
- Compatible strings or compatible constants enumerated by the schema include `qcom,scm-apq8064`, `qcom,scm-apq8084`, `qcom,scm-eliza`, `qcom,scm-glymur`, `qcom,scm-ipq4019`, `qcom,scm-ipq5018`, `qcom,scm-ipq5210`, `qcom,scm-ipq5332`, `qcom,scm-ipq5424`, `qcom,scm-ipq6018`, `qcom,scm-ipq806x`, `qcom,scm-ipq8074`, ....
- Top-level required properties: `compatible`.
- `compatible`: 2 ordered items.
- `clocks`: maxItems 3; minItems 1.
- `clock-names`: maxItems 3; minItems 1.
- `dma-coherent` is accepted as a flag/property marker.
- `interconnects`: maxItems 1.
- `interconnect-names`: maxItems 1.
- `#reset-cells`: const `1`.
- `interrupts`: The wait-queue interrupt that firmware raises as part of handshake protocol to handle sleeping SCM calls.; maxItems 1.
- `memory-region`: Phandle to the memory region reserved for the shared memory bridge to TZ.; maxItems 1.
- `qcom,sdi-enabled`: Indicates that the SDI (Secure Debug Image) has been enabled by TZ by default and it needs to be disabled. If not....
- `qcom,dload-mode`: TCSR hardware block; 1 ordered items; ref `/schemas/types.yaml#/definitions/phandle-array`.
- Uses top-level `allOf` with 5 branch(es) for variant-specific validation.
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
- References shared schemas: `/schemas/types.yaml#/definitions/phandle-array`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `clock-names`.
- Integrates with provider/consumer property `memory-region`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Large compatible matrices make fallback ordering and per-device exception branches easy to regress when adding variants.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Firmware bindings are sensitive to ABI drift because OS drivers and secure/remote firmware must agree on mailbox, shared-memory, SMC, or SCMI protocol details.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/firmware/qcom,scm.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `qcom,scm-apq8064`, `qcom,scm-apq8084`, `qcom,scm-eliza`, `qcom,scm-glymur`, `qcom,scm-ipq4019`, `qcom,scm-ipq5018`, ....
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/qcom,scm.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/thead,th1520-aon.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/thead,th1520-aon.yaml

## Purpose
This YAML binding defines the Device Tree contract for the firmware service node for T-HEAD TH1520 AON (Always-On) Firmware. The Always-On (AON) subsystem in the TH1520 SoC is responsible for managing low-power states, system wakeup events, and power management tasks. It is designed to operate independently in a dedicated power domain, allowing it to remain functional even during the SoC's deep sleep states. At the heart of the AON subsystem is the E902, a low-power core that executes firmware responsible for coordinating tasks such as power domain control, clock management, and system wakeup signaling. Communication between the main.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/firmware/thead,th1520-aon.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `T-HEAD TH1520 AON (Always-On) Firmware`.
- Compatible strings or compatible constants enumerated by the schema include `thead,th1520-aon`.
- Top-level required properties: `compatible`, `mboxes`, `mbox-names`, `#power-domain-cells`.
- `compatible`: const `thead,th1520-aon`.
- `mboxes`: maxItems 1.
- `mbox-names`: 1 ordered items.
- `resets`: maxItems 1.
- `reset-names`: 1 ordered items.
- `#power-domain-cells`: const `1`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates firmware-service discovery; runtime clients bind through firmware, mailbox, SCMI, SMC, or memory-region integration depending on the declared properties.

## State and persistence behavior
- The binding persists no state by itself; it names firmware endpoints, shared memory, clocks, resets, power domains, or secure-call channels consumed by platform drivers at boot/probe.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `resets`.
- Integrates with provider/consumer property `mboxes`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Firmware bindings are sensitive to ABI drift because OS drivers and secure/remote firmware must agree on mailbox, shared-memory, SMC, or SCMI protocol details.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/firmware/thead,th1520-aon.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `thead,th1520-aon`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/firmware/thead,th1520-aon.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/altr,fpga-passive-serial.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/altr,fpga-passive-serial.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FPGA manager, bridge, or region binding for Altera Passive Serial SPI FPGA Manager. Altera FPGAs support a method of loading the bitstream over what is referred to as "passive serial". The passive serial link is not technically SPI, and might require extra circuits in order to play nicely with other SPI slaves on the same bus. See https://www.altera.com/literature/hb/cyc/cyc_c51013.pdf

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fpga/altr,fpga-passive-serial.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Altera Passive Serial SPI FPGA Manager`.
- Compatible strings or compatible constants enumerated by the schema include `altr,fpga-passive-serial`, `altr,fpga-arria10-passive-serial`.
- Top-level required properties: `compatible`, `reg`, `nconfig-gpios`, `nstat-gpios`.
- `compatible`: enum `altr,fpga-passive-serial`, `altr,fpga-arria10-passive-serial`.
- `spi-max-frequency`: constraints via maximum.
- `reg`: maxItems 1.
- `nconfig-gpios`: Config pin (referred to as nCONFIG in the manual).; maxItems 1.
- `nstat-gpios`: Status pin (referred to as nSTATUS in the manual).; maxItems 1.
- `confd-gpios`: confd pin (referred to as CONF_DONE in the manual); maxItems 1.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the DT contract used by the FPGA manager framework: manager nodes program bitstreams, bridge nodes gate traffic, and region nodes sequence overlays and child device population.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- The file itself is declarative and persistent only as checked-in binding metadata; live state is the programmed FPGA image, bridge enablement, and overlay-applied child nodes described by the DT.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/spi/spi-peripheral-props.yaml#`.
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- FPGA reconfiguration ordering is sensitive: bad bridge, region, or manager references can permit bus traffic during programming or leave child devices inconsistent with the loaded image.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fpga/altr,fpga-passive-serial.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `altr,fpga-passive-serial`, `altr,fpga-arria10-passive-serial`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/altr,fpga-passive-serial.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/altr,freeze-bridge-controller.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/altr,freeze-bridge-controller.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FPGA manager, bridge, or region binding for Altera Freeze Bridge Controller. The Altera Freeze Bridge Controller manages one or more freeze bridges. The controller can freeze/disable the bridges which prevents signal changes from passing through the bridge. The controller can also unfreeze/enable the bridges which allows traffic to pass through the bridge normally.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fpga/altr,freeze-bridge-controller.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Altera Freeze Bridge Controller`.
- Compatible strings or compatible constants enumerated by the schema include `altr,freeze-bridge-controller`.
- Top-level required properties: `compatible`, `reg`.
- `compatible`: const `altr,freeze-bridge-controller`.
- `reg`: maxItems 1.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the DT contract used by the FPGA manager framework: manager nodes program bitstreams, bridge nodes gate traffic, and region nodes sequence overlays and child device population.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- The file itself is declarative and persistent only as checked-in binding metadata; live state is the programmed FPGA image, bridge enablement, and overlay-applied child nodes described by the DT.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `fpga-bridge.yaml#`.
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- FPGA reconfiguration ordering is sensitive: bad bridge, region, or manager references can permit bus traffic during programming or leave child devices inconsistent with the loaded image.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fpga/altr,freeze-bridge-controller.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `altr,freeze-bridge-controller`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/altr,freeze-bridge-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/altr,socfpga-fpga2sdram-bridge.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/altr,socfpga-fpga2sdram-bridge.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FPGA manager, bridge, or region binding for Altera FPGA To SDRAM Bridge. Altera FPGA To SDRAM Bridge

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fpga/altr,socfpga-fpga2sdram-bridge.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Altera FPGA To SDRAM Bridge`.
- Compatible strings or compatible constants enumerated by the schema include `altr,socfpga-fpga2sdram-bridge`.
- Top-level required properties: `compatible`.
- `compatible`: const `altr,socfpga-fpga2sdram-bridge`.
- `reg`: maxItems 1.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the DT contract used by the FPGA manager framework: manager nodes program bitstreams, bridge nodes gate traffic, and region nodes sequence overlays and child device population.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- The file itself is declarative and persistent only as checked-in binding metadata; live state is the programmed FPGA image, bridge enablement, and overlay-applied child nodes described by the DT.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `fpga-bridge.yaml#`.
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- FPGA reconfiguration ordering is sensitive: bad bridge, region, or manager references can permit bus traffic during programming or leave child devices inconsistent with the loaded image.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fpga/altr,socfpga-fpga2sdram-bridge.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `altr,socfpga-fpga2sdram-bridge`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/altr,socfpga-fpga2sdram-bridge.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/altr,socfpga-hps2fpga-bridge.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/altr,socfpga-hps2fpga-bridge.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FPGA manager, bridge, or region binding for Altera FPGA/HPS Bridge. Altera FPGA/HPS Bridge

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fpga/altr,socfpga-hps2fpga-bridge.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Altera FPGA/HPS Bridge`.
- Compatible strings or compatible constants enumerated by the schema include `altr,socfpga-lwhps2fpga-bridge`, `altr,socfpga-hps2fpga-bridge`, `altr,socfpga-fpga2hps-bridge`.
- Top-level required properties: `compatible`, `reg`, `clocks`, `resets`.
- `compatible`: enum `altr,socfpga-lwhps2fpga-bridge`, `altr,socfpga-hps2fpga-bridge`, `altr,socfpga-fpga2hps-bridge`.
- `reg`: maxItems 1.
- `resets`: maxItems 1.
- `clocks`: maxItems 1.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the DT contract used by the FPGA manager framework: manager nodes program bitstreams, bridge nodes gate traffic, and region nodes sequence overlays and child device population.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- The file itself is declarative and persistent only as checked-in binding metadata; live state is the programmed FPGA image, bridge enablement, and overlay-applied child nodes described by the DT.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `fpga-bridge.yaml#`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `resets`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- FPGA reconfiguration ordering is sensitive: bad bridge, region, or manager references can permit bus traffic during programming or leave child devices inconsistent with the loaded image.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fpga/altr,socfpga-hps2fpga-bridge.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `altr,socfpga-lwhps2fpga-bridge`, `altr,socfpga-hps2fpga-bridge`, `altr,socfpga-fpga2hps-bridge`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/altr,socfpga-hps2fpga-bridge.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/fpga-bridge.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/fpga-bridge.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FPGA manager, bridge, or region binding for FPGA Bridge. FPGA Bridge

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fpga/fpga-bridge.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `FPGA Bridge`.
- No top-level `required` list is declared; requirements are delegated to referenced schemas, branch logic, or child schemas.
- `$nodename`: pattern `^fpga-bridge(@.*|-([0-9]|[1-9][0-9]+))?$`.
- `bridge-enable`: 0 if driver should disable bridge at startup 1 if driver should enable bridge at startup Default is to leave...; enum `0`, `1`; ref `/schemas/types.yaml#/definitions/uint32`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the DT contract used by the FPGA manager framework: manager nodes program bitstreams, bridge nodes gate traffic, and region nodes sequence overlays and child device population.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- The file itself is declarative and persistent only as checked-in binding metadata; live state is the programmed FPGA image, bridge enablement, and overlay-applied child nodes described by the DT.
- `additionalProperties` is `True`, so the node is open for extra properties or delegated schemas.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- FPGA reconfiguration ordering is sensitive: bad bridge, region, or manager references can permit bus traffic during programming or leave child devices inconsistent with the loaded image.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fpga/fpga-bridge.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/fpga-bridge.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/fpga-region.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/fpga-region.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FPGA manager, bridge, or region binding for FPGA Region. CONTENTS - Introduction - Terminology - Sequence - FPGA Region - Supported Use Models - Constraints Introduction ============ FPGA Regions represent FPGA's and partial reconfiguration regions of FPGA's in the Device Tree. FPGA Regions provide a way to program FPGAs under device tree control. The documentation hits some of the high points of FPGA usage and attempts to include terminology used by both major FPGA manufacturers. This document isn't a replacement for any manufacturers specifications for FPGA usage..

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fpga/fpga-region.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `FPGA Region`.
- Top-level required properties: `compatible`, `fpga-mgr`.
- `$nodename`: pattern `^fpga-region(@.*|-([0-9]|[1-9][0-9]+))?$`.
- `compatible`: const `fpga-region`.
- `reg`: maxItems 1.
- `ranges` is accepted as a flag/property marker.
- `#address-cells` is accepted as a flag/property marker.
- `#size-cells` is accepted as a flag/property marker.
- `config-complete-timeout-us`: The maximum time in microseconds time for the FPGA to go to operating mode after the region has been programmed..
- `encrypted-fpga-config`: Set if the bitstream is encrypted..
- `external-fpga-config`: Set if the FPGA has already been configured prior to OS boot up..
- `firmware-name`: Should contain the name of an FPGA image file located on the firmware search path. If this property shows up in a...; maxItems 1.
- `fpga-bridges`: Should contain a list of phandles to FPGA Bridges that must be controlled during FPGA programming along with the...; ref `/schemas/types.yaml#/definitions/phandle-array`.
- `fpga-mgr`: Should contain a phandle to an FPGA Manager. Child FPGA Regions inherit this property from their ancestor regions....; ref `/schemas/types.yaml#/definitions/phandle`.
- `partial-fpga-config`: Set if partial reconfiguration is to be done, otherwise full reconfiguration is done..
- `region-freeze-timeout-us`: The maximum time in microseconds to wait for bridges to successfully become disabled before the region has been....
- `region-unfreeze-timeout-us`: The maximum time in microseconds to wait for bridges to successfully become enabled after the region has been....

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the DT contract used by the FPGA manager framework: manager nodes program bitstreams, bridge nodes gate traffic, and region nodes sequence overlays and child device population.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- The file itself is declarative and persistent only as checked-in binding metadata; live state is the programmed FPGA image, bridge enablement, and overlay-applied child nodes described by the DT.
- `additionalProperties` is `{'type': 'object'}`, so the node is open for extra properties or delegated schemas.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/phandle`.
- Integrates with provider/consumer property `reg`.
- Includes 2 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- FPGA reconfiguration ordering is sensitive: bad bridge, region, or manager references can permit bus traffic during programming or leave child devices inconsistent with the loaded image.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fpga/fpga-region.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/fpga-region.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/intel,stratix10-soc-fpga-mgr.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/intel,stratix10-soc-fpga-mgr.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FPGA manager, bridge, or region binding for Intel Stratix10 SoC FPGA Manager. The Intel Stratix10 SoC consists of a 64-bit quad-core ARM Cortex A53 hard processor system (HPS) and a Secure Device Manager (SDM). The Stratix10 SoC FPGA Manager driver is used to configure/reconfigure the FPGA fabric on the die.The driver communicates with SDM/ATF via the stratix10-svc platform driver for performing its operations.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fpga/intel,stratix10-soc-fpga-mgr.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Intel Stratix10 SoC FPGA Manager`.
- Compatible strings or compatible constants enumerated by the schema include `intel,stratix10-soc-fpga-mgr`, `intel,agilex-soc-fpga-mgr`.
- Top-level required properties: `compatible`.
- `compatible`: enum `intel,stratix10-soc-fpga-mgr`, `intel,agilex-soc-fpga-mgr`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the DT contract used by the FPGA manager framework: manager nodes program bitstreams, bridge nodes gate traffic, and region nodes sequence overlays and child device population.

## State and persistence behavior
- The file itself is declarative and persistent only as checked-in binding metadata; live state is the programmed FPGA image, bridge enablement, and overlay-applied child nodes described by the DT.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- FPGA reconfiguration ordering is sensitive: bad bridge, region, or manager references can permit bus traffic during programming or leave child devices inconsistent with the loaded image.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fpga/intel,stratix10-soc-fpga-mgr.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `intel,stratix10-soc-fpga-mgr`, `intel,agilex-soc-fpga-mgr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/intel,stratix10-soc-fpga-mgr.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/lattice,ice40-fpga-mgr.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/lattice,ice40-fpga-mgr.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FPGA manager, bridge, or region binding for Lattice iCE40 FPGA Manager. Lattice iCE40 FPGA Manager

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fpga/lattice,ice40-fpga-mgr.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Lattice iCE40 FPGA Manager`.
- Compatible strings or compatible constants enumerated by the schema include `lattice,ice40-fpga-mgr`.
- Top-level required properties: `compatible`, `reg`, `spi-max-frequency`, `cdone-gpios`, `reset-gpios`.
- `compatible`: const `lattice,ice40-fpga-mgr`.
- `reg`: maxItems 1.
- `spi-max-frequency`: constraints via minimum, maximum.
- `cdone-gpios`: GPIO input connected to CDONE pin; maxItems 1.
- `reset-gpios`: Active-low GPIO output connected to CRESET_B pin. Note that unless the GPIO is held low during startup, the FPGA...; maxItems 1.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the DT contract used by the FPGA manager framework: manager nodes program bitstreams, bridge nodes gate traffic, and region nodes sequence overlays and child device population.

## State and persistence behavior
- The file itself is declarative and persistent only as checked-in binding metadata; live state is the programmed FPGA image, bridge enablement, and overlay-applied child nodes described by the DT.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `reset-gpios`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- FPGA reconfiguration ordering is sensitive: bad bridge, region, or manager references can permit bus traffic during programming or leave child devices inconsistent with the loaded image.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fpga/lattice,ice40-fpga-mgr.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `lattice,ice40-fpga-mgr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/lattice,ice40-fpga-mgr.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/lattice,sysconfig.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/lattice,sysconfig.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FPGA manager, bridge, or region binding for Lattice Slave SPI sysCONFIG FPGA manager. Lattice sysCONFIG port, which is used for FPGA configuration, among others, have Slave Serial Peripheral Interface. Only full reconfiguration is supported. Programming of ECP5 is done by writing uncompressed bitstream image in .bit format into FPGA's SRAM configuration memory.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fpga/lattice,sysconfig.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Lattice Slave SPI sysCONFIG FPGA manager`.
- Compatible strings or compatible constants enumerated by the schema include `lattice,sysconfig-ecp5`.
- Top-level required properties: `compatible`, `reg`.
- `compatible`: enum `lattice,sysconfig-ecp5`.
- `reg`: maxItems 1.
- `program-gpios`: A GPIO line connected to PROGRAMN (active low) pin of the device. Initiates configuration sequence.; maxItems 1.
- `init-gpios`: A GPIO line connected to INITN (active low) pin of the device. Indicates that the FPGA is ready to be configured.; maxItems 1.
- `done-gpios`: A GPIO line connected to DONE (active high) pin of the device. Indicates that the configuration sequence is...; maxItems 1.
- Uses top-level `allOf` with 2 branch(es) for variant-specific validation.
- Nested conditional keywords present: `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the DT contract used by the FPGA manager framework: manager nodes program bitstreams, bridge nodes gate traffic, and region nodes sequence overlays and child device population.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- The file itself is declarative and persistent only as checked-in binding metadata; live state is the programmed FPGA image, bridge enablement, and overlay-applied child nodes described by the DT.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `/schemas/spi/spi-peripheral-props.yaml`.
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- FPGA reconfiguration ordering is sensitive: bad bridge, region, or manager references can permit bus traffic during programming or leave child devices inconsistent with the loaded image.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fpga/lattice,sysconfig.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `lattice,sysconfig-ecp5`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/lattice,sysconfig.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/microchip,mpf-spi-fpga-mgr.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/microchip,mpf-spi-fpga-mgr.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FPGA manager, bridge, or region binding for Microchip Polarfire FPGA manager.. Device Tree Bindings for Microchip Polarfire FPGA Manager using slave SPI to load the bitstream in .dat format.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fpga/microchip,mpf-spi-fpga-mgr.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Microchip Polarfire FPGA manager.`.
- Compatible strings or compatible constants enumerated by the schema include `microchip,mpf-spi-fpga-mgr`.
- Top-level required properties: `compatible`, `reg`.
- `compatible`: enum `microchip,mpf-spi-fpga-mgr`.
- `reg`: SPI chip select; maxItems 1.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the DT contract used by the FPGA manager framework: manager nodes program bitstreams, bridge nodes gate traffic, and region nodes sequence overlays and child device population.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- The file itself is declarative and persistent only as checked-in binding metadata; live state is the programmed FPGA image, bridge enablement, and overlay-applied child nodes described by the DT.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `/schemas/spi/spi-peripheral-props.yaml#`.
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- FPGA reconfiguration ordering is sensitive: bad bridge, region, or manager references can permit bus traffic during programming or leave child devices inconsistent with the loaded image.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fpga/microchip,mpf-spi-fpga-mgr.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `microchip,mpf-spi-fpga-mgr`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/microchip,mpf-spi-fpga-mgr.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/xilinx-zynq-fpga-mgr.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/xilinx-zynq-fpga-mgr.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FPGA manager, bridge, or region binding for Xilinx Zynq FPGA Manager. Xilinx Zynq FPGA Manager

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fpga/xilinx-zynq-fpga-mgr.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Xilinx Zynq FPGA Manager`.
- Compatible strings or compatible constants enumerated by the schema include `xlnx,zynq-devcfg-1.0`.
- Top-level required properties: `compatible`, `reg`, `clocks`, `clock-names`, `syscon`.
- `compatible`: const `xlnx,zynq-devcfg-1.0`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `clocks`: maxItems 1.
- `clock-names`: 1 ordered items.
- `syscon`: Phandle to syscon block which provide access to SLCR registers; ref `/schemas/types.yaml#/definitions/phandle`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the DT contract used by the FPGA manager framework: manager nodes program bitstreams, bridge nodes gate traffic, and region nodes sequence overlays and child device population.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- The file itself is declarative and persistent only as checked-in binding metadata; live state is the programmed FPGA image, bridge enablement, and overlay-applied child nodes described by the DT.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/phandle`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `clock-names`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- FPGA reconfiguration ordering is sensitive: bad bridge, region, or manager references can permit bus traffic during programming or leave child devices inconsistent with the loaded image.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fpga/xilinx-zynq-fpga-mgr.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `xlnx,zynq-devcfg-1.0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/xilinx-zynq-fpga-mgr.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/xlnx,fpga-selectmap.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/xlnx,fpga-selectmap.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FPGA manager, bridge, or region binding for Xilinx SelectMAP FPGA interface. Xilinx 7 Series FPGAs support a method of loading the bitstream over a parallel port named the SelectMAP interface in the documentation. Only the x8 mode is supported where data is loaded at one byte per rising edge of the clock, with the MSB of each byte presented to the D0 pin. Datasheets: https://www.xilinx.com/support/documentation/user_guides/ug470_7Series_Config.pdf

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fpga/xlnx,fpga-selectmap.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Xilinx SelectMAP FPGA interface`.
- Compatible strings or compatible constants enumerated by the schema include `xlnx,fpga-xc7s-selectmap`, `xlnx,fpga-xc7a-selectmap`, `xlnx,fpga-xc7k-selectmap`, `xlnx,fpga-xc7v-selectmap`.
- Top-level required properties: `compatible`, `reg`, `prog-gpios`, `done-gpios`, `init-gpios`.
- `compatible`: enum `xlnx,fpga-xc7s-selectmap`, `xlnx,fpga-xc7a-selectmap`, `xlnx,fpga-xc7k-selectmap`, `xlnx,fpga-xc7v-selectmap`.
- `reg`: At least 1 byte of memory mapped IO; maxItems 1.
- `prog-gpios`: config pin (referred to as PROGRAM_B in the manual); maxItems 1.
- `done-gpios`: config status pin (referred to as DONE in the manual); maxItems 1.
- `init-gpios`: initialization status and configuration error pin (referred to as INIT_B in the manual); maxItems 1.
- `csi-gpios`: chip select pin (referred to as CSI_B in the manual) Optional gpio for if the bus controller does not provide a...; maxItems 1.
- `rdwr-gpios`: read/write select pin (referred to as RDWR_B in the manual) Optional gpio for if the bus controller does not...; maxItems 1.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the DT contract used by the FPGA manager framework: manager nodes program bitstreams, bridge nodes gate traffic, and region nodes sequence overlays and child device population.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- The file itself is declarative and persistent only as checked-in binding metadata; live state is the programmed FPGA image, bridge enablement, and overlay-applied child nodes described by the DT.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `/schemas/memory-controllers/mc-peripheral-props.yaml#`.
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- FPGA reconfiguration ordering is sensitive: bad bridge, region, or manager references can permit bus traffic during programming or leave child devices inconsistent with the loaded image.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fpga/xlnx,fpga-selectmap.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `xlnx,fpga-xc7s-selectmap`, `xlnx,fpga-xc7a-selectmap`, `xlnx,fpga-xc7k-selectmap`, `xlnx,fpga-xc7v-selectmap`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/xlnx,fpga-selectmap.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/xlnx,fpga-slave-serial.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/xlnx,fpga-slave-serial.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FPGA manager, bridge, or region binding for Xilinx Slave Serial SPI FPGA. Xilinx Spartan-6 and 7 Series FPGAs support a method of loading the bitstream over what is referred to as slave serial interface.The slave serial link is not technically SPI, and might require extra circuits in order to play nicely with other SPI slaves on the same bus. Datasheets: https://www.xilinx.com/support/documentation/user_guides/ug380.pdf https://www.xilinx.com/support/documentation/user_guides/ug470_7Series_Config.pdf.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fpga/xlnx,fpga-slave-serial.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Xilinx Slave Serial SPI FPGA`.
- Compatible strings or compatible constants enumerated by the schema include `xlnx,fpga-slave-serial`.
- Top-level required properties: `compatible`, `reg`, `prog_b-gpios`, `done-gpios`, `init-b-gpios`.
- `compatible`: enum `xlnx,fpga-slave-serial`.
- `spi-cpha` is accepted as a flag/property marker.
- `spi-max-frequency`: constraints via maximum.
- `reg`: maxItems 1.
- `prog_b-gpios`: config pin (referred to as PROGRAM_B in the manual); maxItems 1.
- `done-gpios`: config status pin (referred to as DONE in the manual); maxItems 1.
- `init-b-gpios`: initialization status and configuration error pin (referred to as INIT_B in the manual); maxItems 1.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the DT contract used by the FPGA manager framework: manager nodes program bitstreams, bridge nodes gate traffic, and region nodes sequence overlays and child device population.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- The file itself is declarative and persistent only as checked-in binding metadata; live state is the programmed FPGA image, bridge enablement, and overlay-applied child nodes described by the DT.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/spi/spi-peripheral-props.yaml#`.
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- FPGA reconfiguration ordering is sensitive: bad bridge, region, or manager references can permit bus traffic during programming or leave child devices inconsistent with the loaded image.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fpga/xlnx,fpga-slave-serial.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `xlnx,fpga-slave-serial`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/xlnx,fpga-slave-serial.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/xlnx,pr-decoupler.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/xlnx,pr-decoupler.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FPGA manager, bridge, or region binding for Xilinx LogiCORE Partial Reconfig Decoupler/AXI shutdown manager Softcore. The Xilinx LogiCORE Partial Reconfig(PR) Decoupler manages one or more decouplers/fpga bridges. The controller can decouple/disable the bridges which prevents signal changes from passing through the bridge. The controller can also couple / enable the bridges which allows traffic to pass through the bridge normally. Xilinx LogiCORE Dynamic Function eXchange(DFX) AXI shutdown manager Softcore is compatible with the Xilinx LogiCORE pr-decoupler. The Dynamic Function eXchange AXI shutdown manager prevents AXI traffic.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fpga/xlnx,pr-decoupler.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Xilinx LogiCORE Partial Reconfig Decoupler/AXI shutdown manager Softcore`.
- Compatible strings or compatible constants enumerated by the schema include `xlnx,pr-decoupler-1.00`, `xlnx,pr-decoupler`, `xlnx,dfx-axi-shutdown-manager-1.00`, `xlnx,dfx-axi-shutdown-manager`.
- Top-level required properties: `compatible`, `reg`, `clocks`, `clock-names`.
- `compatible`: constraints via oneOf.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `clock-names`: 1 ordered items.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the DT contract used by the FPGA manager framework: manager nodes program bitstreams, bridge nodes gate traffic, and region nodes sequence overlays and child device population.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- The file itself is declarative and persistent only as checked-in binding metadata; live state is the programmed FPGA image, bridge enablement, and overlay-applied child nodes described by the DT.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `fpga-bridge.yaml#`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `clock-names`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- FPGA reconfiguration ordering is sensitive: bad bridge, region, or manager references can permit bus traffic during programming or leave child devices inconsistent with the loaded image.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fpga/xlnx,pr-decoupler.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `xlnx,pr-decoupler-1.00`, `xlnx,pr-decoupler`, `xlnx,dfx-axi-shutdown-manager-1.00`, `xlnx,dfx-axi-shutdown-manager`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/xlnx,pr-decoupler.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/xlnx,versal-fpga.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/xlnx,versal-fpga.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FPGA manager, bridge, or region binding for Xilinx Versal FPGA driver.. Device Tree Versal FPGA bindings for the Versal SoC, controlled using firmware interface.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fpga/xlnx,versal-fpga.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Xilinx Versal FPGA driver.`.
- Compatible strings or compatible constants enumerated by the schema include `xlnx,versal-fpga`.
- Top-level required properties: `compatible`.
- `compatible`: 1 ordered items.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the DT contract used by the FPGA manager framework: manager nodes program bitstreams, bridge nodes gate traffic, and region nodes sequence overlays and child device population.

## State and persistence behavior
- The file itself is declarative and persistent only as checked-in binding metadata; live state is the programmed FPGA image, bridge enablement, and overlay-applied child nodes described by the DT.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- FPGA reconfiguration ordering is sensitive: bad bridge, region, or manager references can permit bus traffic during programming or leave child devices inconsistent with the loaded image.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fpga/xlnx,versal-fpga.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `xlnx,versal-fpga`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/xlnx,versal-fpga.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/xlnx,zynqmp-pcap-fpga.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/xlnx,zynqmp-pcap-fpga.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FPGA manager, bridge, or region binding for Xilinx Zynq Ultrascale MPSoC FPGA Manager. Device Tree Bindings for Zynq Ultrascale MPSoC FPGA Manager. The ZynqMP SoC uses the PCAP (Processor Configuration Port) to configure the Programmable Logic (PL). The configuration uses the firmware interface.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fpga/xlnx,zynqmp-pcap-fpga.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Xilinx Zynq Ultrascale MPSoC FPGA Manager`.
- Compatible strings or compatible constants enumerated by the schema include `xlnx,zynqmp-pcap-fpga`.
- Top-level required properties: `compatible`.
- `compatible`: const `xlnx,zynqmp-pcap-fpga`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the DT contract used by the FPGA manager framework: manager nodes program bitstreams, bridge nodes gate traffic, and region nodes sequence overlays and child device population.

## State and persistence behavior
- The file itself is declarative and persistent only as checked-in binding metadata; live state is the programmed FPGA image, bridge enablement, and overlay-applied child nodes described by the DT.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- FPGA reconfiguration ordering is sensitive: bad bridge, region, or manager references can permit bus traffic during programming or leave child devices inconsistent with the loaded image.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fpga/xlnx,zynqmp-pcap-fpga.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `xlnx,zynqmp-pcap-fpga`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fpga/xlnx,zynqmp-pcap-fpga.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/aspeed,ast2400-cf-fsi-master.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/aspeed,ast2400-cf-fsi-master.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FSI bus/controller/peripheral binding for ASpeed ColdFire offloaded GPIO-based FSI master. ASpeed ColdFire offloaded GPIO-based FSI master

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fsi/aspeed,ast2400-cf-fsi-master.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `ASpeed ColdFire offloaded GPIO-based FSI master`.
- Compatible strings or compatible constants enumerated by the schema include `aspeed,ast2400-cf-fsi-master`, `aspeed,ast2500-cf-fsi-master`.
- Top-level required properties: `compatible`, `clock-gpios`, `data-gpios`, `enable-gpios`, `trans-gpios`, `mux-gpios`, `memory-region`, `aspeed,cvic`, `aspeed,sram`.
- `compatible`: enum `aspeed,ast2400-cf-fsi-master`, `aspeed,ast2500-cf-fsi-master`.
- `clock-gpios`: GPIO for FSI clock; maxItems 1.
- `data-gpios`: GPIO for FSI data signal; maxItems 1.
- `enable-gpios`: GPIO for enable signal; maxItems 1.
- `trans-gpios`: GPIO for voltage translator enable; maxItems 1.
- `mux-gpios`: GPIO for pin multiplexing with other functions (eg, external FSI masters); maxItems 1.
- `memory-region`: Reference to the reserved memory for the ColdFire. Must be 2M aligned on AST2400 and 1M aligned on AST2500.; maxItems 1.
- `aspeed,cvic`: Reference to the CVIC node.; ref `/schemas/types.yaml#/definitions/phandle`.
- `aspeed,sram`: Reference to the SRAM node.; ref `/schemas/types.yaml#/definitions/phandle`.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the FSI topology visible to service processors; runtime probing follows FSI master/controller discovery into child engines such as SBEFIFO, SCOM, OCC, or SPI bridges.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent topology is represented by DT child nodes and addressing cells; mutable FSI engine state remains in bus and device drivers.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `/schemas/fsi/fsi-controller.yaml#`, `/schemas/types.yaml#/definitions/phandle`.
- Integrates with provider/consumer property `memory-region`.
- Integrates with provider/consumer property `enable-gpios`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fsi/aspeed,ast2400-cf-fsi-master.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `aspeed,ast2400-cf-fsi-master`, `aspeed,ast2500-cf-fsi-master`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/aspeed,ast2400-cf-fsi-master.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/aspeed,ast2600-fsi-master.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/aspeed,ast2600-fsi-master.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FSI bus/controller/peripheral binding for Aspeed FSI master. The AST2600 and later contain two identical FSI masters. They share a clock and have a separate interrupt line and output pins.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fsi/aspeed,ast2600-fsi-master.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Aspeed FSI master`.
- Compatible strings or compatible constants enumerated by the schema include `aspeed,ast2600-fsi-master`, `aspeed,ast2700-fsi-master`.
- Top-level required properties: `compatible`, `reg`, `clocks`, `interrupts`.
- `compatible`: enum `aspeed,ast2600-fsi-master`, `aspeed,ast2700-fsi-master`.
- `clocks`: maxItems 1.
- `cfam-reset-gpios`: Output GPIO pin for CFAM reset; maxItems 1.
- `fsi-routing-gpios`: Output GPIO pin for setting the FSI mux (internal or cabled); maxItems 1.
- `fsi-mux-gpios`: Input GPIO pin for detecting the desired FSI mux state; maxItems 1.
- `interrupts`: maxItems 1.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.
- Nested conditional keywords present: `else`, `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the FSI topology visible to service processors; runtime probing follows FSI master/controller discovery into child engines such as SBEFIFO, SCOM, OCC, or SPI bridges.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent topology is represented by DT child nodes and addressing cells; mutable FSI engine state remains in bus and device drivers.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `fsi-controller.yaml#`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Includes 2 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fsi/aspeed,ast2600-fsi-master.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `aspeed,ast2600-fsi-master`, `aspeed,ast2700-fsi-master`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/aspeed,ast2600-fsi-master.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/fsi-controller.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/fsi-controller.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FSI bus/controller/peripheral binding for FSI Controller Common Properties. FSI (FRU (Field Replaceable Unit) Service Interface) is a two wire bus. The FSI bus is connected to a CFAM (Common FRU Access Macro) which contains various engines such as I2C controllers, SPI controllers, etc.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fsi/fsi-controller.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `FSI Controller Common Properties`.
- No top-level `required` list is declared; requirements are delegated to referenced schemas, branch logic, or child schemas.
- `#address-cells`: const `2`.
- `#size-cells`: const `0`.
- `#interrupt-cells`: const `1`.
- `bus-frequency`: constraints via minimum, maximum.
- `interrupt-controller` is accepted as a flag/property marker.
- `no-scan-on-init`: The FSI controller cannot scan the bus during initialization.; ref `/schemas/types.yaml#/definitions/flag`.
- Pattern child/property schemas: `cfam@[0-9a-f],[0-9a-f]`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the FSI topology visible to service processors; runtime probing follows FSI master/controller discovery into child engines such as SBEFIFO, SCOM, OCC, or SPI bridges.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent topology is represented by DT child nodes and addressing cells; mutable FSI engine state remains in bus and device drivers.
- `additionalProperties` is `True`, so the node is open for extra properties or delegated schemas.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`.

## Risks and edge cases
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fsi/fsi-controller.yaml` plus `make dtbs_check` on boards using the compatible strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/fsi-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/fsi-master-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/fsi-master-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FSI bus/controller/peripheral binding for fsi-master-gpio. fsi-master-gpio

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fsi/fsi-master-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `fsi-master-gpio`.
- Top-level required properties: `compatible`, `clock-gpios`, `data-gpios`.
- `compatible`: 1 ordered items.
- `clock-gpios`: GPIO for FSI clock; maxItems 1.
- `data-gpios`: GPIO for FSI data signal; maxItems 1.
- `enable-gpios`: GPIO for enable signal; maxItems 1.
- `trans-gpios`: GPIO for voltage translator enable; maxItems 1.
- `mux-gpios`: GPIO for pin multiplexing with other functions (eg, external FSI masters); maxItems 1.
- `no-gpio-delays`: Don't add extra delays between GPIO accesses. This is useful when the HW GPIO block is running at a low enough....
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the FSI topology visible to service processors; runtime probing follows FSI master/controller discovery into child engines such as SBEFIFO, SCOM, OCC, or SPI bridges.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent topology is represented by DT child nodes and addressing cells; mutable FSI engine state remains in bus and device drivers.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `/schemas/fsi/fsi-controller.yaml`.
- Integrates with provider/consumer property `enable-gpios`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fsi/fsi-master-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/fsi-master-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/ibm,fsi2spi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/ibm,fsi2spi.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FSI bus/controller/peripheral binding for IBM FSI-attached SPI controllers. This binding describes an FSI CFAM engine called the FSI2SPI. Therefore this node will always be a child of an FSI CFAM node. This FSI2SPI engine provides access to a number of SPI controllers.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fsi/ibm,fsi2spi.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `IBM FSI-attached SPI controllers`.
- Compatible strings or compatible constants enumerated by the schema include `ibm,fsi2spi`.
- Top-level required properties: `compatible`, `reg`.
- `compatible`: enum `ibm,fsi2spi`.
- `reg`: 1 ordered items.
- `#address-cells`: const `1`.
- `#size-cells`: const `0`.
- Pattern child/property schemas: `^spi@[0-9a-f]+$`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the FSI topology visible to service processors; runtime probing follows FSI master/controller discovery into child engines such as SBEFIFO, SCOM, OCC, or SPI bridges.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent topology is represented by DT child nodes and addressing cells; mutable FSI engine state remains in bus and device drivers.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/spi/ibm,spi-fsi.yaml`.
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fsi/ibm,fsi2spi.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `ibm,fsi2spi`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/ibm,fsi2spi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/ibm,i2cr-fsi-master.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/ibm,i2cr-fsi-master.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FSI bus/controller/peripheral binding for IBM I2C Responder virtual FSI master. The I2C Responder (I2CR) is a an I2C device that's connected to an FSI CFAM (see fsi.txt). The I2CR translates I2C bus operations to FSI CFAM reads and writes or SCOM operations, thereby acting as an FSI master.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fsi/ibm,i2cr-fsi-master.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `IBM I2C Responder virtual FSI master`.
- Compatible strings or compatible constants enumerated by the schema include `ibm,i2cr-fsi-master`.
- Top-level required properties: `compatible`, `reg`.
- `compatible`: enum `ibm,i2cr-fsi-master`.
- `reg`: maxItems 1.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the FSI topology visible to service processors; runtime probing follows FSI master/controller discovery into child engines such as SBEFIFO, SCOM, OCC, or SPI bridges.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent topology is represented by DT child nodes and addressing cells; mutable FSI engine state remains in bus and device drivers.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `fsi-controller.yaml#`.
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fsi/ibm,i2cr-fsi-master.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `ibm,i2cr-fsi-master`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/ibm,i2cr-fsi-master.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/ibm,p9-fsi-controller.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/ibm,p9-fsi-controller.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FSI bus/controller/peripheral binding for IBM FSI-attached FSI Hub Controller. The FSI Hub Controller is an FSI controller, providing a number of FSI links, located on a CFAM. Therefore this node will always be a child of an FSI CFAM node.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fsi/ibm,p9-fsi-controller.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `IBM FSI-attached FSI Hub Controller`.
- Compatible strings or compatible constants enumerated by the schema include `ibm,p9-fsi-controller`.
- No top-level `required` list is declared; requirements are delegated to referenced schemas, branch logic, or child schemas.
- `compatible`: enum `ibm,p9-fsi-controller`.
- `reg`: 1 ordered items.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the FSI topology visible to service processors; runtime probing follows FSI master/controller discovery into child engines such as SBEFIFO, SCOM, OCC, or SPI bridges.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent topology is represented by DT child nodes and addressing cells; mutable FSI engine state remains in bus and device drivers.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `fsi-controller.yaml#`.
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fsi/ibm,p9-fsi-controller.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `ibm,p9-fsi-controller`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/ibm,p9-fsi-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/ibm,p9-occ.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/ibm,p9-occ.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FSI bus/controller/peripheral binding for IBM FSI-attached On-Chip Controller (OCC). The POWER processor On-Chip Controller (OCC) helps manage power and thermals for the system, accessed through the FSI-attached SBEFIFO from a service processor.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fsi/ibm,p9-occ.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `IBM FSI-attached On-Chip Controller (OCC)`.
- Compatible strings or compatible constants enumerated by the schema include `ibm,p9-occ`, `ibm,p10-occ`.
- Top-level required properties: `compatible`.
- `compatible`: enum `ibm,p9-occ`, `ibm,p10-occ`.
- `hwmon`: ref `/schemas/hwmon/ibm,occ-hwmon.yaml`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the FSI topology visible to service processors; runtime probing follows FSI master/controller discovery into child engines such as SBEFIFO, SCOM, OCC, or SPI bridges.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent topology is represented by DT child nodes and addressing cells; mutable FSI engine state remains in bus and device drivers.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/hwmon/ibm,occ-hwmon.yaml`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fsi/ibm,p9-occ.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `ibm,p9-occ`, `ibm,p10-occ`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/ibm,p9-occ.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/ibm,p9-scom.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/ibm,p9-scom.yaml

## Purpose
This YAML binding defines the Device Tree contract for the FSI bus/controller/peripheral binding for IBM FSI-attached SCOM engine. The SCOM engine is an interface to the POWER processor PIB (Pervasive Interconnect Bus). This node will always be a child of an FSI CFAM node.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fsi/ibm,p9-scom.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `IBM FSI-attached SCOM engine`.
- Compatible strings or compatible constants enumerated by the schema include `ibm,fsi2pib`, `ibm,p9-scom`, `ibm,i2cr-scom`.
- Top-level required properties: `compatible`, `reg`.
- `compatible`: enum `ibm,fsi2pib`, `ibm,p9-scom`, `ibm,i2cr-scom`.
- `reg`: 1 ordered items.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates the FSI topology visible to service processors; runtime probing follows FSI master/controller discovery into child engines such as SBEFIFO, SCOM, OCC, or SPI bridges.

## State and persistence behavior
- Persistent topology is represented by DT child nodes and addressing cells; mutable FSI engine state remains in bus and device drivers.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fsi/ibm,p9-scom.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `ibm,fsi2pib`, `ibm,p9-scom`, `ibm,i2cr-scom`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fsi/ibm,p9-scom.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fuse/nvidia,tegra20-fuse.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fuse/nvidia,tegra20-fuse.yaml

## Purpose
This YAML binding defines the Device Tree contract for the eFuse/SoC fuse binding for NVIDIA Tegra FUSE block. NVIDIA Tegra FUSE block

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/fuse/nvidia,tegra20-fuse.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `NVIDIA Tegra FUSE block`.
- Compatible strings or compatible constants enumerated by the schema include `nvidia,tegra20-efuse`, `nvidia,tegra30-efuse`, `nvidia,tegra114-efuse`, `nvidia,tegra124-efuse`, `nvidia,tegra210-efuse`, `nvidia,tegra186-efuse`, `nvidia,tegra194-efuse`, `nvidia,tegra234-efuse`, `nvidia,tegra132-efuse`.
- Top-level required properties: `compatible`, `reg`, `clocks`, `clock-names`.
- `compatible`: constraints via oneOf.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `clock-names`: 1 ordered items.
- `resets`: maxItems 1.
- `reset-names`: 1 ordered items.
- `operating-points-v2` is accepted as a flag/property marker.
- `power-domains`: 1 ordered items.
- Nested conditional keywords present: `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates SoC fuse/NVMEM layout nodes; runtime consumers usually read calibration, identification, or production strap data through nvmem cells.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- The binding describes read-only fuse register windows and NVMEM child cells; durable values live in silicon fuses, not in the schema.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `clock-names`.
- Integrates with provider/consumer property `resets`.
- Integrates with provider/consumer property `power-domains`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/fuse/nvidia,tegra20-fuse.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `nvidia,tegra20-efuse`, `nvidia,tegra30-efuse`, `nvidia,tegra114-efuse`, `nvidia,tegra124-efuse`, `nvidia,tegra210-efuse`, `nvidia,tegra186-efuse`, ....
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/fuse/nvidia,tegra20-fuse.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/brcm,bcm4751.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/brcm,bcm4751.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GNSS receiver binding for Broadcom BCM4751 family GNSS Receiver. Broadcom GPS chips can be used over the UART or I2C bus. The UART bus requires CTS/RTS support. The number of the capsule is more elaborate than the compatibles BCM4751 may be printed BCM4751IFBG for example.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gnss/brcm,bcm4751.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Broadcom BCM4751 family GNSS Receiver`.
- Compatible strings or compatible constants enumerated by the schema include `brcm,bcm4751`, `brcm,bcm4752`, `brcm,bcm4753`.
- Top-level required properties: `compatible`, `enable-gpios`.
- `compatible`: enum `brcm,bcm4751`, `brcm,bcm4752`, `brcm,bcm4753`.
- `reg`: The I2C Address, not required on UART buses..
- `vdd-auxin-supply`: Main voltage supply, pin name VDD_AUXIN, typically connected directly to a battery such as LiIon 3.8V battery or a....
- `vddio-supply`: IO voltage supply, pin name VDDIO, typically 1.8V.
- `reset-gpios`: An optional active low reset line, should be flagged with GPIO_ACTIVE_LOW.; maxItems 1.
- `enable-gpios`: Enable GPIO line, connected to pins named REGPU or NSTANDBY. If the line is active low such as NSTANDBY, it should....
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
- Integrates with provider/consumer property `enable-gpios`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gnss/brcm,bcm4751.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `brcm,bcm4751`, `brcm,bcm4752`, `brcm,bcm4753`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/brcm,bcm4751.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/gnss-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/gnss-common.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GNSS receiver binding for Common Properties for Global Navigation Satellite Systems (GNSS) receiver devices. This document defines device tree properties common to Global Navigation Satellite System receivers.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gnss/gnss-common.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Common Properties for Global Navigation Satellite Systems (GNSS) receiver devices`.
- No top-level `required` list is declared; requirements are delegated to referenced schemas, branch logic, or child schemas.
- `$nodename`: pattern `^gnss(@.*)?$`.
- `lna-supply`: A separate regulator supplying power for the Low Noise Amplifier (LNA). This is an amplifier connected between the....
- `enable-gpios`: A GPIO line that will enable the GNSS receiver when asserted. If this line is active low, the GPIO phandle should...; maxItems 1.
- `timepulse-gpios`: Timepulse signal; maxItems 1.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- The schema validates a serial or platform GNSS receiver node so the GNSS subsystem can bind transport, regulators, reset lines, and optional backup/enable controls consistently.

## State and persistence behavior
- The DT node records hardware wiring and optional regulator/reset/enable policy; live receiver state, fix data, and protocol state are handled by GNSS/serdev drivers.
- `additionalProperties` is `True`, so the node is open for extra properties or delegated schemas.

## Dependencies and integration points
- Integrates with provider/consumer property `enable-gpios`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Main risk is schema drift from the bound kernel driver or from DTS examples that are not covered by validation.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gnss/gnss-common.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/gnss-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/mediatek.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/mediatek.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GNSS receiver binding for Mediatek GNSS Receiver. Mediatek chipsets are used in GNSS-receiver modules produced by several vendors and can use a UART interface.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gnss/mediatek.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Mediatek GNSS Receiver`.
- Compatible strings or compatible constants enumerated by the schema include `globaltop,pa6h`.
- Top-level required properties: `compatible`, `vcc-supply`.
- `compatible`: const `globaltop,pa6h`.
- `vcc-supply`: Main voltage regulator, pin name VCC..
- `reset-gpios`: An optional reset line, with names such as RESET or NRESET. If the line is active low it should be flagged with...; maxItems 1.
- `timepulse-gpios`: Comes with pin names such as PPS1 or 1PPS..
- `gnss-fix-gpios`: GPIO used to determine device position fix state, pin names FIX or 3D_FIX.; maxItems 1.
- `vbackup-supply`: Regulator providing backup voltage, pin names such as VBAT or VBACKUP..
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
- Integrates with provider/consumer property `reset-gpios`.
- Integrates with provider/consumer property `vcc-supply`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gnss/mediatek.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `globaltop,pa6h`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/mediatek.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/u-blox,neo-6m.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/u-blox,neo-6m.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GNSS receiver binding for u-blox GNSS receiver. The u-blox GNSS receivers can use UART, DDC (I2C), SPI and USB interfaces.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gnss/u-blox,neo-6m.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `u-blox GNSS receiver`.
- Compatible strings or compatible constants enumerated by the schema include `u-blox,neo-6m`, `u-blox,neo-8`, `u-blox,neo-m8`, `u-blox,neo-m9`.
- Top-level required properties: `compatible`, `vcc-supply`.
- `compatible`: constraints via oneOf.
- `reg`: The DDC Slave Address, SPI chip select address, the number of the USB hub port or the USB host-controller port to....
- `reset-gpios`: maxItems 1.
- `safeboot-gpios`: maxItems 1.
- `vcc-supply`: Main voltage regulator.
- `u-blox,extint-gpios`: GPIO connected to the "external interrupt" input pin; maxItems 1.
- `v-bckp-supply`: Backup voltage regulator.
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
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gnss/u-blox,neo-6m.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `u-blox,neo-6m`, `u-blox,neo-8`, `u-blox,neo-m8`, `u-blox,neo-m9`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gnss/u-blox,neo-6m.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/abilis,tb10x-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/abilis,tb10x-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Abilis TB10x GPIO controller. Abilis TB10x GPIO controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/abilis,tb10x-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Abilis TB10x GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `abilis,tb10x-gpio`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `abilis,ngpio`.
- `compatible`: const `abilis,tb10x-gpio`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `gpio-ranges` is accepted as a flag/property marker.
- `gpio-ranges-group-names` is accepted as a flag/property marker.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: Interrupts are triggered on both edges; const `1`.
- `interrupts`: maxItems 1.
- `abilis,ngpio`: Number of GPIO pins this driver controls; ref `/schemas/types.yaml#/definitions/uint32`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/abilis,tb10x-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `abilis,tb10x-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/abilis,tb10x-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/adi,ds4520-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/adi,ds4520-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for DS4520 I2C GPIO expander. DS4520 I2C GPIO expander

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/adi,ds4520-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `DS4520 I2C GPIO expander`.
- Compatible strings or compatible constants enumerated by the schema include `adi,ds4520-gpio`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `ngpios`.
- `compatible`: enum `adi,ds4520-gpio`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `ngpios`: constraints via minimum, maximum.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/adi,ds4520-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `adi,ds4520-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/adi,ds4520-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/airoha,en7523-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/airoha,en7523-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Airoha EN7523 GPIO controller. Airoha's GPIO controller on their ARM EN7523 SoCs consists of two banks of 32 GPIOs.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/airoha,en7523-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Airoha EN7523 GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `airoha,en7523-gpio`.
- Top-level required properties: `compatible`, `reg`, `#gpio-cells`, `gpio-controller`.
- `$nodename`: pattern `^gpio@[0-9a-f]+$`.
- `compatible`: 1 ordered items.
- `reg`: The first tuple points to the input register. The second and third tuple point to the direction registers The...; maxItems 4.
- `#gpio-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/airoha,en7523-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `airoha,en7523-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/airoha,en7523-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/altr-pio-1.0.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/altr-pio-1.0.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Altera GPIO controller. Altera GPIO controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/altr-pio-1.0.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Altera GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `altr,pio-1.0`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `interrupts`, `interrupt-controller`, `#interrupt-cells`.
- `compatible`: const `altr,pio-1.0`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: First cell is the GPIO offset number. Second cell is reserved and currently unused.; const `2`.
- `interrupts`: maxItems 1.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `altr,ngpio`: Width of the GPIO bank.; ref `/schemas/types.yaml#/definitions/uint32`.
- `altr,interrupt-type`: Specifies the interrupt trigger type synthesized by hardware. Values defined in...; enum `1`, `2`, `3`, `4`; ref `/schemas/types.yaml#/definitions/uint32`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/altr-pio-1.0.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `altr,pio-1.0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/altr-pio-1.0.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/apm,xgene-gpio-sb.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/apm,xgene-gpio-sb.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for APM X-Gene Standby GPIO controller. This is a gpio controller in the standby domain. It also supports interrupt in some particular pins which are sourced to its parent interrupt controller as diagram below: +-----------------+ | X-Gene standby | | GPIO controller +------ GPIO_0 +------------+ | | ... | Parent IRQ | EXT_INT_0 | +------ GPIO_8/EXT_INT_0 | controller | (SPI40) | | ... | (GICv2) +--------------+ +------ GPIO_[N+8]/EXT_INT_N | | ... | | | | EXT_INT_N | +------ GPIO_[N+9] | | (SPI[40 + N])| | ... | +--------------+ +------ GPIO_MAX.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/apm,xgene-gpio-sb.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `APM X-Gene Standby GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `apm,xgene-gpio-sb`.
- Top-level required properties: `compatible`, `reg`, `#gpio-cells`, `gpio-controller`, `interrupts`, `#interrupt-cells`, `interrupt-controller`.
- `compatible`: const `apm,xgene-gpio-sb`.
- `reg`: maxItems 1.
- `#gpio-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `interrupts`: List of interrupt specifiers for EXT_INT_0 through EXT_INT_N. The first entry must correspond to EXT_INT_0..
- `#interrupt-cells`: First cell selects EXT_INT_N (0-N), second cell specifies flags; const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `apm,nr-gpios`: Number of GPIO pins; ref `/schemas/types.yaml#/definitions/uint32`.
- `apm,nr-irqs`: Number of interrupt pins; ref `/schemas/types.yaml#/definitions/uint32`.
- `apm,irq-start`: Lowest GPIO pin supporting interrupts; ref `/schemas/types.yaml#/definitions/uint32`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/apm,xgene-gpio-sb.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `apm,xgene-gpio-sb`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/apm,xgene-gpio-sb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/apple,smc-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/apple,smc-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Apple Mac System Management Controller GPIO. Apple Mac System Management Controller GPIO block.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/apple,smc-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Apple Mac System Management Controller GPIO`.
- Compatible strings or compatible constants enumerated by the schema include `apple,smc-gpio`.
- Top-level required properties: `compatible`, `gpio-controller`, `#gpio-cells`.
- `compatible`: const `apple,smc-gpio`.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Standalone schema with no explicit provider-property dependencies beyond dt-schema core metadata.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/apple,smc-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- Board DTS coverage should exercise representative compatible values: `apple,smc-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/apple,smc-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/aspeed,ast2400-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/aspeed,ast2400-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Aspeed GPIO controller. Aspeed GPIO controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/aspeed,ast2400-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Aspeed GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `aspeed,ast2400-gpio`, `aspeed,ast2500-gpio`, `aspeed,ast2600-gpio`, `aspeed,ast2700-gpio`.
- Top-level required properties: `compatible`, `reg`, `interrupts`, `interrupt-controller`, `#interrupt-cells`, `gpio-controller`, `#gpio-cells`.
- `compatible`: enum `aspeed,ast2400-gpio`, `aspeed,ast2500-gpio`, `aspeed,ast2600-gpio`, `aspeed,ast2700-gpio`.
- `reg`: maxItems 1.
- `clocks`: The clock to use for debounce timings; maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-line-names`: maxItems 232; minItems 12.
- `gpio-ranges` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `interrupts`: maxItems 1.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `ngpios`: constraints via minimum, maximum.
- Pattern child/property schemas: `-hog(-[0-9]+)?$`.
- Uses top-level `allOf` with 4 branch(es) for variant-specific validation.
- Nested conditional keywords present: `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Includes 3 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/aspeed,ast2400-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `aspeed,ast2400-gpio`, `aspeed,ast2500-gpio`, `aspeed,ast2600-gpio`, `aspeed,ast2700-gpio`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/aspeed,ast2400-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/aspeed,sgpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/aspeed,sgpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Aspeed SGPIO controller. This SGPIO controller is for ASPEED AST2400, AST2500, AST2600 and AST2700 SoC, AST2700 have two sgpio master both with 256 pins, AST2600 have two sgpio master one with 128 pins another one with 80 pins, AST2500/AST2400 have one sgpio master with 80 pins. Each of the Serial GPIO pins can be programmed to support the following options - Support interrupt option for each input port and various interrupt sensitivity option (level-high, level-low, edge-high, edge-low) - Support reset tolerance option for each output.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/aspeed,sgpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Aspeed SGPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `aspeed,ast2400-sgpio`, `aspeed,ast2500-sgpio`, `aspeed,ast2600-sgpiom`, `aspeed,ast2700-sgpiom`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `interrupts`, `interrupt-controller`, `#interrupt-cells`, `ngpios`, `clocks`, `bus-frequency`.
- `compatible`: enum `aspeed,ast2400-sgpio`, `aspeed,ast2500-sgpio`, `aspeed,ast2600-sgpiom`, `aspeed,ast2700-sgpiom`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-line-names`: maxItems 256; minItems 160.
- `#gpio-cells`: const `2`.
- `interrupts`: maxItems 1.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `clocks`: maxItems 1.
- `ngpios` is accepted as a flag/property marker.
- `bus-frequency` is accepted as a flag/property marker.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/aspeed,sgpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `aspeed,ast2400-sgpio`, `aspeed,ast2500-sgpio`, `aspeed,ast2600-sgpiom`, `aspeed,ast2700-sgpiom`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/aspeed,sgpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/atmel,at91rm9200-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/atmel,at91rm9200-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Microchip GPIO controller (PIO). Microchip GPIO controller (PIO)

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/atmel,at91rm9200-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Microchip GPIO controller (PIO)`.
- Compatible strings or compatible constants enumerated by the schema include `atmel,at91sam9x5-gpio`, `microchip,sam9x60-gpio`, `atmel,at91rm9200-gpio`, `microchip,sam9x7-gpio`.
- Top-level required properties: `compatible`, `reg`, `interrupts`, `interrupt-controller`, `#interrupt-cells`, `gpio-controller`, `#gpio-cells`, `clocks`.
- `compatible`: constraints via oneOf.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-line-names` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `clocks`: maxItems 1.
- `#gpio-lines`: Number of gpio, 32 by default if absent; maxItems 1.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/atmel,at91rm9200-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `atmel,at91sam9x5-gpio`, `microchip,sam9x60-gpio`, `atmel,at91rm9200-gpio`, `microchip,sam9x7-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/atmel,at91rm9200-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/blaize,blzp1600-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/blaize,blzp1600-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Blaize BLZP1600 GPIO controller. Blaize BLZP1600 GPIO controller is an implementation of the VeriSilicon APB GPIO v0.2 IP block. It has 32 ports each of which are intended to be represented as child nodes with the generic GPIO-controller properties as described in this binding's file.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/blaize,blzp1600-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Blaize BLZP1600 GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `blaize,blzp1600-gpio`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`.
- `$nodename`: pattern `^gpio@[0-9a-f]+$`.
- `compatible`: enum `blaize,blzp1600-gpio`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `ngpios`: constraints via default, minimum, maximum.
- `interrupts`: maxItems 1.
- `gpio-line-names` is accepted as a flag/property marker.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/blaize,blzp1600-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `blaize,blzp1600-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/blaize,blzp1600-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/brcm,bcm63xx-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/brcm,bcm63xx-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Broadcom BCM63xx GPIO controller. Bindings for Broadcom's BCM63xx memory-mapped GPIO controllers. These bindings can be used on any BCM63xx SoC. However, BCM6338 and BCM6345 are the only ones which don't need a pinctrl driver. BCM6338 have 8-bit data and dirout registers, where GPIO state can be read and/or written, and the direction changed from input to output. BCM6318, BCM6328, BCM6358, BCM6362, BCM6368 and BCM63268 have 32-bit data and dirout registers, where GPIO state can be read and/or written, and the direction changed from input to output.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/brcm,bcm63xx-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Broadcom BCM63xx GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `brcm,bcm6318-gpio`, `brcm,bcm6328-gpio`, `brcm,bcm6358-gpio`, `brcm,bcm6362-gpio`, `brcm,bcm6368-gpio`, `brcm,bcm63268-gpio`.
- Top-level required properties: `compatible`, `reg`, `reg-names`, `gpio-controller`, `#gpio-cells`.
- `compatible`: enum `brcm,bcm6318-gpio`, `brcm,bcm6328-gpio`, `brcm,bcm6358-gpio`, `brcm,bcm6362-gpio`, `brcm,bcm6368-gpio`, `brcm,bcm63268-gpio`.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `gpio-ranges`: maxItems 1.
- `native-endian` is accepted as a flag/property marker.
- `reg`: maxItems 2.
- `reg-names`: 2 ordered items.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/brcm,bcm63xx-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `brcm,bcm6318-gpio`, `brcm,bcm6328-gpio`, `brcm,bcm6358-gpio`, `brcm,bcm6362-gpio`, `brcm,bcm6368-gpio`, `brcm,bcm63268-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/brcm,bcm63xx-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/brcm,brcmstb-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/brcm,brcmstb-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Broadcom STB "UPG GIO" GPIO controller. The controller's registers are organized as sets of eight 32-bit registers with each set controlling a bank of up to 32 pins. A single interrupt is shared for all of the banks handled by the controller.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/brcm,brcmstb-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Broadcom STB "UPG GIO" GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `brcm,bcm7445-gpio`, `brcm,brcmstb-gpio`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `brcm,gpio-bank-widths`.
- `compatible`: 2 ordered items.
- `reg`: Define the base and range of the I/O address space containing the brcmstb GPIO controller registers; maxItems 1.
- `#gpio-cells`: The first cell is the pin number (within the controller's pin space), and the second is used for the following:...; const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `brcm,gpio-bank-widths`: Number of GPIO lines for each bank. Number of elements must correspond to number of banks suggested by the 'reg'...; ref `/schemas/types.yaml#/definitions/uint32-array`.
- `interrupts`: The interrupt shared by all GPIO lines for this controller.; maxItems 1.
- `#interrupt-cells`: The first cell is the GPIO number, the second should specify flags. The following subset of flags is supported: -...; const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `gpio-ranges` is accepted as a flag/property marker.
- `gpio-line-names`: maxItems 128; minItems 1.
- `wakeup-source`: GPIOs for this controller can be used as a wakeup source.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32-array`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/brcm,brcmstb-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `brcm,bcm7445-gpio`, `brcm,brcmstb-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/brcm,brcmstb-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/brcm,kona-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/brcm,kona-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Broadcom Kona family GPIO controller. The Broadcom GPIO Controller IP can be configured prior to synthesis to support up to 8 banks of 32 GPIOs where each bank has its own IRQ. The GPIO controller only supports edge, not level, triggering of interrupts.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/brcm,kona-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Broadcom Kona family GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `brcm,bcm11351-gpio`, `brcm,bcm21664-gpio`, `brcm,bcm23550-gpio`, `brcm,kona-gpio`.
- Top-level required properties: `compatible`, `reg`, `interrupts`, `#gpio-cells`, `#interrupt-cells`, `gpio-controller`, `interrupt-controller`.
- `compatible`: 2 ordered items.
- `reg`: maxItems 1.
- `interrupts`: The interrupt outputs from the controller. There is one GPIO interrupt per GPIO bank. The number of interrupts...; maxItems 6; minItems 4.
- `#gpio-cells`: const `2`.
- `#interrupt-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `interrupt-controller` is accepted as a flag/property marker.
- Uses top-level `allOf` with 2 branch(es) for variant-specific validation.
- Nested conditional keywords present: `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/brcm,kona-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `brcm,bcm11351-gpio`, `brcm,bcm21664-gpio`, `brcm,bcm23550-gpio`, `brcm,kona-gpio`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/brcm,kona-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/brcm,xgs-iproc-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/brcm,xgs-iproc-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Broadcom XGS iProc GPIO controller. This controller is the Chip Common A GPIO present on a number of Broadcom switch ASICs with integrated SoCs.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/brcm,xgs-iproc-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Broadcom XGS iProc GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `brcm,iproc-gpio-cca`.
- Top-level required properties: `compatible`, `reg`, `#gpio-cells`, `gpio-controller`.
- `compatible`: const `brcm,iproc-gpio-cca`.
- `reg`: 2 ordered items.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `ngpios`: constraints via minimum, maximum.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `interrupts`: maxItems 1.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/brcm,xgs-iproc-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `brcm,iproc-gpio-cca`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/brcm,xgs-iproc-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/cavium,octeon-3860-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/cavium,octeon-3860-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Cavium Octeon 3860 GPIO controller. Cavium Octeon 3860 GPIO controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/cavium,octeon-3860-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Cavium Octeon 3860 GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `cavium,octeon-3860-gpio`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `interrupt-controller`, `#interrupt-cells`, `interrupts`.
- `compatible`: const `cavium,octeon-3860-gpio`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `interrupts`: maxItems 16.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/cavium,octeon-3860-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `cavium,octeon-3860-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/cavium,octeon-3860-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/cdns,gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/cdns,gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Cadence GPIO Controller. Cadence GPIO Controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/cdns,gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Cadence GPIO Controller`.
- Compatible strings or compatible constants enumerated by the schema include `cdns,gpio-r1p02`, `axiado,ax3000-gpio`.
- Top-level required properties: `compatible`, `reg`, `clocks`, `gpio-controller`, `#gpio-cells`.
- `compatible`: constraints via oneOf.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `ngpios`: constraints via minimum, maximum.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: - First cell is the GPIO line number. - Second cell is flags as defined in <dt-bindings/gpio/gpio.h>, only...; const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: - First cell is the GPIO line number used as IRQ. - Second cell is the trigger type, as defined in...; const `2`.
- `interrupts`: maxItems 1.
- Nested conditional keywords present: `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/cdns,gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `cdns,gpio-r1p02`, `axiado,ax3000-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/cdns,gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/cirrus,clps711x-mctrl-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/cirrus,clps711x-mctrl-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for ARM Cirrus Logic CLPS711X SYSFLG1 MCTRL GPIOs. ARM Cirrus Logic CLPS711X SYSFLG1 MCTRL GPIOs

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/cirrus,clps711x-mctrl-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `ARM Cirrus Logic CLPS711X SYSFLG1 MCTRL GPIOs`.
- Compatible strings or compatible constants enumerated by the schema include `cirrus,ep7312-mctrl-gpio`, `cirrus,ep7209-mctrl-gpio`.
- Top-level required properties: `compatible`, `gpio-controller`, `#gpio-cells`.
- `compatible`: constraints via oneOf.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `gpio,syscon-dev`: Phandle and offset of device's specific registers within the syscon state control registers; 1 ordered items; ref `/schemas/types.yaml#/definitions/phandle-array`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/phandle-array`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/cirrus,clps711x-mctrl-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `cirrus,ep7312-mctrl-gpio`, `cirrus,ep7209-mctrl-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/cirrus,clps711x-mctrl-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/delta,tn48m-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/delta,tn48m-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Delta Networks TN48M CPLD GPIO controller. This module is part of the Delta TN48M multi-function device. For more details see ../mfd/delta,tn48m-cpld.yaml. Delta TN48M has an onboard Lattice CPLD that is used as an GPIO expander. It provides 12 pins in total, they are input-only or ouput-only type.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/delta,tn48m-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Delta Networks TN48M CPLD GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `delta,tn48m-gpo`, `delta,tn48m-gpi`.
- Top-level required properties: `compatible`, `reg`, `#gpio-cells`, `gpio-controller`.
- `compatible`: enum `delta,tn48m-gpo`, `delta,tn48m-gpi`.
- `reg`: maxItems 1.
- `#gpio-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/delta,tn48m-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- Board DTS coverage should exercise representative compatible values: `delta,tn48m-gpo`, `delta,tn48m-gpi`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/delta,tn48m-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/exar,xra1403.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/exar,xra1403.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for XRA1403 16-bit GPIO Expander with Reset Input. The XRA1403 is an 16-bit GPIO expander with an SPI interface. Features available: - Individually programmable inputs: - Internal pull-up resistors - Polarity inversion - Individual interrupt enable - Rising edge and/or Falling edge interrupt - Input filter - Individually programmable outputs: - Output Level Control - Output Three-State Control

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/exar,xra1403.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `XRA1403 16-bit GPIO Expander with Reset Input`.
- Compatible strings or compatible constants enumerated by the schema include `exar,xra1403`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`.
- `compatible`: const `exar,xra1403`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `reset-gpios`: Control line for the device reset..
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `/schemas/spi/spi-peripheral-props.yaml#`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `reset-gpios`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/exar,xra1403.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `exar,xra1403`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/exar,xra1403.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/fairchild,74hc595.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/fairchild,74hc595.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Generic 8-bit shift register. NOTE: These chips nominally don't have a chip select pin. They do however have a rising-edge triggered latch clock (or storage register clock) pin, which behaves like an active-low chip select. After the bits are shifted into the shift register, CS# is driven high, which the 74HC595 sees as a rising edge on the latch clock that results in a transfer of the bits from the shift register to the storage register and thus to the output pins. _ _ _ _ shift clock ____| |_| |_..._| |_| |_________ latch clock * trigger ___.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/fairchild,74hc595.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Generic 8-bit shift register`.
- Compatible strings or compatible constants enumerated by the schema include `fairchild,74hc595`, `nxp,74lvc594`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `registers-number`.
- `compatible`: enum `fairchild,74hc595`, `nxp,74lvc594`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: The second cell is only used to specify the GPIO polarity.; const `2`.
- `registers-number`: Number of daisy-chained shift registers; ref `/schemas/types.yaml#/definitions/uint32`.
- `enable-gpios`: GPIO connected to the OE (Output Enable) pin.; maxItems 1.
- Pattern child/property schemas: `^(hog-[0-9]+|.+-hog(-[0-9]+)?)$`.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32`, `/schemas/spi/spi-peripheral-props.yaml#`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `enable-gpios`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/fairchild,74hc595.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `fairchild,74hc595`, `nxp,74lvc594`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/fairchild,74hc595.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/faraday,ftgpio010.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/faraday,ftgpio010.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Faraday Technology FTGPIO010 GPIO Controller. Faraday Technology FTGPIO010 GPIO Controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/faraday,ftgpio010.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Faraday Technology FTGPIO010 GPIO Controller`.
- Compatible strings or compatible constants enumerated by the schema include `cortina,gemini-gpio`, `faraday,ftgpio010`, `moxa,moxart-gpio`.
- Top-level required properties: `compatible`, `reg`, `interrupts`, `#gpio-cells`, `interrupt-controller`, `#interrupt-cells`.
- `compatible`: constraints via oneOf.
- `reg`: maxItems 1.
- `resets`: maxItems 1.
- `clocks`: maxItems 1.
- `interrupts`: Should contain the interrupt line for the GPIO block; maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `resets`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/faraday,ftgpio010.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `cortina,gemini-gpio`, `faraday,ftgpio010`, `moxa,moxart-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/faraday,ftgpio010.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/fsl,imx8qxp-sc-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/fsl,imx8qxp-sc-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for GPIO driver over IMX SCU firmware API. This module provides the standard interface to control the resource pins in SCU domain on i.MX8 platforms.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/fsl,imx8qxp-sc-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `GPIO driver over IMX SCU firmware API`.
- Compatible strings or compatible constants enumerated by the schema include `fsl,imx8qxp-sc-gpio`.
- Top-level required properties: `compatible`, `#gpio-cells`, `gpio-controller`.
- `compatible`: enum `fsl,imx8qxp-sc-gpio`.
- `#gpio-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/fsl,imx8qxp-sc-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `fsl,imx8qxp-sc-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/fsl,imx8qxp-sc-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/fsl,qoriq-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/fsl,qoriq-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Freescale MPC512x/MPC8xxx/QorIQ/Layerscape GPIO controller. Freescale MPC512x/MPC8xxx/QorIQ/Layerscape GPIO controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/fsl,qoriq-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Freescale MPC512x/MPC8xxx/QorIQ/Layerscape GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `fsl,mpc5121-gpio`, `fsl,mpc5125-gpio`, `fsl,mpc8314-gpio`, `fsl,mpc8349-gpio`, `fsl,mpc8572-gpio`, `fsl,mpc8610-gpio`, `fsl,pq3-gpio`, `fsl,ls1021a-gpio`, `fsl,ls1028a-gpio`, `fsl,ls1043a-gpio`, `fsl,ls1046a-gpio`, `fsl,ls1088a-gpio`, ....
- Top-level required properties: `compatible`, `reg`, `interrupts`, `#gpio-cells`.
- `compatible`: constraints via oneOf.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `#gpio-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `gpio-line-names`: maxItems 32; minItems 1.
- `little-endian`: GPIO registers are used as little endian. If not present registers are used as big endian by default.; ref `/schemas/types.yaml#/definitions/flag`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/flag`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 2 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Large compatible matrices make fallback ordering and per-device exception branches easy to regress when adding variants.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/fsl,qoriq-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `fsl,mpc5121-gpio`, `fsl,mpc5125-gpio`, `fsl,mpc8314-gpio`, `fsl,mpc8349-gpio`, `fsl,mpc8572-gpio`, `fsl,mpc8610-gpio`, ....
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/fsl,qoriq-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/fsl-imx-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/fsl-imx-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Freescale i.MX/MXC GPIO controller. Freescale i.MX/MXC GPIO controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/fsl-imx-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Freescale i.MX/MXC GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `fsl,imx1-gpio`, `fsl,imx21-gpio`, `fsl,imx31-gpio`, `fsl,imx35-gpio`, `fsl,imx7d-gpio`, `fsl,imx27-gpio`, `fsl,imx25-gpio`, `fsl,imx50-gpio`, `fsl,imx51-gpio`, `fsl,imx53-gpio`, `fsl,imx6q-gpio`, `fsl,imx6sl-gpio`, ....
- Top-level required properties: `compatible`, `reg`, `interrupts`, `interrupt-controller`, `#interrupt-cells`, `#gpio-cells`, `gpio-controller`.
- `compatible`: constraints via oneOf.
- `reg`: maxItems 1.
- `interrupts`: Should be the port interrupt shared by all 32 pins, if one number. If two numbers, the first one is the interrupt...; maxItems 2; minItems 1.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `clocks`: maxItems 1.
- `#gpio-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-line-names` is accepted as a flag/property marker.
- `gpio-ranges` is accepted as a flag/property marker.
- `power-domains`: maxItems 1.
- Pattern child/property schemas: `^(hog-[0-9]+|.+-hog(-[0-9]+)?)$`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `power-domains`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Large compatible matrices make fallback ordering and per-device exception branches easy to regress when adding variants.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/fsl-imx-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `fsl,imx1-gpio`, `fsl,imx21-gpio`, `fsl,imx31-gpio`, `fsl,imx35-gpio`, `fsl,imx7d-gpio`, `fsl,imx27-gpio`, ....
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/fsl-imx-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/fujitsu,mb86s70-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/fujitsu,mb86s70-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Fujitsu MB86S7x GPIO Controller. Fujitsu MB86S7x GPIO Controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/fujitsu,mb86s70-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Fujitsu MB86S7x GPIO Controller`.
- Compatible strings or compatible constants enumerated by the schema include `socionext,synquacer-gpio`, `fujitsu,mb86s70-gpio`.
- Top-level required properties: `compatible`, `reg`, `#gpio-cells`, `gpio-controller`, `clocks`.
- `compatible`: constraints via oneOf.
- `reg`: maxItems 1.
- `#gpio-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-line-names` is accepted as a flag/property marker.
- `clocks`: maxItems 1.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `clocks`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/fujitsu,mb86s70-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `socionext,synquacer-gpio`, `fujitsu,mb86s70-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/fujitsu,mb86s70-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-consumer-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-consumer-common.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Common GPIO lines. Pay attention to using proper GPIO flag (e.g. GPIO_ACTIVE_LOW) for the GPIOs using inverted signal (e.g. RESETN).

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/gpio-consumer-common.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Common GPIO lines`.
- No top-level `required` list is declared; requirements are delegated to referenced schemas, branch logic, or child schemas.
- `enable-gpios`: GPIO connected to the enable control pin.; maxItems 1.
- `reset-gpios`: GPIO (or GPIOs for power sequence) connected to the device reset pin (e.g. RESET or RESETN)..
- `powerdown-gpios`: GPIO connected to the power down pin (hardware power down or power cut, e.g. PD or PWDN).; maxItems 1.
- `pwdn-gpios`: Use powerdown-gpios; maxItems 1.
- `wakeup-gpios`: GPIO connected to the pin waking up the device from suspend or other power-saving modes.; maxItems 1.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.
- Nested conditional keywords present: `else`, `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `True`, so the node is open for extra properties or delegated schemas.

## Dependencies and integration points
- Integrates with provider/consumer property `reset-gpios`.
- Integrates with provider/consumer property `enable-gpios`.

## Risks and edge cases
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/gpio-consumer-common.yaml` plus `make dtbs_check` on boards using the compatible strings.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-consumer-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-davinci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-davinci.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for GPIO controller for Davinci and keystone devices. GPIO controller for Davinci and keystone devices

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/gpio-davinci.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `GPIO controller for Davinci and keystone devices`.
- Compatible strings or compatible constants enumerated by the schema include `ti,k2g-gpio`, `ti,am654-gpio`, `ti,j721e-gpio`, `ti,am64-gpio`, `ti,keystone-gpio`, `ti,dm6441-gpio`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `interrupts`, `ti,ngpio`, `ti,davinci-gpio-unbanked`, `clocks`, `clock-names`.
- `compatible`: constraints via oneOf.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-ranges` is accepted as a flag/property marker.
- `gpio-reserved-ranges` is accepted as a flag/property marker.
- `gpio-line-names`: strings describing the names of each gpio line.; maxItems 144; minItems 1.
- `#gpio-cells`: first cell is the pin number and second cell is used to specify optional parameters (unused).; const `2`.
- `interrupts`: The interrupts are specified as per the interrupt parent. Only banked or unbanked IRQs are supported at a time. If...; maxItems 100; minItems 1.
- `ti,ngpio`: The number of GPIO pins supported consecutively.; ref `/schemas/types.yaml#/definitions/uint32`.
- `ti,davinci-gpio-unbanked`: The number of GPIOs that have an individual interrupt line to processor.; ref `/schemas/types.yaml#/definitions/uint32`.
- `clocks`: maxItems 1.
- `clock-names`: const `gpio`.
- `interrupt-controller` is accepted as a flag/property marker.
- `power-domains`: maxItems 1.
- `#interrupt-cells`: const `2`.
- Pattern child/property schemas: `^(.+-hog(-[0-9]+)?)$`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `clock-names`.
- Integrates with provider/consumer property `power-domains`.
- Includes 3 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/gpio-davinci.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `ti,k2g-gpio`, `ti,am654-gpio`, `ti,j721e-gpio`, `ti,am64-gpio`, `ti,keystone-gpio`, `ti,dm6441-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-davinci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-delay.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-delay.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for GPIO delay controller. This binding describes an electrical setup where setting an GPIO output is delayed by some external setup, e.g. RC circuit. +----------+ +-----------+ | | VCC_B | | | | | | | | | VCC_A _ | | | GPIO | | | R | Consumer | |controller| ___ |_| | | | | | | | | | | [IOx|-------| |--+-----|-----+ | | | |___| | | input | | | | | | +----------+ --- C +-----------+ --- | - GND If the input on the consumer is controlled by an open-drain signal attached to an RC circuit the ramp-up delay is not under control of the GPIO.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/gpio-delay.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `GPIO delay controller`.
- Top-level required properties: `compatible`, `#gpio-cells`, `gpio-controller`, `gpios`.
- `compatible`: const `gpio-delay`.
- `#gpio-cells`: Specifies the pin, ramp-up and ramp-down delays. The delays are specified in microseconds.; const `3`.
- `gpios`: Array of GPIOs which output signal change is delayed; maxItems 32; minItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-line-names`: maxItems 32; minItems 1.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/gpio-delay.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-delay.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-ep9301.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-ep9301.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for EP93xx GPIO controller. EP93xx GPIO controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/gpio-ep9301.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `EP93xx GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `cirrus,ep9301-gpio`, `cirrus,ep9302-gpio`, `cirrus,ep9307-gpio`, `cirrus,ep9312-gpio`, `cirrus,ep9315-gpio`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`.
- `compatible`: constraints via oneOf.
- `reg`: minItems 2; 3 ordered items.
- `reg-names`: minItems 2; 3 ordered items.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-ranges` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `interrupts`: constraints via oneOf.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/gpio-ep9301.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `cirrus,ep9301-gpio`, `cirrus,ep9302-gpio`, `cirrus,ep9307-gpio`, `cirrus,ep9312-gpio`, `cirrus,ep9315-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-ep9301.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-latch.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-latch.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for GPIO latch controller. This binding describes a GPIO multiplexer based on latches connected to other GPIOs, like this: CLK0 ----------------------. ,--------. CLK1 -------------------. `--------|> #0 | | | | OUT0 ----------------+--|-----------|D0 Q0|-----|< OUT1 --------------+-|--|-----------|D1 Q1|-----|< OUT2 ------------+-|-|--|-----------|D2 Q2|-----|< OUT3 ----------+-|-|-|--|-----------|D3 Q3|-----|< OUT4 --------+-|-|-|-|--|-----------|D4 Q4|-----|< OUT5 ------+-|-|-|-|-|--|-----------|D5 Q5|-----|< OUT6.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/gpio-latch.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `GPIO latch controller`.
- Top-level required properties: `compatible`, `#gpio-cells`, `gpio-controller`, `clk-gpios`, `latched-gpios`.
- `compatible`: const `gpio-latch`.
- `#gpio-cells`: const `2`.
- `clk-gpios`: Array of GPIOs to be used to clock a latch.
- `latched-gpios`: Array of GPIOs to be used as inputs per latch.
- `setup-duration-ns`: Delay in nanoseconds to wait after the latch inputs have been set up.
- `clock-duration-ns`: Delay in nanoseconds to wait between clock output changes.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-line-names` is accepted as a flag/property marker.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/gpio-latch.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-latch.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-line-mux.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-line-mux.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for GPIO line mux. A GPIO controller to provide virtual GPIOs for a 1-to-many input-only mapping backed by a single shared GPIO and a multiplexer. A simple illustrated example is: +----- A IN / <-----o------- B / |\ | | +----- C | | \ | | +--- D | | M1 M0 MUX CONTROL M1 M0 IN 0 0 A 0 1 B 1 0 C 1 1 D This can be used in case a real GPIO is connected to multiple inputs and controlled by a multiplexer, and another subsystem/driver does not work directly with the multiplexer subsystem.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/gpio-line-mux.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `GPIO line mux`.
- Top-level required properties: `compatible`, `gpio-controller`, `gpio-line-mux-states`, `mux-controls`, `muxed-gpios`.
- `compatible`: const `gpio-line-mux`.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `gpio-line-mux-states`: Mux states corresponding to the virtual GPIOs.; ref `/schemas/types.yaml#/definitions/uint32-array`.
- `gpio-line-names` is accepted as a flag/property marker.
- `mux-controls`: Phandle to the multiplexer to control access to the GPIOs.; maxItems 1.
- `ngpios` is explicitly rejected in this schema branch.
- `muxed-gpios`: GPIO which is the '1' in 1-to-many and is shared by the virtual GPIOs and controlled via the mux.; maxItems 1.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32-array`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/gpio-line-mux.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-line-mux.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-mmio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-mmio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Generic MMIO GPIO. Some simple GPIO controllers may consist of a single data register or a pair of set/clear-bit registers. Such controllers are common for glue logic in FPGAs or ASICs. Commonly, these controllers are accessed over memory-mapped NAND-style parallel busses.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/gpio-mmio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Generic MMIO GPIO`.
- Compatible strings or compatible constants enumerated by the schema include `brcm,bcm6345-gpio`, `intel,ixp4xx-expansion-bus-mmio-gpio`, `ni,169445-nand-gpio`, `opencores,gpio`, `wd,mbl-gpio`.
- Top-level required properties: `compatible`, `reg`, `reg-names`, `#gpio-cells`, `gpio-controller`.
- `compatible`: enum `brcm,bcm6345-gpio`, `intel,ixp4xx-expansion-bus-mmio-gpio`, `ni,169445-nand-gpio`, `opencores,gpio`, `wd,mbl-gpio`.
- `big-endian` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `little-endian` is accepted as a flag/property marker.
- `reg`: A list of registers in the controller. The width of each register is determined by its size. All registers must...; minItems 1; 5 ordered items.
- `reg-names`: maxItems 5; minItems 1.
- `native-endian` is accepted as a flag/property marker.
- `ngpios`: If this property is present the number of usable GPIO lines are restricted to the first 0 .. ngpios lines. This is....
- `no-output`: If this property is present, the controller cannot drive the GPIO lines.; ref `/schemas/types.yaml#/definitions/flag`.
- Pattern child/property schemas: `^.+-hog(-[0-9]+)?$`.
- Nested conditional keywords present: `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/flag`, `/schemas/memory-controllers/intel,ixp4xx-expansion-peripheral-props.yaml#`.
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/gpio-mmio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `brcm,bcm6345-gpio`, `intel,ixp4xx-expansion-bus-mmio-gpio`, `ni,169445-nand-gpio`, `opencores,gpio`, `wd,mbl-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-mmio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-mvebu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-mvebu.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Marvell EBU GPIO controller. Marvell EBU GPIO controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/gpio-mvebu.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Marvell EBU GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `marvell,armada-8k-gpio`, `marvell,orion-gpio`, `marvell,mv78200-gpio`, `marvell,armada-370-gpio`, `marvell,armadaxp-gpio`.
- Top-level required properties: `compatible`, `gpio-controller`, `ngpios`, `#gpio-cells`.
- `compatible`: constraints via oneOf.
- `reg`: Address and length of the register set for the device. Not used for marvell,armada-8k-gpio. A second entry can be...; maxItems 2; minItems 1.
- `reg-names`: minItems 1; 2 ordered items.
- `offset`: Offset in the register map for the gpio registers (in bytes); ref `/schemas/types.yaml#/definitions/uint32`.
- `interrupts`: The list of interrupts that are used for all the pins managed by this GPIO bank. There can be more than one...; maxItems 4; minItems 1.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `ngpios`: constraints via minimum, maximum.
- `#gpio-cells`: const `2`.
- `gpio-ranges`: maxItems 1.
- `marvell,pwm-offset`: Offset in the register map for the pwm registers (in bytes); ref `/schemas/types.yaml#/definitions/uint32`.
- `#pwm-cells`: The first cell is the GPIO line number. The second cell is the period in nanoseconds.; const `2`.
- `clocks`: Clock(s) used for PWM function.; minItems 1; 2 ordered items.
- `clock-names`: minItems 1; 2 ordered items.
- Pattern child/property schemas: `^(.+-hog(-[0-9]+)?)$`.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.
- Nested conditional keywords present: `else`, `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `clock-names`.
- Includes 2 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/gpio-mvebu.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `marvell,armada-8k-gpio`, `marvell,orion-gpio`, `marvell,mv78200-gpio`, `marvell,armada-370-gpio`, `marvell,armadaxp-gpio`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-mvebu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-mxs.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-mxs.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Freescale MXS GPIO controller. The Freescale MXS GPIO controller is part of MXS PIN controller. The GPIOs are organized in port/bank, each port consists of 32 GPIOs. As the GPIO controller is embedded in the PIN controller and all the GPIO ports share the same IO space with PIN controller, the GPIO node will be represented as sub-nodes of MXS pinctrl node.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/gpio-mxs.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Freescale MXS GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `fsl,imx23-pinctrl`, `fsl,imx28-pinctrl`.
- Top-level required properties: `compatible`, `reg`, `#address-cells`, `#size-cells`.
- `compatible`: 2 ordered items.
- `#address-cells`: const `1`.
- `#size-cells`: const `0`.
- `reg`: maxItems 1.
- Pattern child/property schemas: `^(?!gpio@)[^@]+@[0-9]+$`, `^gpio@[0-9]+$`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`.
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/gpio-mxs.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `fsl,imx23-pinctrl`, `fsl,imx28-pinctrl`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-mxs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-pca95xx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-pca95xx.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for NXP PCA95xx I2C GPIO multiplexer. Bindings for the family of I2C GPIO multiplexers/expanders: NXP PCA95xx, Maxim MAX73xx

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/gpio-pca95xx.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `NXP PCA95xx I2C GPIO multiplexer`.
- Compatible strings or compatible constants enumerated by the schema include `toradex,ecgpiol16`, `nxp,pcal6416`, `diodes,pi4ioe5v6534q`, `nxp,pcal6534`, `exar,xra1202`, `maxim,max7310`, `maxim,max7312`, `maxim,max7313`, `maxim,max7315`, `maxim,max7319`, `maxim,max7320`, `maxim,max7321`, ....
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`.
- `compatible`: constraints via oneOf.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `gpio-line-names`: maxItems 40; minItems 1.
- `interrupts`: maxItems 1.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `reset-gpios`: GPIO specification for the RESET input. This is an active low signal to the PCA953x. Not valid for Maxim MAX732x...; maxItems 1.
- `vcc-supply`: Optional power supply. Not valid for Maxim MAX732x devices..
- `wakeup-source`: ref `/schemas/types.yaml#/definitions/flag`.
- Pattern child/property schemas: `^(hog-[0-9]+|.+-hog(-[0-9]+)?)$`.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.
- Nested conditional keywords present: `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/flag`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `reset-gpios`.
- Integrates with provider/consumer property `vcc-supply`.
- Includes 4 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Large compatible matrices make fallback ordering and per-device exception branches easy to regress when adding variants.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/gpio-pca95xx.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `toradex,ecgpiol16`, `nxp,pcal6416`, `diodes,pi4ioe5v6534q`, `nxp,pcal6534`, `exar,xra1202`, `maxim,max7310`, ....
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-pca95xx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-rda.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-rda.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for RDA Micro GPIO controller. RDA Micro GPIO controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/gpio-rda.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `RDA Micro GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `rda,8810pl-gpio`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `ngpios`, `interrupt-controller`, `#interrupt-cells`, `interrupts`.
- `compatible`: const `rda,8810pl-gpio`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `ngpios`: Number of available gpios in a bank..
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `interrupts`: maxItems 1.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/gpio-rda.yaml` plus `make dtbs_check` on boards using the compatible strings.
- Board DTS coverage should exercise representative compatible values: `rda,8810pl-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-rda.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-stp-xway.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-stp-xway.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Lantiq SoC Serial To Parallel (STP) GPIO controller. The Serial To Parallel (STP) is found on MIPS based Lantiq socs. It is a peripheral controller used to drive external shift register cascades. At most 3 groups of 8 bits can be driven. The hardware is able to allow the DSL modem and Ethernet PHYs to drive some bytes of the cascade automatically.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/gpio-stp-xway.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Lantiq SoC Serial To Parallel (STP) GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `lantiq,gpio-stp-xway`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`.
- `$nodename`: pattern `^gpio@[0-9a-f]+$`.
- `compatible`: const `lantiq,gpio-stp-xway`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: The first cell is the pin number and the second cell is used to specify consumer flags.; const `2`.
- `lantiq,shadow`: The default value that we shall assume as already set on the shift register cascade.; ref `/schemas/types.yaml#/definitions/uint32`.
- `lantiq,groups`: Set the 3 bit mask to select which of the 3 groups are enabled in the shift register cascade.; ref `/schemas/types.yaml#/definitions/uint32`.
- `lantiq,dsl`: The dsl core can control the 2 LSBs of the gpio cascade. This 2 bit property can enable this feature.; ref `/schemas/types.yaml#/definitions/uint32`.
- `lantiq,rising`: Use rising instead of falling edge for the shift register..
- Pattern child/property schemas: `^lantiq,phy[1-4]$`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32`.
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/gpio-stp-xway.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `lantiq,gpio-stp-xway`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-stp-xway.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-vf610.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-vf610.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Freescale VF610 PORT/GPIO module. The Freescale PORT/GPIO modules are two adjacent modules providing GPIO functionality. Each pair serves 32 GPIOs. The VF610 has 5 instances of each, and each PORT module has its own interrupt. Note: Each GPIO port should have an alias correctly numbered in "aliases" node.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/gpio-vf610.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Freescale VF610 PORT/GPIO module`.
- Compatible strings or compatible constants enumerated by the schema include `fsl,imx8ulp-gpio`, `fsl,vf610-gpio`, `fsl,imx7ulp-gpio`, `fsl,imx93-gpio`, `fsl,imx94-gpio`, `fsl,imx95-gpio`.
- Top-level required properties: `compatible`, `reg`, `interrupts`, `interrupt-controller`, `#interrupt-cells`, `#gpio-cells`, `gpio-controller`.
- `compatible`: constraints via oneOf.
- `reg`: maxItems 2; minItems 1.
- `interrupts`: minItems 1; 2 ordered items.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `#gpio-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-line-names`: maxItems 32; minItems 1.
- `clocks`: 2 ordered items.
- `clock-names`: 2 ordered items.
- `gpio-ranges`: maxItems 4; minItems 1.
- `gpio-reserved-ranges` is accepted as a flag/property marker.
- `ngpios`: constraints via minimum, maximum, default.
- Pattern child/property schemas: `^.+-hog(-[0-9]+)?$`.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.
- Nested conditional keywords present: `else`, `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `clock-names`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/gpio-vf610.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `fsl,imx8ulp-gpio`, `fsl,vf610-gpio`, `fsl,imx7ulp-gpio`, `fsl,imx93-gpio`, `fsl,imx94-gpio`, `fsl,imx95-gpio`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-vf610.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-virtio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-virtio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Virtio GPIO controller. Virtio GPIO controller, see /schemas/virtio/virtio-device.yaml for more details.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/gpio-virtio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Virtio GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `virtio,device29`.
- Top-level required properties: `compatible`, `gpio-controller`, `#gpio-cells`.
- `$nodename`: const `gpio`.
- `compatible`: const `virtio,device29`.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `/schemas/virtio/virtio-device.yaml#`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/gpio-virtio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `virtio,device29`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-virtio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-zynq.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-zynq.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Xilinx Zynq GPIO controller. Xilinx Zynq GPIO controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/gpio-zynq.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Xilinx Zynq GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `xlnx,zynq-gpio-1.0`, `xlnx,zynqmp-gpio-1.0`, `xlnx,versal-gpio-1.0`, `xlnx,pmc-gpio-1.0`.
- Top-level required properties: `compatible`, `reg`, `#gpio-cells`, `interrupts`, `gpio-controller`, `interrupt-controller`, `#interrupt-cells`, `clocks`.
- `compatible`: enum `xlnx,zynq-gpio-1.0`, `xlnx,zynqmp-gpio-1.0`, `xlnx,versal-gpio-1.0`, `xlnx,pmc-gpio-1.0`.
- `reg`: maxItems 1.
- `#gpio-cells`: const `2`.
- `interrupts`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-line-names`: strings describing the names of each gpio line; maxItems 174; minItems 58.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `clocks`: maxItems 1.
- `power-domains`: maxItems 1.
- Uses top-level `allOf` with 4 branch(es) for variant-specific validation.
- Nested conditional keywords present: `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `power-domains`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/gpio-zynq.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `xlnx,zynq-gpio-1.0`, `xlnx,zynqmp-gpio-1.0`, `xlnx,versal-gpio-1.0`, `xlnx,pmc-gpio-1.0`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/gpio-zynq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/hisilicon,ascend910-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/hisilicon,ascend910-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for HiSilicon common GPIO controller. The HiSilicon common GPIO controller can be used for many different types of SoC such as Huawei Ascend AI series chips.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/hisilicon,ascend910-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `HiSilicon common GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `hisilicon,ascend910-gpio`.
- Top-level required properties: `compatible`, `reg`, `interrupts`, `gpio-controller`, `#gpio-cells`, `ngpios`.
- `compatible`: const `hisilicon,ascend910-gpio`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `ngpios`: constraints via minimum, maximum.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/hisilicon,ascend910-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `hisilicon,ascend910-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/hisilicon,ascend910-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/idt,32434-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/idt,32434-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for IDT 79RC32434 GPIO controller. IDT 79RC32434 GPIO controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/idt,32434-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `IDT 79RC32434 GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `idt,32434-gpio`.
- Top-level required properties: `compatible`, `reg`, `reg-names`, `gpio-controller`, `#gpio-cells`.
- `compatible`: const `idt,32434-gpio`.
- `reg`: maxItems 2.
- `reg-names`: 2 ordered items.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `ngpios`: constraints via minimum, maximum.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `interrupts`: maxItems 1.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/idt,32434-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `idt,32434-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/idt,32434-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/intel,ixp4xx-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/intel,ixp4xx-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Intel IXP4xx XScale Networking Processors GPIO Controller. This GPIO controller is found in the Intel IXP4xx processors. It supports 16 GPIO lines. The interrupt portions of the GPIO controller is hierarchical. The synchronous edge detector is part of the GPIO block, but the actual enabling/disabling of the interrupt line is done in the main IXP4xx interrupt controller which has a 1-to-1 mapping for the first 12 GPIO lines to 12 system interrupts. The remaining 4 GPIO lines can not be used for receiving interrupts. The interrupt parent of this GPIO controller must be the.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/intel,ixp4xx-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Intel IXP4xx XScale Networking Processors GPIO Controller`.
- Compatible strings or compatible constants enumerated by the schema include `intel,ixp4xx-gpio`.
- Top-level required properties: `compatible`, `reg`, `#gpio-cells`, `interrupt-controller`, `#interrupt-cells`.
- `compatible`: const `intel,ixp4xx-gpio`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `intel,ixp4xx-gpio14-clkout`: If defined, enables clock output on GPIO 14 instead of GPIO..
- `intel,ixp4xx-gpio15-clkout`: If defined, enables clock output on GPIO 15 instead of GPIO..

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/intel,ixp4xx-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `intel,ixp4xx-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/intel,ixp4xx-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/kontron,sl28cpld-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/kontron,sl28cpld-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for GPIO driver for the sl28cpld board management controller. This module is part of the sl28cpld multi-function device. For more details see ../embedded-controller/kontron,sl28cpld.yaml. There are three flavors of the GPIO controller, one full featured input/output with interrupt support (kontron,sl28cpld-gpio), one output-only (kontron,sl28-gpo) and one input-only (kontron,sl28-gpi). Each controller supports 8 GPIO lines.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/kontron,sl28cpld-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `GPIO driver for the sl28cpld board management controller`.
- Compatible strings or compatible constants enumerated by the schema include `kontron,sl28cpld-gpio`, `kontron,sl28cpld-gpi`, `kontron,sl28cpld-gpo`.
- Top-level required properties: `compatible`, `#gpio-cells`, `gpio-controller`.
- `compatible`: enum `kontron,sl28cpld-gpio`, `kontron,sl28cpld-gpi`, `kontron,sl28cpld-gpo`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `#interrupt-cells`: const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-line-names`: maxItems 8; minItems 1.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/kontron,sl28cpld-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- Board DTS coverage should exercise representative compatible values: `kontron,sl28cpld-gpio`, `kontron,sl28cpld-gpi`, `kontron,sl28cpld-gpo`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/kontron,sl28cpld-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/lacie,netxbig-gpio-ext.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/lacie,netxbig-gpio-ext.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for NetxBig GPIO extension bus. GPIO extension bus found on some LaCie/Seagate boards (Example: 2Big/5Big Network v2, 2Big NAS).

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/lacie,netxbig-gpio-ext.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `NetxBig GPIO extension bus`.
- Compatible strings or compatible constants enumerated by the schema include `lacie,netxbig-gpio-ext`.
- Top-level required properties: `compatible`, `addr-gpios`, `data-gpios`, `enable-gpio`.
- `compatible`: 1 ordered items.
- `addr-gpios`: GPIOs representing the address register (LSB->MSB).; 3 ordered items.
- `data-gpios`: GPIOs representing the data register (LSB->MSB).; 3 ordered items.
- `enable-gpio`: Latches the new configuration (address, data) on raising edge.; maxItems 1.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/lacie,netxbig-gpio-ext.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `lacie,netxbig-gpio-ext`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/lacie,netxbig-gpio-ext.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/lantiq,gpio-mm-lantiq.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/lantiq,gpio-mm-lantiq.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Lantiq SoC External Bus memory mapped GPIO controller. By attaching hardware latches to the EBU it is possible to create output only gpios. This driver configures a special memory address, which when written to outputs 16 bit to the latches. The node describing the memory mapped GPIOs needs to be a child of the node describing the "lantiq,localbus".

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/lantiq,gpio-mm-lantiq.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Lantiq SoC External Bus memory mapped GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `lantiq,gpio-mm-lantiq`, `lantiq,gpio-mm`.
- Top-level required properties: `compatible`, `reg`, `#gpio-cells`, `gpio-controller`.
- `compatible`: enum `lantiq,gpio-mm-lantiq`, `lantiq,gpio-mm`.
- `reg`: maxItems 1.
- `#gpio-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `lantiq,shadow`: The default value that we shall assume as already set on the shift register cascade.; ref `/schemas/types.yaml#/definitions/uint32`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32`.
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/lantiq,gpio-mm-lantiq.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `lantiq,gpio-mm-lantiq`, `lantiq,gpio-mm`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/lantiq,gpio-mm-lantiq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/loongson,ls-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/loongson,ls-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Loongson GPIO controller.. Loongson GPIO controller.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/loongson,ls-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Loongson GPIO controller.`.
- Compatible strings or compatible constants enumerated by the schema include `loongson,ls2k-gpio`, `loongson,ls2k0300-gpio`, `loongson,ls2k0500-gpio0`, `loongson,ls2k0500-gpio1`, `loongson,ls2k2000-gpio0`, `loongson,ls2k2000-gpio1`, `loongson,ls2k2000-gpio2`, `loongson,ls3a5000-gpio`, `loongson,ls3a6000-gpio`, `loongson,ls7a-gpio`, `loongson,ls7a2000-gpio1`, `loongson,ls7a2000-gpio2`, ....
- Top-level required properties: `compatible`, `reg`, `ngpios`, `#gpio-cells`, `gpio-controller`, `gpio-ranges`, `interrupts`.
- `compatible`: constraints via oneOf.
- `reg`: maxItems 1.
- `ngpios`: constraints via minimum, maximum.
- `#gpio-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-ranges` is accepted as a flag/property marker.
- `interrupts`: maxItems 64; minItems 1.
- `#interrupt-cells`: const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `resets`: maxItems 1.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.
- Nested conditional keywords present: `else`, `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `resets`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Large compatible matrices make fallback ordering and per-device exception branches easy to regress when adding variants.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/loongson,ls-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `loongson,ls2k-gpio`, `loongson,ls2k0300-gpio`, `loongson,ls2k0500-gpio0`, `loongson,ls2k0500-gpio1`, `loongson,ls2k2000-gpio0`, `loongson,ls2k2000-gpio1`, ....
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/loongson,ls-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/lsi,zevio-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/lsi,zevio-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Zevio GPIO controller. Zevio GPIO controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/lsi,zevio-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Zevio GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `lsi,zevio-gpio`.
- Top-level required properties: `compatible`, `reg`, `#gpio-cells`, `gpio-controller`.
- `compatible`: 1 ordered items.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `#gpio-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/lsi,zevio-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `lsi,zevio-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/lsi,zevio-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/maxim,max31910.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/maxim,max31910.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Maxim MAX3191x GPIO serializer. Maxim MAX3191x GPIO serializer

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/maxim,max31910.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Maxim MAX3191x GPIO serializer`.
- Compatible strings or compatible constants enumerated by the schema include `maxim,max31910`, `maxim,max31911`, `maxim,max31912`, `maxim,max31913`, `maxim,max31953`, `maxim,max31963`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`.
- `compatible`: enum `maxim,max31910`, `maxim,max31911`, `maxim,max31912`, `maxim,max31913`, `maxim,max31953`, `maxim,max31963`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `#daisy-chained-devices`: Number of chips in the daisy-chain..
- `maxim,modesel-gpios`: GPIO pins to configure modesel of each chip. The number of GPIOs must equal "#daisy-chained-devices" (if each chip....
- `maxim,fault-gpios`: GPIO pins to read fault of each chip. The number of GPIOs must equal "#daisy-chained-devices" or 1..
- `maxim,db0-gpios`: GPIO pins to configure debounce of each chip. The number of GPIOs must equal "#daisy-chained-devices" or 1..
- `maxim,db1-gpios`: GPIO pins to configure debounce of each chip. The number of GPIOs must equal "maxim,db0-gpios"..
- `maxim,modesel-8bit`: Boolean whether the modesel pin of the chips is pulled high (8-bit mode). Use this if the modesel pin is hardwired....
- `maxim,ignore-undervoltage`: Boolean whether to ignore undervoltage alarms signaled by the "maxim,fault-gpios" or by the status byte (in 16-bit....
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `/schemas/spi/spi-peripheral-props.yaml#`.
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/maxim,max31910.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `maxim,max31910`, `maxim,max31911`, `maxim,max31912`, `maxim,max31913`, `maxim,max31953`, `maxim,max31963`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/maxim,max31910.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/maxim,max7360-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/maxim,max7360-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Maxim MAX7360 GPIO controller. Maxim MAX7360 GPIO controller, in MAX7360 chipset https://www.analog.com/en/products/max7360.html The device provides two series of GPIOs, referred here as GPIOs and GPOs. PORT0 to PORT7 pins can be used as GPIOs, with support for interrupts and constant-current mode. These pins will also be used by the rotary encoder and PWM functionalities. COL2 to COL7 pins can be used as GPOs, there is no input capability. COL pins will be partitioned, with the first pins being affected to the keypad functionality and the last.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/maxim,max7360-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Maxim MAX7360 GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `maxim,max7360-gpio`, `maxim,max7360-gpo`.
- Top-level required properties: `compatible`, `gpio-controller`.
- `compatible`: enum `maxim,max7360-gpio`, `maxim,max7360-gpo`.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `maxim,constant-current-disable`: Bit field, each bit disables constant-current output of the associated GPIO, starting from the least significant...; ref `/schemas/types.yaml#/definitions/uint32`.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.
- Nested conditional keywords present: `else`, `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/maxim,max7360-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `maxim,max7360-gpio`, `maxim,max7360-gpo`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/maxim,max7360-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/maxim,max77759-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/maxim,max77759-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Maxim Integrated MAX77759 GPIO. This module is part of the MAX77759 PMIC. For additional information, see Documentation/devicetree/bindings/mfd/maxim,max77759.yaml. The MAX77759 is a PMIC integrating, amongst others, a GPIO controller including interrupt support for 2 GPIO lines.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/maxim,max77759-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Maxim Integrated MAX77759 GPIO`.
- Compatible strings or compatible constants enumerated by the schema include `maxim,max77759-gpio`.
- Top-level required properties: `compatible`, `#gpio-cells`, `gpio-controller`, `#interrupt-cells`, `interrupt-controller`.
- `compatible`: const `maxim,max77759-gpio`.
- `#gpio-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-line-names`: maxItems 2; minItems 1.
- `#interrupt-cells`: const `2`.
- `interrupt-controller` is accepted as a flag/property marker.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Standalone schema with no explicit provider-property dependencies beyond dt-schema core metadata.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/maxim,max77759-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- Board DTS coverage should exercise representative compatible values: `maxim,max77759-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/maxim,max77759-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/mediatek,mt7621-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/mediatek,mt7621-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Mediatek MT7621 SoC GPIO controller. The IP core used inside these SoCs has 3 banks of 32 GPIOs each. The registers of all the banks are interwoven inside one single IO range. We load one GPIO controller instance per bank. Also the GPIO controller can receive interrupts on any of the GPIOs, either edge or level. It then interrupts the CPU using GIC INT12.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/mediatek,mt7621-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Mediatek MT7621 SoC GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `mediatek,mt7621-gpio`.
- Top-level required properties: `compatible`, `reg`, `#gpio-cells`, `gpio-controller`, `gpio-ranges`, `interrupt-controller`, `#interrupt-cells`, `interrupts`.
- `$nodename`: pattern `^gpio@[0-9a-f]+$`.
- `compatible`: const `mediatek,mt7621-gpio`.
- `reg`: maxItems 1.
- `#gpio-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-ranges` is accepted as a flag/property marker.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `interrupts`: maxItems 1.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/mediatek,mt7621-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `mediatek,mt7621-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/mediatek,mt7621-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/microchip,mpfs-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/microchip,mpfs-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Microchip MPFS GPIO Controller. Microchip MPFS GPIO Controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/microchip,mpfs-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Microchip MPFS GPIO Controller`.
- Compatible strings or compatible constants enumerated by the schema include `microchip,pic64gx-gpio`, `microchip,mpfs-gpio`, `microchip,coregpio-rtl-v3`.
- Top-level required properties: `compatible`, `reg`, `#gpio-cells`, `gpio-controller`, `clocks`.
- `compatible`: constraints via oneOf.
- `reg`: maxItems 1.
- `interrupts`: Interrupt mapping, one per GPIO. Maximum 32 GPIOs.; maxItems 32; minItems 1.
- `interrupt-controller` is accepted as a flag/property marker.
- `clocks`: maxItems 1.
- `resets`: maxItems 1.
- `#gpio-cells`: const `2`.
- `#interrupt-cells`: const `2`.
- `ngpios`: The number of GPIOs available..
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-line-names` is accepted as a flag/property marker.
- Pattern child/property schemas: `^.+-hog(-[0-9]+)?$`.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.
- Nested conditional keywords present: `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `resets`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/microchip,mpfs-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `microchip,pic64gx-gpio`, `microchip,mpfs-gpio`, `microchip,coregpio-rtl-v3`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/microchip,mpfs-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/microchip,pic32mzda-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/microchip,pic32mzda-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Microchip PIC32 GPIO controller. Microchip PIC32 GPIO controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/microchip,pic32mzda-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Microchip PIC32 GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `microchip,pic32mzda-gpio`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `gpio-ranges`, `#gpio-cells`, `interrupts`, `interrupt-controller`, `#interrupt-cells`, `clocks`, `microchip,gpio-bank`.
- `compatible`: const `microchip,pic32mzda-gpio`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-ranges` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `interrupts`: maxItems 1.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `clocks`: maxItems 1.
- `microchip,gpio-bank`: Bank index owned by the controller; ref `/schemas/types.yaml#/definitions/uint32`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/microchip,pic32mzda-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `microchip,pic32mzda-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/microchip,pic32mzda-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/mrvl-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/mrvl-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Marvell PXA GPIO controller. Marvell PXA GPIO controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/mrvl-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Marvell PXA GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `intel,pxa25x-gpio`, `intel,pxa26x-gpio`, `intel,pxa27x-gpio`, `intel,pxa3xx-gpio`, `marvell,mmp-gpio`, `marvell,mmp2-gpio`, `marvell,pxa93x-gpio`.
- Top-level required properties: `compatible`, `#address-cells`, `#size-cells`, `reg`, `gpio-controller`, `#gpio-cells`, `interrupts`, `interrupt-names`, `interrupt-controller`, `#interrupt-cells`.
- `$nodename`: pattern `^gpio@[0-9a-f]+$`.
- `compatible`: enum `intel,pxa25x-gpio`, `intel,pxa26x-gpio`, `intel,pxa27x-gpio`, `intel,pxa3xx-gpio`, `marvell,mmp-gpio`, `marvell,mmp2-gpio`, `marvell,pxa93x-gpio`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `resets`: maxItems 1.
- `ranges` is accepted as a flag/property marker.
- `#address-cells`: const `1`.
- `#size-cells`: const `1`.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `gpio-ranges` is accepted as a flag/property marker.
- `interrupts` is accepted as a flag/property marker.
- `interrupt-names` is accepted as a flag/property marker.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- Pattern child/property schemas: `^gpio@[0-9a-f]*$`.
- Uses top-level `allOf` with 2 branch(es) for variant-specific validation.
- Nested conditional keywords present: `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `resets`.
- Includes 2 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/mrvl-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `intel,pxa25x-gpio`, `intel,pxa26x-gpio`, `intel,pxa27x-gpio`, `intel,pxa3xx-gpio`, `marvell,mmp-gpio`, `marvell,mmp2-gpio`, ....
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/mrvl-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/mstar,msc313-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/mstar,msc313-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for MStar/SigmaStar GPIO controller. MStar/SigmaStar GPIO controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/mstar,msc313-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `MStar/SigmaStar GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `mstar,msc313-gpio`, `sstar,ssd20xd-gpio`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `interrupt-controller`, `#interrupt-cells`.
- `$nodename`: pattern `^gpio@[0-9a-f]+$`.
- `compatible`: enum `mstar,msc313-gpio`, `sstar,ssd20xd-gpio`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `gpio-ranges` is accepted as a flag/property marker.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/mstar,msc313-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `mstar,msc313-gpio`, `sstar,ssd20xd-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/mstar,msc313-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nuvoton,sgpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nuvoton,sgpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Nuvoton SGPIO controller. This SGPIO controller is for NUVOTON NPCM7xx and NPCM8xx SoC and detailed information is in the NPCM7XX/8XX SERIAL I/O EXPANSION INTERFACE section. Nuvoton NPCM7xx SGPIO module is combines a serial to parallel IC (HC595) and a parallel to serial IC (HC165). Clock is a division of the APB3 clock. This interface has 4 pins (D_out , D_in, S_CLK, LDSH). NPCM7xx/NPCM8xx have two sgpio modules. Each module can support up to 64 output pins, and up to 64 input pins, the pin is only for GPI or GPO. GPIO pins can be.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/nuvoton,sgpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Nuvoton SGPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `nuvoton,npcm750-sgpio`, `nuvoton,npcm845-sgpio`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `interrupts`, `nuvoton,input-ngpios`, `nuvoton,output-ngpios`, `clocks`.
- `compatible`: enum `nuvoton,npcm750-sgpio`, `nuvoton,npcm845-sgpio`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `interrupts`: maxItems 1.
- `clocks`: maxItems 1.
- `nuvoton,input-ngpios`: The numbers of GPIO's exposed. GPIO lines are only for GPI.; ref `/schemas/types.yaml#/definitions/uint32`.
- `nuvoton,output-ngpios`: The numbers of GPIO's exposed. GPIO lines are only for GPO.; ref `/schemas/types.yaml#/definitions/uint32`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/nuvoton,sgpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `nuvoton,npcm750-sgpio`, `nuvoton,npcm845-sgpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nuvoton,sgpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nvidia,tegra186-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nvidia,tegra186-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for NVIDIA Tegra GPIO Controller (Tegra186 and later). Tegra186 contains two GPIO controllers; a main controller and an "AON" controller. This binding document applies to both controllers. The register layouts for the controllers share many similarities, but also some significant differences. Hence, this document describes closely related but different bindings and compatible values. The Tegra186 GPIO controller allows software to set the IO direction of, and read/write the value of, numerous GPIO signals. Routing of GPIO signals to package balls is under the control.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/nvidia,tegra186-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `NVIDIA Tegra GPIO Controller (Tegra186 and later)`.
- Compatible strings or compatible constants enumerated by the schema include `nvidia,tegra186-gpio`, `nvidia,tegra186-gpio-aon`, `nvidia,tegra194-gpio`, `nvidia,tegra194-gpio-aon`, `nvidia,tegra234-gpio`, `nvidia,tegra234-gpio-aon`, `nvidia,tegra256-gpio`, `nvidia,tegra264-gpio`, `nvidia,tegra264-gpio-uphy`, `nvidia,tegra264-gpio-aon`.
- Top-level required properties: `compatible`, `reg`, `reg-names`, `interrupts`.
- `compatible`: enum `nvidia,tegra186-gpio`, `nvidia,tegra186-gpio-aon`, `nvidia,tegra194-gpio`, `nvidia,tegra194-gpio-aon`, `nvidia,tegra234-gpio`, `nvidia,tegra234-gpio-aon`, `nvidia,tegra256-gpio`, `nvidia,tegra264-gpio`, ....
- `reg-names`: minItems 1; 2 ordered items.
- `reg`: minItems 1; 2 ordered items.
- `interrupts`: The interrupt outputs from the HW block, one per set of ports, in the order the HW manual describes them. The....
- `wakeup-parent`: Phandle to the parent interrupt controller used for wake-up. On Tegra, this typically references the PMC interrupt....
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-ranges`: maxItems 1.
- `#gpio-cells`: Indicates how many cells are used in a consumer's GPIO specifier. In the specifier: - The first cell is the pin...; const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: Indicates how many cells are used in a consumer's interrupt specifier. In the specifier: - The first cell is the...; const `2`.
- Uses top-level `allOf` with 3 branch(es) for variant-specific validation.
- Nested conditional keywords present: `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/nvidia,tegra186-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `nvidia,tegra186-gpio`, `nvidia,tegra186-gpio-aon`, `nvidia,tegra194-gpio`, `nvidia,tegra194-gpio-aon`, `nvidia,tegra234-gpio`, `nvidia,tegra234-gpio-aon`, ....
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nvidia,tegra186-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nvidia,tegra20-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nvidia,tegra20-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for NVIDIA Tegra GPIO Controller (Tegra20 - Tegra210). NVIDIA Tegra GPIO Controller (Tegra20 - Tegra210)

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/nvidia,tegra20-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `NVIDIA Tegra GPIO Controller (Tegra20 - Tegra210)`.
- Compatible strings or compatible constants enumerated by the schema include `nvidia,tegra20-gpio`, `nvidia,tegra30-gpio`, `nvidia,tegra114-gpio`, `nvidia,tegra124-gpio`, `nvidia,tegra210-gpio`.
- Top-level required properties: `compatible`, `reg`, `interrupts`, `#gpio-cells`, `gpio-controller`, `#interrupt-cells`, `interrupt-controller`.
- `compatible`: constraints via oneOf.
- `reg`: maxItems 1.
- `interrupts`: The interrupt outputs from the controller. For Tegra20, there should be 7 interrupts specified, and for Tegra30,....
- `#gpio-cells`: The first cell is the pin number and the second cell is used to specify the GPIO polarity (0 = active high, 1 =...; const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-ranges`: maxItems 1.
- `#interrupt-cells`: Should be 2. The first cell is the GPIO number. The second cell is used to specify flags: bits[3:0] trigger type...; const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.
- Nested conditional keywords present: `else`, `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `{'type': 'object', 'required': ['gpio-hog']}`, so the node is open for extra properties or delegated schemas.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/nvidia,tegra20-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `nvidia,tegra20-gpio`, `nvidia,tegra30-gpio`, `nvidia,tegra114-gpio`, `nvidia,tegra124-gpio`, `nvidia,tegra210-gpio`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nvidia,tegra20-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nxp,lpc1850-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nxp,lpc1850-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for NXP LPC18xx/43xx GPIO controller. NXP LPC18xx/43xx GPIO controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/nxp,lpc1850-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `NXP LPC18xx/43xx GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `nxp,lpc1850-gpio`.
- Top-level required properties: `compatible`, `reg`, `clocks`, `gpio-controller`, `#gpio-cells`.
- `compatible`: const `nxp,lpc1850-gpio`.
- `reg`: maxItems 4; minItems 1.
- `reg-names`: minItems 1; 4 ordered items.
- `clocks`: maxItems 1.
- `resets`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: - The first cell is an interrupt number within 0..9 range, for GPIO pin interrupts it is equal to...; const `2`.
- `gpio-ranges` is accepted as a flag/property marker.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `resets`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/nxp,lpc1850-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `nxp,lpc1850-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nxp,lpc1850-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nxp,lpc3220-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nxp,lpc3220-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for NXP LPC3220 SoC GPIO controller. NXP LPC3220 SoC GPIO controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/nxp,lpc3220-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `NXP LPC3220 SoC GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `nxp,lpc3220-gpio`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`.
- `compatible`: const `nxp,lpc3220-gpio`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: 1) bank: 0: GPIO P0 1: GPIO P1 2: GPIO P2 3: GPIO P3 4: GPI P3 5: GPO P3 2) pin number 3) flags: - bit 0 specifies...; const `3`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/nxp,lpc3220-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `nxp,lpc3220-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nxp,lpc3220-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nxp,pcf8575.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nxp,pcf8575.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for PCF857x-compatible I/O expanders. The PCF857x-compatible chips have "quasi-bidirectional" I/O lines that can be driven high by a pull-up current source or driven low to ground. This combines the direction and output level into a single bit per line, which can't be read back. We can't actually know at initialization time whether a line is configured (a) as output and driving the signal low/high, or (b) as input and reporting a low/high value, without knowing the last value written since the chip came out of reset (if any). The only reliable.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/nxp,pcf8575.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `PCF857x-compatible I/O expanders`.
- Compatible strings or compatible constants enumerated by the schema include `maxim,max7328`, `maxim,max7329`, `nxp,pca8574`, `nxp,pca8575`, `nxp,pca9670`, `nxp,pca9671`, `nxp,pca9672`, `nxp,pca9673`, `nxp,pca9674`, `nxp,pca9675`, `nxp,pcf8574`, `nxp,pcf8574a`, ....
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`.
- `compatible`: enum `maxim,max7328`, `maxim,max7329`, `nxp,pca8574`, `nxp,pca8575`, `nxp,pca9670`, `nxp,pca9671`, `nxp,pca9672`, `nxp,pca9673`, ....
- `reg`: maxItems 1.
- `gpio-line-names`: maxItems 16; minItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: The first cell is the GPIO number and the second cell specifies GPIO flags, as defined in...; const `2`.
- `lines-initial-states`: Bitmask that specifies the initial state of each line. When a bit is set to zero, the corresponding line will be...; ref `/schemas/types.yaml#/definitions/uint32`.
- `interrupts`: maxItems 1.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `wakeup-source` is accepted as a flag/property marker.
- `reset-gpios`: GPIO controlling the (reset active LOW) RESET# pin. The active polarity of the GPIO must translate to the low...; maxItems 1.
- Pattern child/property schemas: `^(.+-hog(-[0-9]+)?)$`.
- Uses top-level `allOf` with 2 branch(es) for variant-specific validation.
- Nested conditional keywords present: `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `reset-gpios`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Large compatible matrices make fallback ordering and per-device exception branches easy to regress when adding variants.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/nxp,pcf8575.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `maxim,max7328`, `maxim,max7329`, `nxp,pca8574`, `nxp,pca8575`, `nxp,pca9670`, `nxp,pca9671`, ....
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/nxp,pcf8575.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/pin-control-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/pin-control-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Pin control based generic GPIO controller. The pin control-based GPIO will facilitate a pin controller's ability to drive electric lines high/low and other generic properties of a pin controller to perform general-purpose one-bit binary I/O.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/pin-control-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Pin control based generic GPIO controller`.
- Top-level required properties: `compatible`, `gpio-controller`, `#gpio-cells`, `gpio-ranges`, `ngpios`.
- `compatible`: const `scmi-pinctrl-gpio`.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `gpio-line-names` is accepted as a flag/property marker.
- `gpio-ranges` is accepted as a flag/property marker.
- `ngpios` is accepted as a flag/property marker.
- Pattern child/property schemas: `^.+-hog(-[0-9]+)?$`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/pin-control-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/pin-control-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/pisosr-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/pisosr-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Generic Parallel-in/Serial-out Shift Register GPIO Driver. This binding describes generic parallel-in/serial-out shift register devices that can be used for GPI (General Purpose Input). This includes SN74165 serial-out shift registers and the SN65HVS88x series of industrial serializers.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/pisosr-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Generic Parallel-in/Serial-out Shift Register GPIO Driver`.
- Top-level required properties: `compatible`, `gpio-controller`, `#gpio-cells`.
- `compatible`: enum `pisosr-gpio`.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `ngpios`: constraints via maximum, default.
- `load-gpios`: GPIO pin specifier attached to load enable, this pin is pulsed before reading from the device to load input pin....
- `spi-cpol` is accepted as a flag/property marker.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `/schemas/spi/spi-peripheral-props.yaml#`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/pisosr-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/pisosr-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/pl061-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/pl061-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for ARM PL061 GPIO controller. ARM PL061 GPIO controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/pl061-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `ARM PL061 GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `arm,pl061`, `arm,primecell`.
- Top-level required properties: `compatible`, `reg`, `clocks`, `#gpio-cells`, `gpio-controller`.
- `$nodename`: pattern `^gpio@[0-9a-f]+$`.
- `compatible`: 2 ordered items.
- `reg`: maxItems 1.
- `interrupts`: constraints via oneOf.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `clocks`: maxItems 1.
- `clock-names` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-line-names` is accepted as a flag/property marker.
- `gpio-ranges`: maxItems 8; minItems 1.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `clock-names`.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/pl061-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- Board DTS coverage should exercise representative compatible values: `arm,pl061`, `arm,primecell`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/pl061-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/qca,ar7100-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/qca,ar7100-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Qualcomm Atheros AR7xxx/AR9xxx GPIO controller. Qualcomm Atheros AR7xxx/AR9xxx GPIO controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/qca,ar7100-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Qualcomm Atheros AR7xxx/AR9xxx GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `qca,ar9132-gpio`, `qca,ar7100-gpio`, `qca,ar9340-gpio`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `ngpios`.
- `compatible`: constraints via oneOf.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `ngpios` is accepted as a flag/property marker.
- `interrupts`: maxItems 1.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/qca,ar7100-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `qca,ar9132-gpio`, `qca,ar7100-gpio`, `qca,ar9340-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/qca,ar7100-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/qcom,wcd934x-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/qcom,wcd934x-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for WCD9340/WCD9341 GPIO controller. Qualcomm Technologies Inc WCD9340/WCD9341 Audio Codec has integrated gpio controller to control 5 gpios on the chip.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/qcom,wcd934x-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `WCD9340/WCD9341 GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `qcom,wcd9340-gpio`, `qcom,wcd9341-gpio`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`.
- `compatible`: enum `qcom,wcd9340-gpio`, `qcom,wcd9341-gpio`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/qcom,wcd934x-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `qcom,wcd9340-gpio`, `qcom,wcd9341-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/qcom,wcd934x-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/realtek,otto-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/realtek,otto-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Realtek Otto GPIO controller. Realtek's GPIO controller on their MIPS switch SoCs (Otto platform) consists of two banks of 32 GPIOs. These GPIOs can generate edge-triggered interrupts. Each bank's interrupts are cascased into one interrupt line on the parent interrupt controller, if provided. This binding allows defining a single bank in the devicetree. The interrupt controller is not supported on the fallback compatible name, which only allows for GPIO port use.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/realtek,otto-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Realtek Otto GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `realtek,rtl8380-gpio`, `realtek,rtl8390-gpio`, `realtek,rtl9300-gpio`, `realtek,rtl9310-gpio`, `realtek,rtl9607-gpio`, `realtek,otto-gpio`.
- Top-level required properties: `compatible`, `reg`, `#gpio-cells`, `gpio-controller`.
- `$nodename`: pattern `^gpio@[0-9a-f]+$`.
- `compatible`: 2 ordered items.
- `reg` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `ngpios`: constraints via minimum, maximum.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `interrupts`: maxItems 1.
- Nested conditional keywords present: `else`, `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 2 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/realtek,otto-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `realtek,rtl8380-gpio`, `realtek,rtl8390-gpio`, `realtek,rtl9300-gpio`, `realtek,rtl9310-gpio`, `realtek,rtl9607-gpio`, `realtek,otto-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/realtek,otto-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/realtek,rtd-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/realtek,rtd-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Realtek DHC GPIO controller. The GPIO controller is designed for the Realtek DHC (Digital Home Center) RTD series SoC family, which are high-definition media processor SoCs.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/realtek,rtd-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Realtek DHC GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `realtek,rtd1295-misc-gpio`, `realtek,rtd1295-iso-gpio`, `realtek,rtd1315e-iso-gpio`, `realtek,rtd1319-iso-gpio`, `realtek,rtd1319d-iso-gpio`, `realtek,rtd1395-iso-gpio`, `realtek,rtd1619-iso-gpio`, `realtek,rtd1619b-iso-gpio`.
- Top-level required properties: `compatible`, `reg`, `interrupts`, `gpio-ranges`, `gpio-controller`, `#gpio-cells`.
- `compatible`: enum `realtek,rtd1295-misc-gpio`, `realtek,rtd1295-iso-gpio`, `realtek,rtd1315e-iso-gpio`, `realtek,rtd1319-iso-gpio`, `realtek,rtd1319d-iso-gpio`, `realtek,rtd1395-iso-gpio`, `realtek,rtd1619-iso-gpio`, `realtek,rtd1619b-iso-gpio`.
- `reg`: 2 ordered items.
- `interrupts`: 2 ordered items.
- `gpio-ranges` is accepted as a flag/property marker.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/realtek,rtd-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `realtek,rtd1295-misc-gpio`, `realtek,rtd1295-iso-gpio`, `realtek,rtd1315e-iso-gpio`, `realtek,rtd1319-iso-gpio`, `realtek,rtd1319d-iso-gpio`, `realtek,rtd1395-iso-gpio`, ....
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/realtek,rtd-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/renesas,em-gio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/renesas,em-gio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Renesas EMMA Mobile General Purpose I/O Interface. Renesas EMMA Mobile General Purpose I/O Interface

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/renesas,em-gio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Renesas EMMA Mobile General Purpose I/O Interface`.
- Compatible strings or compatible constants enumerated by the schema include `renesas,em-gio`.
- Top-level required properties: `compatible`, `reg`, `interrupts`, `gpio-controller`, `#gpio-cells`, `gpio-ranges`, `ngpios`, `interrupt-controller`, `#interrupt-cells`.
- `compatible`: const `renesas,em-gio`.
- `reg`: 2 ordered items.
- `interrupts`: 2 ordered items.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `gpio-ranges`: maxItems 1.
- `ngpios`: constraints via minimum, maximum.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/renesas,em-gio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `renesas,em-gio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/renesas,em-gio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/renesas,rcar-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/renesas,rcar-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Renesas R-Car General-Purpose Input/Output Ports (GPIO). Renesas R-Car General-Purpose Input/Output Ports (GPIO)

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/renesas,rcar-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Renesas R-Car General-Purpose Input/Output Ports (GPIO)`.
- Compatible strings or compatible constants enumerated by the schema include `renesas,gpio-r8a7778`, `renesas,gpio-r8a7779`, `renesas,rcar-gen1-gpio`, `renesas,gpio-r8a7742`, `renesas,gpio-r8a7743`, `renesas,gpio-r8a7744`, `renesas,gpio-r8a7745`, `renesas,gpio-r8a77470`, `renesas,gpio-r8a7790`, `renesas,gpio-r8a7791`, `renesas,gpio-r8a7792`, `renesas,gpio-r8a7793`, ....
- Top-level required properties: `compatible`, `reg`, `interrupts`, `gpio-controller`, `#gpio-cells`, `gpio-ranges`, `interrupt-controller`, `#interrupt-cells`.
- `compatible`: constraints via oneOf.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `clocks`: maxItems 1.
- `power-domains`: maxItems 1.
- `resets`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `gpio-ranges`: maxItems 1.
- `gpio-reserved-ranges`: maxItems 8; minItems 1.
- Pattern child/property schemas: `^.*$`.
- Nested conditional keywords present: `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `resets`.
- Integrates with provider/consumer property `power-domains`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Large compatible matrices make fallback ordering and per-device exception branches easy to regress when adding variants.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/renesas,rcar-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `renesas,gpio-r8a7778`, `renesas,gpio-r8a7779`, `renesas,rcar-gen1-gpio`, `renesas,gpio-r8a7742`, `renesas,gpio-r8a7743`, `renesas,gpio-r8a7744`, ....
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/renesas,rcar-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/rockchip,gpio-bank.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/rockchip,gpio-bank.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Rockchip GPIO bank. Rockchip GPIO bank

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/rockchip,gpio-bank.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Rockchip GPIO bank`.
- Compatible strings or compatible constants enumerated by the schema include `rockchip,gpio-bank`, `rockchip,rk3188-gpio-bank0`.
- Top-level required properties: `compatible`, `reg`, `interrupts`, `clocks`, `gpio-controller`, `#gpio-cells`, `interrupt-controller`, `#interrupt-cells`.
- `compatible`: enum `rockchip,gpio-bank`, `rockchip,rk3188-gpio-bank0`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `clocks`: minItems 1; 2 ordered items.
- `gpio-ranges` is accepted as a flag/property marker.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-line-names` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `power-domains`: maxItems 1.
- Pattern child/property schemas: `^.+-hog(-[0-9]+)?$`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `power-domains`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/rockchip,gpio-bank.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `rockchip,gpio-bank`, `rockchip,rk3188-gpio-bank0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/rockchip,gpio-bank.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/sifive,gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/sifive,gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for SiFive GPIO controller. SiFive GPIO controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/sifive,gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `SiFive GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `sifive,fu540-c000-gpio`, `sifive,fu740-c000-gpio`, `canaan,k210-gpiohs`, `sifive,gpio0`.
- Top-level required properties: `compatible`, `reg`, `interrupts`, `interrupt-controller`, `#interrupt-cells`, `#gpio-cells`, `gpio-controller`.
- `compatible`: 2 ordered items.
- `reg`: maxItems 1.
- `interrupts`: Interrupt mapping, one per GPIO. Maximum 32 GPIOs.; maxItems 32; minItems 1.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `clocks`: maxItems 1.
- `#gpio-cells`: const `2`.
- `ngpios`: The number of GPIOs available on the controller implementation. It is 16 for the SiFive SoCs and 32 for the Canaan....
- `gpio-line-names`: maxItems 32; minItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- Nested conditional keywords present: `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/sifive,gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `sifive,fu540-c000-gpio`, `sifive,fu740-c000-gpio`, `canaan,k210-gpiohs`, `sifive,gpio0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/sifive,gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/snps,dw-apb-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/snps,dw-apb-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Synopsys DesignWare APB GPIO controller. Synopsys DesignWare GPIO controllers have a configurable number of ports, each of which are intended to be represented as child nodes with the generic GPIO-controller properties as described in this bindings file.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/snps,dw-apb-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Synopsys DesignWare APB GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `snps,dw-apb-gpio`.
- Top-level required properties: `compatible`, `reg`, `#address-cells`, `#size-cells`.
- `$nodename`: pattern `^gpio@[0-9a-f]+$`.
- `compatible`: const `snps,dw-apb-gpio`.
- `#address-cells`: const `1`.
- `#size-cells`: const `0`.
- `reg`: maxItems 1.
- `clocks`: minItems 1; 2 ordered items.
- `clock-names`: minItems 1; 2 ordered items.
- `resets`: maxItems 1.
- Pattern child/property schemas: `^gpio-(port|controller)@[0-9a-f]+$`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `clock-names`.
- Integrates with provider/consumer property `resets`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/snps,dw-apb-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `snps,dw-apb-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/snps,dw-apb-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/socionext,uniphier-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/socionext,uniphier-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for UniPhier GPIO controller. UniPhier GPIO controller

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/socionext,uniphier-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `UniPhier GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `socionext,uniphier-gpio`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `interrupt-controller`, `#interrupt-cells`, `ngpios`, `gpio-ranges`, `socionext,interrupt-ranges`.
- `$nodename`: pattern `^gpio@[0-9a-f]+$`.
- `compatible`: const `socionext,uniphier-gpio`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: The first cell defines the interrupt number. The second cell bits[3:0] is used to specify trigger type as follows:...; const `2`.
- `ngpios`: constraints via minimum, maximum.
- `gpio-ranges` is accepted as a flag/property marker.
- `gpio-ranges-group-names` is accepted as a flag/property marker.
- `socionext,interrupt-ranges`: Specifies an interrupt number mapping between this GPIO controller and its interrupt parent, in the form of...; ref `/schemas/types.yaml#/definitions/uint32-matrix`.
- Pattern child/property schemas: `^.+-hog(-[0-9]+)?$`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32-matrix`.
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/socionext,uniphier-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `socionext,uniphier-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/socionext,uniphier-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/spacemit,k1-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/spacemit,k1-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for SpacemiT K1 GPIO controller. The controller's registers are organized as sets of eight 32-bit registers with each set of port controlling 32 pins. A single interrupt line is shared for all of the pins by the controller.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/spacemit,k1-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `SpacemiT K1 GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `spacemit,k1-gpio`, `spacemit,k3-gpio`.
- Top-level required properties: `compatible`, `reg`, `clocks`, `clock-names`, `gpio-controller`, `#gpio-cells`, `interrupts`, `interrupt-controller`, `#interrupt-cells`, `gpio-ranges`.
- `$nodename`: pattern `^gpio@[0-9a-f]+$`.
- `compatible`: enum `spacemit,k1-gpio`, `spacemit,k3-gpio`.
- `reg`: maxItems 1.
- `clocks`: 2 ordered items.
- `clock-names`: 2 ordered items.
- `resets`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: The first two cells are the GPIO bank index and offset inside the bank, the third cell should specify GPIO flag.; const `3`.
- `gpio-ranges` is accepted as a flag/property marker.
- `interrupts`: maxItems 1.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: The first two cells are the GPIO bank index and offset inside the bank, the third cell should specify interrupt...; const `3`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `clock-names`.
- Integrates with provider/consumer property `resets`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/spacemit,k1-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `spacemit,k1-gpio`, `spacemit,k3-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/spacemit,k1-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/sprd,gpio-eic.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/sprd,gpio-eic.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Unisoc EIC controller. The EIC is the abbreviation of external interrupt controller, which can be used only in input mode. The Spreadtrum platform has 2 EIC controllers, one is in digital chip, and another one is in PMIC. The digital chip EIC controller contains 4 sub-modules, i.e. EIC-debounce, EIC-latch, EIC-async and EIC-sync. But the PMIC EIC controller contains only one EIC-debounce sub- module. The EIC-debounce sub-module provides up to 8 source input signal connections. A debounce mechanism is used to capture the input signals'.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/sprd,gpio-eic.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Unisoc EIC controller`.
- Compatible strings or compatible constants enumerated by the schema include `sprd,sc9860-eic-debounce`, `sprd,sc9860-eic-latch`, `sprd,sc9860-eic-async`, `sprd,sc9860-eic-sync`, `sprd,sc2731-eic`, `sprd,ums512-eic-debounce`, `sprd,ums512-eic-latch`, `sprd,ums512-eic-async`, `sprd,ums512-eic-sync`, `sprd,sc2730-eic`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `interrupt-controller`, `#interrupt-cells`, `interrupts`.
- `compatible`: constraints via oneOf.
- `reg`: EIC controller can support maximum 3 banks which has its own address base.; maxItems 3; minItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `interrupts`: The interrupt shared by all GPIO lines for this controller.; maxItems 1.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/sprd,gpio-eic.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `sprd,sc9860-eic-debounce`, `sprd,sc9860-eic-latch`, `sprd,sc9860-eic-async`, `sprd,sc9860-eic-sync`, `sprd,sc2731-eic`, `sprd,ums512-eic-debounce`, ....
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/sprd,gpio-eic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/sprd,gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/sprd,gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Unisoc GPIO controller. The controller's registers are organized as sets of sixteen 16-bit registers with each set controlling a bank of up to 16 pins. A single interrupt is shared for all of the banks handled by the controller.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/sprd,gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Unisoc GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `sprd,sc9860-gpio`, `sprd,ums512-gpio`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `interrupt-controller`, `#interrupt-cells`, `interrupts`.
- `compatible`: constraints via oneOf.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `interrupts`: The interrupt shared by all GPIO lines for this controller.; maxItems 1.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/sprd,gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `sprd,sc9860-gpio`, `sprd,ums512-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/sprd,gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/st,nomadik-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/st,nomadik-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Nomadik GPIO controller. The Nomadik GPIO driver handles Nomadik SoC GPIO blocks. This block has also been called ST STA2X11. On the Nomadik platform, this driver is intertwined with pinctrl-nomadik.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/st,nomadik-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Nomadik GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `st,nomadik-gpio`, `mobileye,eyeq5-gpio`.
- Top-level required properties: `compatible`, `reg`, `interrupts`, `#gpio-cells`, `gpio-controller`, `interrupt-controller`, `gpio-bank`.
- `$nodename`: pattern `^gpio@[0-9a-f]+$`.
- `compatible`: enum `st,nomadik-gpio`, `mobileye,eyeq5-gpio`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `#gpio-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `gpio-bank`: System-wide GPIO bank index.; ref `/schemas/types.yaml#/definitions/uint32`.
- `st,supports-sleepmode`: Whether the controller can sleep or not.; ref `/schemas/types.yaml#/definitions/flag`.
- `clocks`: maxItems 1.
- `gpio-ranges`: maxItems 1.
- `ngpios`: constraints via minimum, maximum.
- `resets`: maxItems 1.
- Uses top-level `allOf` with 1 branch(es) for variant-specific validation.
- Nested conditional keywords present: `if`, `then`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.
- Branch evaluation is part of the control path: properties and compatible strings select whether variant-specific requirements or forbiddance rules apply.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `unevaluatedProperties` is `False`, allowing shared `$ref` schemas to consume common properties before closing validation.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/flag`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Integrates with provider/consumer property `clocks`.
- Integrates with provider/consumer property `resets`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Conditional schema branches are high-risk: a valid property for one compatible may be forbidden or required for another.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/st,nomadik-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `st,nomadik-gpio`, `mobileye,eyeq5-gpio`.
- Negative validation is valuable for each conditional branch: missing required fields, forbidden properties, and wrong fallback-compatible ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/st,nomadik-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/st,spear-spics-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/st,spear-spics-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for ST Microelectronics SPEAr SPI CS GPIO Controller. SPEAr platform provides a provision to control chipselects of ARM PL022 Prime Cell spi controller through its system registers, which otherwise remains under PL022 control. If chipselect remain under PL022 control then they would be released as soon as transfer is over and TxFIFO becomes empty. This is not desired by some of the device protocols above spi which expect (multiple) transfers without releasing their chipselects. Chipselects can be controlled by software by turning them as GPIOs. SPEAr provides another.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/st,spear-spics-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `ST Microelectronics SPEAr SPI CS GPIO Controller`.
- Compatible strings or compatible constants enumerated by the schema include `st,spear-spics-gpio`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `st-spics,peripcfg-reg`, `st-spics,sw-enable-bit`, `st-spics,cs-value-bit`, `st-spics,cs-enable-mask`, `st-spics,cs-enable-shift`.
- `compatible`: const `st,spear-spics-gpio`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `st-spics,peripcfg-reg`: Offset of the peripcfg register.; ref `/schemas/types.yaml#/definitions/uint32`.
- `st-spics,sw-enable-bit`: Bit offset to enable software chipselect control.; ref `/schemas/types.yaml#/definitions/uint32`.
- `st-spics,cs-value-bit`: Bit offset to drive chipselect low or high.; ref `/schemas/types.yaml#/definitions/uint32`.
- `st-spics,cs-enable-mask`: Bitmask selecting which chipselects to enable.; ref `/schemas/types.yaml#/definitions/uint32`.
- `st-spics,cs-enable-shift`: Bit shift for programming chipselect number.; ref `/schemas/types.yaml#/definitions/uint32`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32`.
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/st,spear-spics-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `st,spear-spics-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/st,spear-spics-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/st,stmpe-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/st,stmpe-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for STMicroelectonics Port Expander (STMPE) GPIO Block. STMicroelectronics Port Expander (STMPE) is a series of slow bus controllers for various expanded peripherals such as GPIO, keypad, touchscreen, ADC, PWM or rotator. It can contain one or several different peripherals connected to SPI or I2C. These bindings pertain to the GPIO portions of these expanders.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/st,stmpe-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `STMicroelectonics Port Expander (STMPE) GPIO Block`.
- Compatible strings or compatible constants enumerated by the schema include `st,stmpe-gpio`.
- Top-level required properties: `compatible`, `#gpio-cells`, `#interrupt-cells`, `gpio-controller`, `interrupt-controller`.
- `compatible`: const `st,stmpe-gpio`.
- `#gpio-cells`: const `2`.
- `#interrupt-cells`: const `2`.
- `gpio-controller` is accepted as a flag/property marker.
- `gpio-line-names`: maxItems 24; minItems 1.
- `interrupt-controller` is accepted as a flag/property marker.
- `st,norequest-mask`: A bitmask of GPIO lines that cannot be requested because for for example not being connected to anything on the...; ref `/schemas/types.yaml#/definitions/uint32`.
- Pattern child/property schemas: `^.+-hog(-[0-9]+)?$`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/uint32`.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/st,stmpe-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- Board DTS coverage should exercise representative compatible values: `st,stmpe-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/st,stmpe-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/ti,keystone-dsp-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/ti,keystone-dsp-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for Keystone 2 DSP GPIO controller. HOST OS userland running on ARM can send interrupts to DSP cores using the DSP GPIO controller IP. It provides 28 IRQ signals per each DSP core. This is one of the component used by the IPC mechanism used on Keystone SOCs. For example TCI6638K2K SoC has 8 DSP GPIO controllers: - 8 for C66x CorePacx CPUs 0-7 Keystone 2 DSP GPIO controller has specific features: - each GPIO can be configured only as output pin; - setting GPIO value to 1 causes IRQ generation on target DSP core; - reading pin value returns 0 - if IRQ.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/ti,keystone-dsp-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `Keystone 2 DSP GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `ti,keystone-dsp-gpio`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `gpio,syscon-dev`.
- `compatible`: const `ti,keystone-dsp-gpio`.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `gpio,syscon-dev`: Phandle and offset of device's specific registers within the syscon state control registers; 1 ordered items; ref `/schemas/types.yaml#/definitions/phandle-array`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/phandle-array`.
- Integrates with provider/consumer property `reg`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/ti,keystone-dsp-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `ti,keystone-dsp-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/ti,keystone-dsp-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/ti,omap-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/ti,omap-gpio.yaml

## Purpose
This YAML binding defines the Device Tree contract for the GPIO controller, expander, or consumer binding for OMAP GPIO controller. The general-purpose interface combines general-purpose input/output (GPIO) banks. Each GPIO banks provides up to 32 dedicated general-purpose pins with input and output capabilities; interrupt generation in active mode and wake-up request generation in idle mode upon the detection of external events.

## Important APIs/types/functions
- `$id` is `http://devicetree.org/schemas/gpio/ti,omap-gpio.yaml#` and `$schema` is `http://devicetree.org/meta-schemas/core.yaml#`, so the file participates in dt-schema validation rather than runtime code execution.
- `title` is `OMAP GPIO controller`.
- Compatible strings or compatible constants enumerated by the schema include `ti,omap2-gpio`, `ti,omap3-gpio`, `ti,omap4-gpio`, `ti,am4372-gpio`.
- Top-level required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `interrupt-controller`, `#interrupt-cells`, `interrupts`.
- `compatible`: constraints via oneOf.
- `reg`: maxItems 1.
- `gpio-controller` is accepted as a flag/property marker.
- `#gpio-cells`: const `2`.
- `interrupt-controller` is accepted as a flag/property marker.
- `#interrupt-cells`: const `2`.
- `interrupts`: maxItems 1.
- `gpio-ranges` is accepted as a flag/property marker.
- `gpio-line-names`: maxItems 32; minItems 1.
- `ti,gpio-always-on`: Indicates if a GPIO bank is always powered and will never lose its logic state.; ref `/schemas/types.yaml#/definitions/flag`.
- `ti,hwmods`: Name of the hwmod associated with the GPIO. Needed on some legacy OMAP SoCs which have not been converted to the...; ref `/schemas/types.yaml#/definitions/string`.
- `ti,no-reset-on-init`: Do not reset on init. Used with ti,hwmods on some legacy OMAP SoCs which have not been converted to the ti,sysc...; ref `/schemas/types.yaml#/definitions/flag`.
- Pattern child/property schemas: `^(.+-hog(-[0-9]+)?)$`.

## Control flow
- There is no executable control flow in this file; validation flow is driven by dt-schema loading the YAML, matching DTS nodes by `compatible` and `$nodename` constraints, then applying shared refs and local branches.
- dt-schema checks GPIO controller shape, interrupt-controller declarations, `#gpio-cells`, optional hog children, and bus resources before the kernel GPIO driver binds from `compatible`.
- Runtime use usually flows through gpiolib and, when interrupt properties are present, irqdomain setup for line-to-IRQ translation.
- Referenced shared schemas extend validation rather than adding executable code here, so failures typically surface as dtbs_check errors before runtime.

## State and persistence behavior
- Persistent data is limited to DT properties such as line counts, names, reset/power wiring, interrupt wiring, and gpio-hog defaults; mutable pin state is owned by gpiolib and the hardware driver.
- `additionalProperties` is `False`, so the node is closed to keep DTS nodes tight.

## Dependencies and integration points
- References shared schemas: `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/string`.
- Integrates with provider/consumer property `reg`.
- Integrates with provider/consumer property `interrupts`.
- Includes 1 DTS example block(s) that act as practical integration templates.

## Risks and edge cases
- Closed-property validation can reject board DTS files that carry undocumented vendor extensions or legacy names.
- Interrupt-controller mode must match interrupt cell count and parent wiring, or probe-time IRQ mapping will fail despite basic GPIO validation.
- GPIO cell count and line naming/count constraints need to track the hardware driver, otherwise consumers can encode wrong specifiers.

## Test signals
- Primary signal is `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/ti,omap-gpio.yaml` plus `make dtbs_check` on boards using the compatible strings.
- The embedded example(s) should compile under dt_binding_check and cover required provider phandles, cells, and child-node shape.
- Board DTS coverage should exercise representative compatible values: `ti,omap2-gpio`, `ti,omap3-gpio`, `ti,omap4-gpio`, `ti,am4372-gpio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/ti,omap-gpio.yaml -->
