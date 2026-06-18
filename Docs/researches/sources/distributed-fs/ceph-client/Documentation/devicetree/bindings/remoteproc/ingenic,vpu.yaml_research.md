<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/remoteproc/ingenic,vpu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/remoteproc/ingenic,vpu.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/remoteproc/ingenic,vpu.yaml` defines the Linux devicetree remoteproc binding titled `Ingenic Video Processing Unit`. Inside the Video Processing Unit (VPU) of the recent JZ47xx SoCs from Ingenic is a second Xburst MIPS CPU very similar to the main core. It is consumed by dt-schema tooling to constrain source DTS and compiled DTB nodes before Linux drivers bind to the hardware.

## Important APIs, Types, and Functions
This YAML exports devicetree ABI rather than callable functions. `compatible` uses a single `const` token with 1 token: `ingenic,jz4770-vpu-rproc`. Top-level properties are `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `interrupts`. Required top-level properties are `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `interrupts`. Nested required keys observed across child/conditional schemas include `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `interrupts`. Important local constraints: non-compatible enum/const values `aux`, `tcsm0`, `tcsm1`, `sram`, `vpu`. The primary contract surface is compatible strings, reserved-memory links, firmware-name policy, interrupt and interrupt-name order, clocks/resets, power-domain naming, mailbox or SMEM state phandles, qcom-specific IDs, and child communication edge schemas.

## Control Flow
Control flow is declarative validation. `dt_binding_check` loads the YAML, validates examples, follows `$ref` links, applies required-property checks, array sizes, constants/enums, and any composed conditions, then descends into pattern-matched child nodes before enforcing schema closure. `dtbs_check` applies the same contract to real compiled DTS nodes selected by compatible strings or parent schemas. Runtime control flow begins outside this file: the Linux device core matches the node to drivers/remoteproc and rpmsg transport drivers, acquires the declared resources, and then creates regulator or remoteproc runtime objects as appropriate.

## State and Persistence Behavior
The binding itself has no mutable state and performs no persistence. Its persistent behavior is the DT ABI: property names, compatible/fallback ordering, child-node names, interrupt-name order, supply names, and address-cell layout are compiled into DTBs and must remain stable for old boards. Runtime state is external and owned by the matched kernel driver after probe, including remote processor boot/stop state, firmware image selection, reserved-memory ownership, interrupt-driven crash/ready/handover events, power-domain votes, and rpmsg channel registration.

## Dependencies and Integration Points
Maintainers listed in the schema: Paul Cercueil <paul@crapouillou.net>. Referenced schemas are dt-schema core/meta schemas only. Integration points include the Linux remoteproc core, Qualcomm/SoC-specific PIL/PAS/SCM loaders, reserved-memory carveouts, mailbox or smem/smp2p signaling, clocks, resets, regulators, power domains, and rpmsg/GLINK/SMD child transports. The file also integrates with example extraction, Linux `make dt_binding_check`, `make dtbs_check`, driver `of_match_table` review, and board DTS files using the compatible strings or common fragment.

## Risks
Primary risks are ABI drift in compatible strings, reserved-memory links, firmware-name policy, interrupt and interrupt-name order, clocks/resets, power-domain naming, mailbox or SMEM state phandles, qcom-specific IDs, and child communication edge schemas, a compatible string accepted by schema but missing in the driver match table, or vice versa, resource ordering mistakes in `reg`, `interrupts`, `clock-names`, `reset-names`, or `power-domain-names`, reserved-memory or firmware-name mismatches that make remote firmware boot fail late in probe, interrupt-name or SMEM/GLINK/SMD edge mistakes that break crash, ready, stop, or rpmsg signaling. This schema uses `additionalProperties: false`. Regressions usually show up as schema failures during DT validation, boot-time probe errors, missing regulators/remote processors, failed child-device creation, or subtly wrong power/firmware sequencing on affected boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/remoteproc/ingenic,vpu.yaml` and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/remoteproc/ingenic,vpu.yaml` against boards that instantiate the binding. The file includes 1 embedded example, so example extraction is a direct smoke test. Compare compatible strings and required resources with drivers/remoteproc and rpmsg transport drivers, check all referenced common schemas, and review probe logs for successful resource acquisition and expected child-device or channel registration.

Source read size: 77 lines, 1693 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/remoteproc/ingenic,vpu.yaml -->
