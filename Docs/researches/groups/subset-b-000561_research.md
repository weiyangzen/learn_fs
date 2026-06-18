# subset-b-000561 research

Grouped research report for ARM devicetree binding schemas under `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm`. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/hi6220-domain-ctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/hi6220-domain-ctrl.yaml

## Purpose
This schema documents the HiSilicon Hi6220 always-on, media, and power-management domain controller register blocks. These nodes are `syscon` providers that expose clocks and, optionally, reset lines to other DT consumers.

## Important APIs, Types, And Functions
The binding surface is the `compatible` tuple, `reg`, `#clock-cells`, and optional `#reset-cells`. The first compatible selects `hisilicon,hi6220-aoctrl`, `hisilicon,hi6220-mediactrl`, or `hisilicon,hi6220-pmctrl`; the second must be `syscon`.

## Control Flow
Validation requires the compatible tuple, one register range, and clock provider cells. `additionalProperties: false` rejects undeclared properties, so consumers must use standard clock/reset/syscon links rather than ad hoc fields.

## State And Persistence
The schema has no runtime state. It describes persistent MMIO control registers used by kernel syscon, clock, and reset drivers after boot.

## Dependencies And Integration Points
It depends on the core devicetree meta-schema and integrates with Linux `syscon`, clock provider, and reset-controller lookups for Hi6220 platform drivers.

## Risks
The main risk is an incorrect compatible order or missing `syscon`, which prevents shared register access. Missing `#clock-cells` breaks clock phandle consumers; over-declaring reset cells on blocks without resets can mislead drivers.

## Test Signals
`make dt_binding_check` validates the examples and schema shape. `make dtbs_check` on Hi6220 DTS files confirms compatible ordering, register ranges, and clock/reset cell usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/hi6220-domain-ctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/hip04-bootwrapper.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/hip04-bootwrapper.yaml

## Purpose
This binding describes the HiSilicon HiP04 bootwrapper SMP boot method. It records the physical bootwrapper and optional relocation areas used by platform code to release secondary CPUs.

## Important APIs, Types, And Functions
The schema exposes `compatible = "hisilicon,hip04-bootwrapper"` and `boot-method`, a uint32 array with two to four cells: bootwrapper physical address, bootwrapper size, relocation physical address, and relocation size.

## Control Flow
Validation requires both properties and constrains `boot-method` with `minItems: 2` and `maxItems: 4`. There are no child nodes or fallback compatibles.

## State And Persistence
The DT node persists boot protocol addresses. Runtime state is held by firmware/platform code that copies or jumps through the described regions.

## Dependencies And Integration Points
It depends on `/schemas/types.yaml` for uint32-array validation and integrates with HiP04 SMP bring-up code that interprets the boot method.

## Risks
Bad physical addresses or sizes can make secondary CPU startup fail very early. Because the property is a positional array, element order is a high-risk contract.

## Test Signals
`dt_binding_check` catches array length and type errors; boot testing on HiP04 systems is the real signal for address correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/hip04-bootwrapper.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/hip04-fabric.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/hip04-fabric.yaml

## Purpose
This schema describes the HiSilicon HiP04 fabric controller MMIO block, a platform control block involved in SoC fabric configuration.

## Important APIs, Types, And Functions
The binding surface is intentionally small: `compatible = "hisilicon,hip04-fabric"` and a single `reg` resource.

## Control Flow
The schema requires both properties and rejects extras with `additionalProperties: false`, so validation is a direct fixed-shape check.

## State And Persistence
The DT node describes persistent hardware registers. No schema-level state is created; runtime state belongs to platform controller code that maps the region.

## Dependencies And Integration Points
It depends only on the core schema and integrates with HiP04 platform initialization code using the compatible string and MMIO range.

## Risks
The risk surface is mostly address accuracy. An incorrect `reg` range can map the wrong fabric registers, and extra undocumented properties will fail schema validation.

## Test Signals
`dt_binding_check` validates the schema; `dtbs_check` for HiP04 board DTS files catches missing or malformed fabric controller nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/hip04-fabric.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/pctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/pctrl.yaml

## Purpose
This binding documents HiSilicon peripheral miscellaneous control registers, represented as a small MMIO controller node.

## Important APIs, Types, And Functions
The valid schema API is `compatible = "hisilicon,pctrl"` plus one `reg` range. The included example shows `pctrl@fca09000`.

## Control Flow
Validation requires both `compatible` and `reg`, with `reg` limited to one item and no additional properties allowed.

## State And Persistence
The node has no independent runtime state. It describes persistent peripheral control registers that platform or pin/control drivers can map.

## Dependencies And Integration Points
It depends on the core DT schema and integrates with HiSilicon board DTS files and any driver matching `hisilicon,pctrl`.

## Risks
Wrong MMIO range or node placement can break peripheral setup. Because `additionalProperties` is false, future extensions must update the schema before DTS properties are added.

## Test Signals
Binding examples and affected DTS files should pass `dt_binding_check` and `dtbs_check`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/pctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/sysctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/sysctrl.yaml

## Purpose
This schema covers multiple HiSilicon system controller variants used for slave-core startup, reboot, clocks, resets, and related SoC control functions.

## Important APIs, Types, And Functions
It validates two compatible styles: generic/Hi6220/Hi3519 controllers followed by `syscon`, and HiP01 as `hisilicon,hip01-sysctrl`, `hisilicon,sysctrl`. Important properties include `reg`, `smp-offset`, `resume-offset`, `reboot-offset`, `#clock-cells`, `#reset-cells`, address/size cells, `ranges`, and `clock@` child nodes for `hisilicon,hi3620-clock` or `hisilicon,hi3620-mmc-clock`.

## Control Flow
An `allOf` conditional requires `#clock-cells` when `compatible` contains `hisilicon,hi6220-sysctrl`. `patternProperties` validates `clock@` children, while `additionalProperties` allows other child objects for controller subfunctions.

## State And Persistence
The binding describes persistent sysctrl registers and child clock register windows. Runtime state lives in syscon, reboot, SMP, clock, and reset drivers that use the offsets and child nodes.

## Dependencies And Integration Points
It integrates with Linux syscon, clock providers, reset providers, SMP boot code, and reboot paths. It depends on type definitions for uint32 offsets and on standard bus child-node conventions.

## Risks
Offset mistakes can affect CPU bring-up, resume, or reboot. The Hi6220 conditional is a compatibility trap: missing `#clock-cells` breaks clock consumers even if basic syscon probing succeeds.

## Test Signals
`dt_binding_check` exercises conditionals and examples. `dtbs_check`, SMP boot, suspend/resume, reboot, and clock consumer probing are practical signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/sysctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/hisilicon.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/hisilicon.yaml

## Purpose
This root-node platform schema catalogs supported HiSilicon boards and SoCs, including Hi3660/Hi3670 Hikey boards, Poplar, Hi6220 Hikey, HiP server boards, and SD5203.

## Important APIs, Types, And Functions
The binding constrains the root `$nodename` to `/` and validates `compatible` with `oneOf` board-to-SoC fallback lists such as `hisilicon,hi3660-hikey960`, `hisilicon,hi3660` and `hisilicon,hi6220-hikey`, `hisilicon,hi6220`.

## Control Flow
dt-schema selects exactly one `oneOf` compatible sequence. The exact item order matters because the first string identifies the board and later strings identify the SoC family.

## State And Persistence
The schema carries immutable platform identity in the DTB. It does not describe mutable state or persistence beyond the root compatible string.

## Dependencies And Integration Points
It depends on the core schema and integrates with board matching, machine selection, quirks, and SoC-level driver probing.

## Risks
Adding a board under the wrong SoC fallback can route platform code to incorrect quirks. `additionalProperties: true` intentionally leaves normal root properties to other schemas, so this file only catches compatible-list shape.

## Test Signals
`dtbs_check` on HiSilicon DTBs confirms root compatible ordering. Board boot logs and platform driver matches provide runtime confirmation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/hisilicon.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/low-pin-count.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/low-pin-count.yaml

## Purpose
This schema describes the HiSilicon HiP06/HiP07 Low Pin Count controller, which provides non-CPU-addressed LPC I/O access to legacy ISA devices.

## Important APIs, Types, And Functions
It requires an `isa@...` node name, `compatible` of `hisilicon,hip06-lpc` or `hisilicon,hip07-lpc`, one `reg` resource, and fixed `#address-cells = <2>` and `#size-cells = <1>` when child ISA devices are present.

## Control Flow
The schema validates the parent LPC node and permits child device objects through `additionalProperties: { type: object }`. It intentionally omits a `ranges` requirement because LPC I/O ports are not CPU addresses on arm64.

## State And Persistence
The node records a persistent LPC controller register block and child-device I/O port tuples. Runtime state is in LPC/ISA/IPMI drivers.

## Dependencies And Integration Points
It integrates with ISA/EISA child bindings such as `ipmi-bt` and with HiSilicon LPC controller code interpreting two-cell port addresses.

## Risks
Adding `ranges` or treating LPC ports as CPU addresses would be semantically wrong. Incorrect address/size cell counts can make child device `reg` encodings invalid.

## Test Signals
`dtbs_check` validates node naming, cell counts, and child-address shape. Runtime signals include successful discovery of LPC-attached IPMI or legacy devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/low-pin-count.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hpe,gxp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hpe,gxp.yaml

## Purpose
This root platform binding identifies HPE GXP BMC boards, currently the DL360 Gen10 BMC platform.

## Important APIs, Types, And Functions
The root `compatible` must be a two-item list with a board string such as `hpe,gxp-dl360gen10` followed by the SoC family fallback `hpe,gxp`.

## Control Flow
The schema uses a single `oneOf` branch for GXP boards and requires `compatible`. Other root-node properties remain validated by generic schemas because `additionalProperties` is true.

## State And Persistence
It stores immutable board/SoC identity in the DTB; no runtime state or persistent storage is created.

## Dependencies And Integration Points
It integrates with HPE GXP platform setup and any driver or machine matching keyed by the root compatible.

## Risks
The schema is narrow: new GXP boards must be added explicitly or `dtbs_check` will fail. Wrong fallback ordering can prevent shared SoC code from matching.

## Test Signals
`dtbs_check` validates GXP DTS root compatibles; boot logs should show expected platform and BMC device probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hpe,gxp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/intel,keembay.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/intel,keembay.yaml

## Purpose
This schema identifies Intel Keem Bay platform DT root nodes.

## Important APIs, Types, And Functions
It fixes `$nodename` to `/` and requires `compatible = "intel,keembay-evm", "intel,keembay"`.

## Control Flow
Validation is a simple ordered `items` check. The board-specific compatible must precede the SoC fallback.

## State And Persistence
The schema describes immutable platform identity only. There is no runtime state, allocation, or persistence behavior.

## Dependencies And Integration Points
It integrates with Keem Bay board selection and SoC driver matching through the root compatible list.

## Risks
The binding currently covers one EVM; derivative boards need explicit schema updates. Misordering the two compatibles can break generic Keem Bay matching.

## Test Signals
`dt_binding_check` validates the schema and `dtbs_check` validates any Keem Bay DTS root node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/intel,keembay.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/intel-ixp4xx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/intel-ixp4xx.yaml

## Purpose
This root-node schema catalogs Intel IXP4xx network/NAS/router platforms for the IXP42x and IXP43x SoC families.

## Important APIs, Types, And Functions
The root compatible is validated as one of two fallback chains: a board string followed by `intel,ixp42x`, or selected boards followed by `intel,ixp43x`.

## Control Flow
dt-schema chooses a `oneOf` branch and enforces exact compatible ordering. The root node name is fixed to `/`.

## State And Persistence
The binding stores platform identity only. It has no mutable state; the compatible list controls machine and driver matching.

## Dependencies And Integration Points
It depends on the core schema and integrates with IXP4xx platform code, board-specific DTS files, and SoC-level driver matching.

## Risks
Many legacy boards are enumerated; misspelling or using the wrong SoC fallback silently changes platform match behavior. New boards must be added before validation passes.

## Test Signals
`dtbs_check` validates compatible chains for affected IXP4xx DTS files; successful boot and peripheral enumeration confirm the selected SoC family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/intel-ixp4xx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/keystone/ti,k3-sci-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/keystone/ti,k3-sci-common.yaml

## Purpose
This shared schema fragment defines common properties for TI K3 device-management nodes that communicate with the System Controller Processor through TI-SCI.

## Important APIs, Types, And Functions
The common properties are `ti,sci` phandle, `ti,sci-dev-id` uint32, and `ti,sci-proc-ids` tuple containing processor ID and host ID for remote processor ownership transfer.

## Control Flow
It is intended for inclusion by more specific clock, reset, interrupt, and processor-management bindings. `additionalProperties: true` lets those bindings define their own required and specialized fields.

## State And Persistence
The properties persist firmware protocol addressing and ownership metadata in DT. Runtime state is managed by the TI-SCI firmware and Linux TI-SCI clients.

## Dependencies And Integration Points
It depends on `/schemas/types.yaml` and integrates with the parent TI-SCI controller node described by `ti,sci.yaml`, plus TI clock/reset/power/remoteproc bindings.

## Risks
Wrong device IDs or processor/host tuples can make firmware calls target the wrong resource. Because this is common glue, changes can affect multiple K3 subsystems.

## Test Signals
Consumers should pass `dtbs_check` through their concrete bindings. Runtime signals include successful TI-SCI clock, reset, interrupt, or remote processor operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/keystone/ti,k3-sci-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/keystone/ti,sci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/keystone/ti,sci.yaml

## Purpose
This schema describes the TI-SCI system controller node used by Keystone/K3 SoCs to communicate with firmware managing clocks, resets, power domains, and other SoC resources.

## Important APIs, Types, And Functions
It validates `system-controller@...`, compatible strings `ti,k2g-sci` or `ti,am654-sci`, optional debug `reg`/`reg-names`, required mailbox names `rx` and `tx`, `mboxes`, optional `ti,host-id`, and child nodes `power-controller`, `clock-controller`, and `reset-controller` via dedicated `$ref`s.

## Control Flow
Validation requires compatible and mailbox wiring, then delegates child validation to the TI SCI PM domain, clock, and reset schemas. `additionalProperties: false` keeps the parent controller strict.

## State And Persistence
The DT stores mailbox endpoints, host identity, optional debug region, and child function nodes. Runtime state is held by the TI-SCI firmware and Linux protocol clients.

## Dependencies And Integration Points
It depends on mailbox providers, secure proxy/message manager nodes, and child schemas under `/schemas/soc/ti`, `/schemas/clock`, and `/schemas/reset`.

## Risks
Reversed mailboxes or wrong host IDs can break all firmware-mediated resources. Optional child nodes must remain compatible with the parent protocol node or subsystem drivers will not bind.

## Test Signals
`dt_binding_check` validates examples and child `$ref`s. Runtime probes of TI-SCI, power domains, clocks, and resets are strong integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/keystone/ti,sci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/lge.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/lge.yaml

## Purpose
This root-node schema catalogs LG Electronics LG1312 and LG1313 reference SoC platforms.

## Important APIs, Types, And Functions
It fixes `$nodename` to `/` and validates compatible lists `lge,lg1312-ref`, `lge,lg1312` or `lge,lg1313-ref`, `lge,lg1313`.

## Control Flow
Validation is an ordered `oneOf` selection between the two SoC families. Other root properties remain allowed.

## State And Persistence
The schema stores immutable board identity only, with no runtime state.

## Dependencies And Integration Points
It integrates with LG platform/machine matching and SoC-specific driver selection through root compatibles.

## Risks
The binding is small and exact; new boards or incorrect fallback order require updates. It does not validate peripherals beyond root identity.

## Test Signals
`dtbs_check` on LG DTS files validates compatible ordering; boot-time platform selection confirms runtime use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/lge.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/linux,dummy-virt.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/linux,dummy-virt.yaml

## Purpose
This schema identifies the QEMU dummy virt machine root node.

## Important APIs, Types, And Functions
It fixes `$nodename` to `/` and requires the root `compatible` string `linux,dummy-virt`.

## Control Flow
Validation is a direct constant check. `additionalProperties: true` leaves normal virtual platform contents to other bindings.

## State And Persistence
The DT root compatible stores virtual machine identity. There is no hardware state beyond what QEMU exposes in other nodes.

## Dependencies And Integration Points
It integrates with QEMU-generated DTBs and Linux virtual platform detection.

## Risks
The schema is intentionally minimal; it will not catch malformed devices below the root. Incorrect compatible value can affect virtual machine matching.

## Test Signals
`dtbs_check` against QEMU virt DT output or checked-in DTS validates the root compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/linux,dummy-virt.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell,berlin.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell,berlin.yaml

## Purpose
This root platform schema catalogs Synaptics/Marvell Berlin multimedia SoC boards, noting the product-line ownership transition to Synaptics.

## Important APIs, Types, And Functions
It validates root compatible fallback chains for Berlin2, Berlin2CD, Berlin2Q, and Berlin4CT boards, always ending in `marvell,berlin`.

## Control Flow
The schema uses `oneOf` to choose the exact board/SoC/family chain and fixes the root node name to `/`.

## State And Persistence
It describes immutable platform identity in the DTB. No runtime state or storage is managed by the schema.

## Dependencies And Integration Points
It integrates with Berlin SoC platform matching and board DTS files for devices such as Chromecast, Steam Link, and Sony NSZ-GS7.

## Risks
Fallback ordering matters for shared family code. The Synaptics/Marvell naming history can cause incompatible additions if maintainers mix vendor prefixes without schema updates.

## Test Signals
`dtbs_check` confirms root compatible strings; boot probing of Berlin platform drivers confirms runtime matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell,berlin.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/armada-37xx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/armada-37xx.yaml

## Purpose
This schema validates root compatibles for Marvell Armada 37xx boards, especially Armada 3720/3710 devices and Globalscale Espressobin variants.

## Important APIs, Types, And Functions
The root `compatible` is one of several ordered chains. Common board strings such as `cznic,turris-mox`, `glinet,gl-mv1000`, `globalscale,espressobin`, and `methode,edpu` fall back to `marvell,armada3720`, `marvell,armada3710`; Espressobin subvariants include extra intermediate board fallbacks.

## Control Flow
Validation selects one `oneOf` branch and enforces every list item in order. The root node name must be `/`.

## State And Persistence
The binding stores board/SoC identity only. Platform-specific state is represented by other nodes.

## Dependencies And Integration Points
It integrates with Armada 37xx DTS files, machine matching, and SoC drivers keyed by the fallback compatibles.

## Risks
Subvariant chains are easy to misorder, especially Espressobin V7 and eMMC/Ultra models. Missing the generic Armada fallback can prevent common drivers from matching.

## Test Signals
`dtbs_check` catches incompatible root strings. Boot logs showing correct Armada 37xx platform probing provide runtime confirmation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/armada-37xx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/armada-38x.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/armada-38x.yaml

## Purpose
This root-node schema documents Marvell Armada 380/385/388 boards, including Netgear, Marvell development boards, SolidRun Clearfog systems, and Kobol Helios4.

## Important APIs, Types, And Functions
It validates ordered compatible chains ending in `marvell,armada380`, with intermediate fallbacks for `marvell,armada385`, `marvell,armada388`, and `solidrun,clearfog-a1` where appropriate.

## Control Flow
Each board family is a `oneOf` branch. dt-schema requires exact order and branch-specific item counts.

## State And Persistence
The schema records immutable platform identity only; peripherals and memory state are validated elsewhere.

## Dependencies And Integration Points
It integrates with Armada 38x board DTS files and common SoC/platform code using the compatible chain.

## Risks
The 385/388 fallback hierarchy is important for shared support. Incorrect board grouping can select the wrong quirks for NAS or switch boards.

## Test Signals
`dtbs_check` validates compatible order for Armada 38x DTBs. Runtime signals include successful platform match and peripheral initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/armada-38x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/armada-7k-8k.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/armada-7k-8k.yaml

## Purpose
This schema catalogs Marvell Armada 7K/8K, CN913x, AP806/AP807/AP810, and related carrier/module root compatible chains.

## Important APIs, Types, And Functions
The binding validates many ordered chains, including pure SoC compatibles like `marvell,armada7020`, `marvell,armada-ap806-dual`, `marvell,armada-ap806`, board chains for Falcon and MACCHIATOBin, CN9130/9131/9132 fallback sequences, Alleycat5X carrier/module forms, and SolidRun CN913x products.

## Control Flow
`oneOf` enforces exactly one board or SoC chain. The order preserves board, module, SoC, CPU/AP, and family identity from most to least specific.

## State And Persistence
It stores root identity only. Multi-chip and carrier/module topology is represented through the compatible list rather than mutable state.

## Dependencies And Integration Points
It integrates with Marvell Armada 7K/8K platform code, DTS includes for AP/CP layouts, and board-specific matching.

## Risks
The multi-level fallback chains are error-prone. Missing an intermediate module or AP compatible can break shared initialization for carrier/module combinations.

## Test Signals
`dtbs_check` is the primary validation signal. Hardware boot on Armada/CN913x boards confirms that the selected compatible chain reaches the expected platform code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/armada-7k-8k.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,ac5.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,ac5.yaml

## Purpose
This root platform schema identifies Marvell Alleycat5 and Alleycat5X switch reference designs.

## Important APIs, Types, And Functions
It validates `marvell,rd-ac5`, `marvell,ac5` and `marvell,rd-ac5x`, `marvell,ac5x`, `marvell,ac5` compatible chains.

## Control Flow
The schema selects between AC5 and AC5X branches and requires the root node name `/`. Other root properties are allowed.

## State And Persistence
It carries immutable platform identity for switch SoCs; no runtime state is described here.

## Dependencies And Integration Points
It integrates with AC5/AC5X DTS files and switch SoC platform initialization.

## Risks
AC5X must retain the AC5 fallback for shared support. New boards require explicit enum additions.

## Test Signals
`dtbs_check` validates root compatibles; switch platform boot and Ethernet subsystem probing provide runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,ac5.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,armada-370-xp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,armada-370-xp.yaml

## Purpose
This schema catalogs root compatibles for Marvell Armada 370 and Armada XP boards, including NAS, router, switch, and development platforms.

## Important APIs, Types, And Functions
It validates board-specific compatibles followed by SoC fallbacks such as `marvell,armada370`, `marvell,armadaxp-98dx3236`, `marvell,armadaxp-mv78230`, `marvell,armadaxp-mv78260`, or `marvell,armadaxp-mv78460`, all ending at `marvell,armada-370-xp` where appropriate.

## Control Flow
`oneOf` chooses the board/SoC chain and requires exact ordering. The root node name is fixed to `/`.

## State And Persistence
The binding stores immutable board and SoC identity. Runtime platform state belongs to drivers matched by that identity.

## Dependencies And Integration Points
It integrates with Armada 370/XP DTS files and common Marvell platform code, especially for legacy NAS and switch boards.

## Risks
Board families have similar marketing names but different SoC fallbacks. Incorrect fallback can apply wrong CPU, switch, or peripheral assumptions.

## Test Signals
`dtbs_check` validates compatible chains; boot-time machine match and peripheral enumeration are runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,armada-370-xp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,armada375.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,armada375.yaml

## Purpose
This schema identifies the Marvell Armada 375 development board platform.

## Important APIs, Types, And Functions
The root compatible must be `marvell,a375-db`, `marvell,armada375`.

## Control Flow
Validation is a single ordered `items` check with the root node name fixed to `/`.

## State And Persistence
It records immutable board/SoC identity only.

## Dependencies And Integration Points
It integrates with Armada 375 DTS files and platform matching.

## Risks
The schema covers one board, so variants need new enum entries. Missing the SoC fallback breaks common Armada 375 matching.

## Test Signals
`dtbs_check` validates DTS root nodes; runtime platform selection validates integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,armada375.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,armada390.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,armada390.yaml

## Purpose
This schema catalogs Marvell Armada 39x platform root compatibles for A390, A395, and A398 boards.

## Important APIs, Types, And Functions
It validates chains for `marvell,a390-db`, `marvell,armada390`, for A398 boards falling back to `marvell,armada398`, `marvell,armada390`, and for A395 boards falling back to `marvell,armada395`, `marvell,armada390`.

## Control Flow
`oneOf` enforces the exact SoC variant branch and compatible order.

## State And Persistence
Only root platform identity is represented. Device state is in other DT nodes and runtime drivers.

## Dependencies And Integration Points
It integrates with Armada 39x DTS files and shared Armada platform matching.

## Risks
Variant fallback errors can select the wrong SoC-level support. New boards require schema updates.

## Test Signals
`dtbs_check` validates root compatible lists; hardware boot validates correct platform matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,armada390.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,dove.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,dove.yaml

## Purpose
This root schema catalogs Marvell Dove boards such as CuBox, D2Plug/D3Plug, CM-A510, and Dove DB.

## Important APIs, Types, And Functions
Compatible chains either use a board enum followed by `marvell,dove`, or include intermediate board fallbacks such as `solidrun,cubox` or `compulab,cm-a510`.

## Control Flow
Validation chooses one `oneOf` branch and enforces exact ordering from board variant to generic Dove SoC.

## State And Persistence
The schema stores immutable platform identity only.

## Dependencies And Integration Points
It integrates with Marvell Dove DTS files and legacy ARM platform matching.

## Risks
Intermediate fallback boards are important for variants; omitting them can bypass board-specific quirks.

## Test Signals
`dtbs_check` validates root compatible order; boot-time board and SoC driver matching confirms use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,dove.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,kirkwood.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,kirkwood.yaml

## Purpose
This large root-node schema catalogs Marvell Kirkwood boards across NAS, plug computer, router, and embedded product families.

## Important APIs, Types, And Functions
The schema validates many ordered compatible chains for generic `marvell,kirkwood`, SoC variants `marvell,kirkwood-88f6192`, `88f6281`, `88f6282`, `88f6283`, `88f6702`, and `98DX4122`, plus board-family fallbacks for Synology, D-Link, Globalscale, LaCie, Buffalo, Netgear, Zyxel, and others.

## Control Flow
Each board or product family is represented as a `oneOf` branch. dt-schema enforces exact item counts and ordering, commonly board variant, product family, SoC variant, then `marvell,kirkwood`.

## State And Persistence
The binding represents immutable root identity. Runtime state for SATA, Ethernet, GPIO, and storage devices is described in separate nodes.

## Dependencies And Integration Points
It integrates with many legacy Kirkwood DTS files and platform-specific quirk matching. The fallback strings are used by common Marvell Kirkwood support.

## Risks
The list is long and contains highly similar product names, so duplicate or misordered entries are easy. The `synology,ds212pv10` duplicate-looking chain should be treated carefully when editing to avoid unintended ABI changes.

## Test Signals
`dtbs_check` across Kirkwood DTS files is essential. Hardware or emulator boot confirming SoC variant selection and peripheral probing is the runtime signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,kirkwood.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,orion5x.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,orion5x.yaml

## Purpose
This schema catalogs Marvell Orion5x platform root compatibles for 88F5181 and 88F5182 boards.

## Important APIs, Types, And Functions
It validates board enums followed by `marvell,orion5x-88f5181`, `marvell,orion5x` or by `marvell,orion5x-88f5182`, `marvell,orion5x`.

## Control Flow
`oneOf` selects the SoC branch and enforces the exact board-to-SoC fallback order.

## State And Persistence
Only root identity is represented; mutable device state is outside this schema.

## Dependencies And Integration Points
It integrates with Orion5x DTS files and legacy Marvell platform code.

## Risks
The two SoC variants are close enough that board placement in the wrong enum would select incorrect low-level support.

## Test Signals
`dtbs_check` validates root compatibles. Successful boot and peripheral setup confirm runtime matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,orion5x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek.yaml

## Purpose
This large root platform schema catalogs MediaTek SoC based boards across mobile, router, Chromebook, IoT, and evaluation platforms.

## Important APIs, Types, And Functions
It fixes the root node to `/` and validates many `compatible` chains sorted by final SoC compatible. Covered SoCs include MT2701, MT762x, MT798x router SoCs, MT81xx/MT82xx Chromebook and tablet SoCs, MT83xx/MT839x Genio-style platforms, and MT8516. Board chains include Banana Pi, Google Chromebook revisions/SKUs, MediaTek EVBs, Sony phones, and other vendors.

## Control Flow
dt-schema selects a single `oneOf` branch and checks exact compatible ordering. Many Chromebook entries encode revision and SKU fallback chains, so the list acts as an ABI catalog.

## State And Persistence
The schema records immutable platform identity in the DTB. Device state and resources are represented by downstream peripheral nodes.

## Dependencies And Integration Points
It integrates with MediaTek platform matching, board DTS files, and SoC-specific driver probing. `additionalProperties: true` leaves non-root properties to generic schemas.

## Risks
The file is high-churn because every new board or SKU needs an entry. Risks include ordering mistakes, placing a board under the wrong SoC, and accidentally changing ChromeOS revision fallback semantics.

## Test Signals
`dtbs_check` over MediaTek DTS files is the primary signal. Boot logs showing expected SoC and board quirks, especially for Chromebook SKUs, provide runtime confirmation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,audsys.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,audsys.yaml

## Purpose
This schema describes MediaTek AUDSYS clock/system controller blocks and optional embedded audio-controller child nodes.

## Important APIs, Types, And Functions
The compatible list is either a supported AUDSYS variant followed by `syscon`, or the MT7623 backward-compatible chain through `mediatek,mt2701-audsys`, `syscon`. It requires `#clock-cells = <1>`, supports `reg`, and has an `audio-controller` child whose schema depends on the SoC.

## Control Flow
`allOf` conditionals attach specific sound binding `$ref`s for MT2701/MT7622, MT8183 audiosys, and MT8192 audsys. `additionalProperties: false` keeps the controller node strict.

## State And Persistence
The DT describes clock controller registers and optional audio hardware topology. Runtime state is in clock, syscon, and ASoC drivers.

## Dependencies And Integration Points
It depends on sound schemas, syscon, clock provider conventions, interrupt/power/clock phandles in child examples, and MediaTek clock ID headers.

## Risks
The MT8183 spelling split between `audiosys` and `audsys` and the MT7623 compatibility exception are easy to break. Missing `#clock-cells` prevents clock consumers from resolving.

## Test Signals
`dt_binding_check` validates conditional child refs. `dtbs_check`, clock provider registration, and ASoC card probing are runtime/integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,audsys.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,mmsys.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,mmsys.yaml

## Purpose
This binding describes MediaTek MMSYS/VDOSYS/VPPSYS system controllers that provide display clocks, routing, resets, GCE access, and graph outputs.

## Important APIs, Types, And Functions
The node name must match `syscon@...`. Compatible chains cover many MediaTek display system variants followed by `syscon`, including deprecated `mediatek,mt8195-mmsys`, MT7623 fallback through MT2701, and MT8195 VDOSYS0 compatibility. Properties include `reg`, `power-domains`, `mboxes`, `mediatek,gce-client-reg`, `#clock-cells`, `#reset-cells`, and an optional graph `port`.

## Control Flow
Validation requires compatible, reg, and clock cells. The graph `port` uses `anyOf` to require at least one endpoint among primary, secondary, and tertiary outputs.

## State And Persistence
The DT records display-system MMIO, clock/reset provider metadata, power domain, command-queue mailbox, and display graph connectivity. Runtime state is held by display, clock, reset, power, and GCE drivers.

## Dependencies And Integration Points
It depends on graph, mailbox, power-domain, and type schemas plus MediaTek GCE headers. It integrates with DRM display pipelines and system-controller users.

## Risks
Deprecated MT8195 compatible handling and multi-output graph modeling are the main traps. Wrong GCE register tuples can break command-queue programming.

## Test Signals
`dt_binding_check` validates graph and property shape. `dtbs_check`, DRM component bind, clock/reset registration, and display pipeline bring-up are strong signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,mmsys.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,mt7622-pcie-mirror.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,mt7622-pcie-mirror.yaml

## Purpose
This schema documents the MT7622 PCIe mirror controller, a small syscon register block used to configure the PCIe controller.

## Important APIs, Types, And Functions
It requires `compatible = "mediatek,mt7622-pcie-mirror", "syscon"` and one `reg` range.

## Control Flow
Validation is a fixed-shape check with no extra properties allowed.

## State And Persistence
The DT describes a persistent MMIO configuration window. Runtime state is managed through syscon/regmap users in PCIe-related code.

## Dependencies And Integration Points
It integrates with MT7622 PCIe controller setup and Linux syscon infrastructure.

## Risks
The register window is tiny, so address or size mistakes can target the wrong system register. Missing `syscon` prevents shared regmap lookup.

## Test Signals
`dtbs_check` catches schema shape errors; PCIe enumeration on MT7622 validates runtime integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,mt7622-pcie-mirror.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,mt7622-wed.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,mt7622-wed.yaml

## Purpose
This schema describes MediaTek Wireless Ethernet Dispatch controllers, which offload Ethernet-to-WLAN traffic and interact with WLAN DMA queues and PCIe interrupts.

## Important APIs, Types, And Functions
Compatible strings cover `mediatek,mt7622-wed`, `mt7981-wed`, `mt7986-wed`, and `mt7988-wed`, each followed by `syscon`. Required properties are `reg` and `interrupts`; newer variants may use five `memory-region` phandles with matching `memory-region-names` and a `mediatek,wo-ccif` phandle.

## Control Flow
An `allOf` conditional forbids firmware memory-region and WO CCIF properties for MT7622. The schema otherwise validates exact memory-region name ordering.

## State And Persistence
The DT stores MMIO, interrupt, reserved firmware memory, and controller-interface links. Runtime state is in WED networking, firmware, and PCIe/WLAN drivers.

## Dependencies And Integration Points
It depends on reserved-memory phandles, interrupt controllers, syscon, and MediaTek wireless offload infrastructure.

## Risks
Variant differences are significant: applying MT7986 firmware-memory properties to MT7622 is invalid, while omitting them on newer designs can break firmware-assisted offload.

## Test Signals
`dtbs_check` validates variant conditionals. Runtime signals include WED driver probe, interrupt handling, reserved-memory mapping, and WLAN offload operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,mt7622-wed.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,mt7986-wed-pcie.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,mt7986-wed-pcie.yaml

## Purpose
This binding documents the MT7986 WED PCIe configuration syscon block.

## Important APIs, Types, And Functions
It requires `compatible = "mediatek,mt7986-wed-pcie", "syscon"` and one `reg` range.

## Control Flow
The schema is strict and fixed-shape; compatible and reg are required and additional properties are rejected.

## State And Persistence
The node describes a small persistent MMIO configuration region. Runtime state is in WED/PCIe syscon users.

## Dependencies And Integration Points
It integrates with MT7986 WED and PCIe controller setup through syscon/regmap.

## Risks
Address or compatible errors prevent WED PCIe configuration. The two-item compatible order must include `syscon`.

## Test Signals
`dtbs_check` validates DTS shape; PCIe-backed wireless offload initialization validates runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mediatek/mediatek,mt7986-wed-pcie.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/microchip,sam9x60-pit64b.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/microchip,sam9x60-pit64b.yaml

## Purpose
This schema describes Microchip PIT64B, a 64-bit periodic interval timer used by SAM9X60, SAM9X7, SAMA7D65, and SAMA7G5 families.

## Important APIs, Types, And Functions
Compatible is either `microchip,sam9x60-pit64b` or a newer SoC-specific string followed by that fallback. Required properties are `reg`, `interrupts`, and `clocks`; `clock-names` can contain one or two names from `pclk` and `gclk`.

## Control Flow
Validation enforces one MMIO resource, one interrupt, one or two clocks, and no unevaluated properties.

## State And Persistence
The DT records the timer register block, interrupt line, and clock sources. Runtime state is managed by the timer/clocksource driver.

## Dependencies And Integration Points
It depends on interrupt and clock provider bindings, including AT91/Microchip clock IDs in examples.

## Risks
Clock-name ordering must match clock phandles. Missing `gclk` may be valid for some designs but wrong for hardware needing a generated clock.

## Test Signals
`dt_binding_check` validates examples; boot-time clocksource/clockevent registration and timer interrupt delivery validate runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/microchip,sam9x60-pit64b.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/microchip,sama7g5-chipid.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/microchip,sama7g5-chipid.yaml

## Purpose
This binding describes Atmel/Microchip Chip ID register blocks used to read SoC identification and revision information.

## Important APIs, Types, And Functions
It accepts `atmel,sama5d2-chipid`, `microchip,sama7d65-chipid`, or `microchip,sama7g5-chipid`, and requires a single `reg` range.

## Control Flow
Validation is a strict compatible-plus-reg check with no unevaluated properties allowed.

## State And Persistence
The node describes read-only or mostly read-only chip identification registers. Runtime state is limited to driver reads of the register contents.

## Dependencies And Integration Points
It integrates with SoC identification code and any platform logic using chip revision data.

## Risks
The title mentions RAMC SDRAM/DDR controller while the description and compatible strings describe Chip ID; that mismatch can confuse maintainers. Incorrect `reg` size can hide revision fields.

## Test Signals
`dt_binding_check` validates schema shape; boot logs or sysfs/debug output showing correct SoC ID validate runtime reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/microchip,sama7g5-chipid.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/microchip,sparx5.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/microchip,sparx5.yaml

## Purpose
This root platform schema describes Microchip Sparx5 ARMv8 TSN-capable Ethernet switch boards.

## Important APIs, Types, And Functions
The root compatible must identify one of `microchip,sparx5-pcb125`, `pcb134`, or `pcb135` followed by `microchip,sparx5`. The root must also contain an `axi@600000000` simple-bus child.

## Control Flow
Validation requires both `compatible` and the fixed-address AXI bus child. The child object requires `compatible = "simple-bus"` while other root properties are allowed.

## State And Persistence
The binding records immutable board identity and the top-level AXI bus location. Runtime state belongs to switch, bus, and peripheral drivers.

## Dependencies And Integration Points
It integrates with Sparx5 board DTS files and the SoC bus/peripheral layout rooted at `axi@600000000`.

## Risks
The mandatory fixed AXI child is stricter than most root schemas; missing it invalidates the platform even if the root compatible is correct.

## Test Signals
`dtbs_check` validates root and AXI child structure; switch subsystem probe validates runtime integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/microchip,sparx5.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/moxart.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/moxart.yaml

## Purpose
This schema identifies the MOXA ART UC-7112-LX embedded computer platform.

## Important APIs, Types, And Functions
The root compatible list is `moxa,moxart-uc-7112-lx`, `moxa,moxart`.

## Control Flow
Validation enforces the ordered two-item compatible list and allows other root properties.

## State And Persistence
It stores immutable platform identity only.

## Dependencies And Integration Points
It integrates with MOXA ART platform code and board DTS files.

## Risks
The schema has no `$nodename` restriction and covers one board, so maintainers must update it for variants.

## Test Signals
`dtbs_check` validates DTS root compatible strings; boot platform matching confirms runtime use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/moxart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mrvl/mrvl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mrvl/mrvl.yaml

## Purpose
This root platform schema catalogs Marvell/MRVL PXA and MMP-family boards.

## Important APIs, Types, And Functions
It validates root compatible chains for PXA168 Aspenite, PXA910 DKB, MMP2 boards including OLPC XO-1.75, MMP3 Dell Wyse Ariel, and PXA1908 Samsung Core Prime LTE.

## Control Flow
The schema fixes `$nodename` to `/` and selects one `oneOf` branch for the board/SoC fallback list.

## State And Persistence
The binding records immutable board/SoC identity only.

## Dependencies And Integration Points
It integrates with PXA/MMP DTS files and platform/SoC matching code.

## Risks
Vendor prefix drift is visible: both `mrvl` and `marvell` compatibles are present for different generations. New entries should preserve existing naming conventions.

## Test Signals
`dtbs_check` validates compatible chains; platform boot confirms correct SoC matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mrvl/mrvl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mstar/mstar,l3bridge.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mstar/mstar,l3bridge.yaml

## Purpose
This binding describes the MStar/SigmaStar Armv7 L3 bridge register block used to flush a CPU-to-memory pipeline before DMA-capable devices run.

## Important APIs, Types, And Functions
It requires `compatible = "mstar,l3bridge"` and one `reg` range. The platform code uses this node to install a DMA barrier.

## Control Flow
Validation is strict: compatible and reg are required and additional properties are rejected.

## State And Persistence
The DT records persistent bridge registers. Runtime state is the platform-installed barrier and hardware flush side effects.

## Dependencies And Integration Points
It integrates with MStar platform code and DMA coherency/barrier handling.

## Risks
If the node is absent or the register range is wrong, DMA devices may observe stale memory due to missing pipeline flushes.

## Test Signals
`dtbs_check` validates the node. Runtime DMA stability on affected SoCs is the practical signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mstar/mstar,l3bridge.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mstar/mstar,smpctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mstar/mstar,smpctrl.yaml

## Purpose
This schema documents MStar/SigmaStar SMP control registers used to set secondary CPU boot addresses and release magic values.

## Important APIs, Types, And Functions
It requires a compatible list of a SoC-specific value such as `sstar,ssd201-smpctrl` followed by `mstar,smpctrl`, plus a single `reg` range.

## Control Flow
Validation is a strict fixed-shape check and disallows additional properties.

## State And Persistence
The node describes persistent SMP control registers. Runtime state is written by platform CPU bring-up code.

## Dependencies And Integration Points
It integrates with MStar/SigmaStar SMP startup code and CPU nodes that depend on secondary bring-up.

## Risks
Incorrect registers can leave secondary CPUs parked in boot ROM loops. Compatible order must retain the generic fallback for shared handling.

## Test Signals
`dtbs_check` validates the schema; successful multi-core boot validates runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mstar/mstar,smpctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mstar/mstar.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mstar/mstar.yaml

## Purpose
This root platform schema catalogs MStar/SigmaStar boards for Infinity, Infinity2M, Infinity3, and Mercury5 SoC families.

## Important APIs, Types, And Functions
The root compatible list maps boards such as BreadBee, BreadBee Crust, DongShanPiOne, UnitV2, Miyoo Mini, Wireless Tag modules, and 70mai midrive d08 to their SoC family fallback.

## Control Flow
`oneOf` selects the SoC family branch and validates exact board-to-SoC compatible ordering.

## State And Persistence
It records immutable platform identity only.

## Dependencies And Integration Points
It integrates with MStar DTS files and platform matching for these SoCs.

## Risks
The schema covers small-board ecosystems where board names are similar; incorrect enum placement can select wrong SoC support.

## Test Signals
`dtbs_check` validates root compatible chains; board boot validates platform matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mstar/mstar.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/nuvoton/nuvoton,ma35d1.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/nuvoton/nuvoton,ma35d1.yaml

## Purpose
This root platform schema identifies ARMv8 Nuvoton MA35D1 boards.

## Important APIs, Types, And Functions
It validates board strings `nuvoton,ma35d1-iot` and `nuvoton,ma35d1-som` followed by `nuvoton,ma35d1`.

## Control Flow
The schema fixes the root node name to `/` and uses a single `oneOf` branch for MA35D1 boards.

## State And Persistence
It records immutable root platform identity only.

## Dependencies And Integration Points
It integrates with MA35D1 DTS files and SoC driver matching.

## Risks
New MA35 variants require explicit schema additions. Missing the generic fallback can break common MA35D1 support.

## Test Signals
`dtbs_check` validates root compatibles; successful MA35D1 boot confirms runtime matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/nuvoton/nuvoton,ma35d1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/nuvoton/nuvoton,npcm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/nuvoton/nuvoton,npcm.yaml

## Purpose
This root platform schema catalogs Nuvoton WPCM450 and NPCM BMC evaluation/server boards.

## Important APIs, Types, And Functions
It validates root compatible chains for `supermicro,x9sci-ln4f-bmc`, `nuvoton,wpcm450`, for `nuvoton,npcm750-evb`, `nuvoton,npcm750`, and for `nuvoton,npcm845-evb`, `nuvoton,npcm845`.

## Control Flow
`oneOf` selects the BMC SoC family branch and enforces ordered board-to-SoC fallback strings.

## State And Persistence
The binding records immutable BMC platform identity only.

## Dependencies And Integration Points
It integrates with Nuvoton NPCM/WPCM DTS files and BMC platform driver matching.

## Risks
Server BMC board compatibles must remain exact for platform quirks. New NPCM boards need explicit enum additions.

## Test Signals
`dtbs_check` validates root compatible strings; BMC boot and platform device probing confirm runtime integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/nuvoton/nuvoton,npcm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/nvidia,tegra194-ccplex.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/nvidia,tegra194-ccplex.yaml

## Purpose
This binding describes the `cpus` node-level NVIDIA Tegra194 CPU complex, including a BPMP phandle used to query CPU operating point data.

## Important APIs, Types, And Functions
It requires `$nodename = cpus`, compatible `nvidia,tegra194-ccplex`, and optional `nvidia,bpmp` phandle. The example contains Carmel CPU child nodes using PSCI enable-method.

## Control Flow
Validation applies to the `cpus` node rather than the root. Additional properties are allowed so standard CPU topology and child CPU nodes can coexist.

## State And Persistence
The DT records CPU-complex identity and firmware link to BPMP. Runtime state is managed by CPU, PSCI, cpufreq/OPP, and BPMP drivers.

## Dependencies And Integration Points
It integrates with Tegra BPMP firmware bindings, CPU nodes, PSCI, and operating point discovery.

## Risks
Missing or wrong BPMP phandle can prevent CPU OPP queries. Applying the compatible to the wrong node name would fail schema validation and driver expectations.

## Test Signals
`dtbs_check` validates `cpus` node shape; CPU enumeration and cpufreq/OPP probing validate runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/nvidia,tegra194-ccplex.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/nxp/lpc32xx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/nxp/lpc32xx.yaml

## Purpose
This schema catalogs NXP LPC32xx and LPC43xx platform compatibles.

## Important APIs, Types, And Functions
It allows plain SoC compatibles for LPC3220/3230/3240, board-to-SoC chains for EA/Phytec LPC3250 boards, and LPC43xx development/evaluation boards with LPC4357/LPC4337/LPC4350 fallbacks.

## Control Flow
Validation selects one `oneOf` branch. Some branches are single-string SoC compatibles while others are ordered board fallback chains.

## State And Persistence
The binding records immutable platform identity only.

## Dependencies And Integration Points
It integrates with NXP LPC DTS files and platform matching.

## Risks
Mixing LPC32xx and LPC43xx families in one schema requires care when adding boards. Single-string SoC compatibles offer less board-specific validation than ordered board chains.

## Test Signals
`dtbs_check` validates compatible lists; boot-time platform match confirms runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/nxp/lpc32xx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/pmu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/pmu.yaml

## Purpose
This schema describes ARM CPU Performance Monitor Unit nodes used for counting CPU and cache events.

## Important APIs, Types, And Functions
The `compatible` enum covers many ARM, Apple, Qualcomm, NVIDIA, Samsung, Broadcom, Cavium, and Ampere/APM PMUs. Optional properties include `interrupts`, `interrupt-affinity`, Qualcomm `qcom,no-pc-write`, and `secure-reg-access` for ARMv7 secure-state setup.

## Control Flow
Validation requires only `compatible`; interrupt properties are shape-checked when present. `additionalProperties: false` makes the PMU node strict.

## State And Persistence
The DT records PMU identity and interrupt routing. Runtime state is in perf/PMU drivers and hardware counters.

## Dependencies And Integration Points
It integrates with interrupt controller bindings, CPU phandles for affinity, and Linux perf PMU drivers.

## Risks
Incorrect interrupt affinity causes per-CPU counter interrupts to be routed incorrectly. `secure-reg-access` is valid only for a narrow ARMv7 secure-state case and can be harmful if copied blindly.

## Test Signals
`dtbs_check` validates compatible and affinity shape. Runtime signals include PMU driver probe, perf event counting, and interrupt delivery under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/pmu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/primecell.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/primecell.yaml

## Purpose
This generic schema describes ARM PrimeCell peripherals that expose standard ID registers for driver matching.

## Important APIs, Types, And Functions
The compatible list must contain `arm,primecell` after a more specific engineering-name compatible. Optional properties include `arm,primecell-periphid`, `clocks`, and `clock-names` containing `apb_pclk`.

## Control Flow
Validation checks that `arm,primecell` appears in the compatible list and that clock naming includes the APB clock. Additional properties are allowed for specific PrimeCell device bindings.

## State And Persistence
The DT records peripheral identity, optional ID override, and clock inputs. Runtime state is managed by the specific PrimeCell driver.

## Dependencies And Integration Points
It is a shared integration point for many ARM AMBA/PrimeCell device schemas and drivers.

## Risks
Because additional properties are allowed, specific device schemas must add stricter validation. Wrong `arm,primecell-periphid` can override hardware identification incorrectly.

## Test Signals
`dtbs_check` validates common PrimeCell constraints; AMBA bus probing and specific driver binding validate runtime integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/primecell.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/psci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/psci.yaml

## Purpose
This schema describes ARM Power State Coordination Interface firmware nodes used by Linux to perform CPU suspend, hotplug, CPU on/off, migration, and hierarchical power-domain control.

## Important APIs, Types, And Functions
It validates `psci` node name, compatible strings for `arm,psci`, `arm,psci-0.2`, and `arm,psci-1.0`, the call `method` (`smc` or `hvc`), legacy function IDs `cpu_suspend`, `cpu_off`, `cpu_on`, `migrate`, `arm,psci-suspend-param`, and `power-domain-*` children referenced to the generic power-domain schema.

## Control Flow
An `allOf` conditional requires `cpu_off` and `cpu_on` when the legacy `arm,psci` compatible is present. PSCI 0.2 and 1.0 branches allow standardized function IDs without explicit numeric properties.

## State And Persistence
The DT stores firmware ABI selection, call conduit, optional legacy function IDs, and power-domain topology. Runtime state is managed by PSCI firmware, CPU hotplug/idle, and power-domain code.

## Dependencies And Integration Points
It integrates with CPU `enable-method = "psci"`, idle-state bindings, domain-idle-state bindings, and generic power-domain bindings.

## Risks
Wrong `method` can make every PSCI call trap to the wrong firmware conduit. Legacy and modern compatible mixing must preserve required function IDs for old kernels.

## Test Signals
`dt_binding_check` validates examples and conditionals. Runtime signals include CPU bring-up, hotplug, suspend, idle-state entry, and hierarchical power-domain operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/psci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-ctcu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-ctcu.yaml

## Purpose
This schema describes Qualcomm CoreSight TMC Control Unit devices that help TMC ETR sinks filter trace data by source Trace ID.

## Important APIs, Types, And Functions
It validates compatible `qcom,sa8775p-ctcu` or `qcom,qcs8300-ctcu`, `qcom,sa8775p-ctcu`, plus `reg`, optional APB clock, optional `label`, and graph `in-ports` from CoreSight trace buses.

## Control Flow
Validation requires compatible, reg, and in-ports. Graph port nodes are validated by the generic graph schema, allowing port indices 0 and 1.

## State And Persistence
The DT records the CTCU MMIO region, clock, and trace graph inputs. Runtime state is in CoreSight drivers configuring trace filters.

## Dependencies And Integration Points
It depends on graph bindings, clocks, and CoreSight TMC/ETR endpoint links.

## Risks
Broken graph endpoint phandles can make trace paths unusable even if the device probes. Missing clock data can affect APB register access on platforms that require it.

## Test Signals
`dtbs_check` validates graph shape. Runtime CoreSight path discovery and ETR trace filtering validate integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-ctcu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-itnoc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-itnoc.yaml

## Purpose
This binding describes Qualcomm CoreSight Interconnect Trace Network-on-Chip links that forward subsystem trace data to an aggregator TNOC.

## Important APIs, Types, And Functions
The node name matches `itnoc@...`; required properties include `compatible = "qcom,coresight-itnoc"`, `reg`, one APB clock with `clock-names = "apb"`, graph `in-ports`, and a single output `out-ports/port`.

## Control Flow
Validation requires both graph directions and rejects additional properties. Input ports can use small hexadecimal port indices; output is a fixed port object.

## State And Persistence
The DT records trace interconnect MMIO, clock, and graph connectivity. Runtime state is CoreSight routing state.

## Dependencies And Integration Points
It integrates with CoreSight graph endpoints, clock providers, TPDM sources, and aggregator TNOC nodes.

## Risks
Trace graph errors are high-impact: a missing remote endpoint can prevent source-to-sink path construction. Clock-name mismatch prevents driver clock lookup.

## Test Signals
`dtbs_check` validates graph and clock shape; CoreSight sysfs path discovery and trace capture validate runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-itnoc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-remote-etm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-remote-etm.yaml

## Purpose
This schema describes Qualcomm CoreSight remote ETM nodes for enabling trace collection from remote processors such as modems.

## Important APIs, Types, And Functions
It requires `compatible = "qcom,coresight-remote-etm"` and graph `out-ports` with a single `port` to the CoreSight trace bus. `label` is optional.

## Control Flow
Validation is strict and requires the output graph. There is no MMIO or clock requirement because the traced processor is remote.

## State And Persistence
The DT records a logical CoreSight source and its graph output. Runtime state is managed through CoreSight sysfs and remote processor trace infrastructure.

## Dependencies And Integration Points
It depends on graph bindings and integrates with funnels, TMC sinks, and remote processor trace enable paths.

## Risks
Without a valid output endpoint, the remote ETM cannot be connected to a sink. Because there is no register resource, all useful integration depends on graph correctness and driver support.

## Test Signals
`dtbs_check` validates graph shape. Runtime signal is enabling the remote ETM source and collecting trace through a CoreSight sink.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-remote-etm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-tnoc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-tnoc.yaml

## Purpose
This binding describes Qualcomm CoreSight Trace Network-on-Chip aggregator instances that combine trace streams and route them toward sinks.

## Important APIs, Types, And Functions
It uses a custom `select` for `qcom,coresight-tnoc` to avoid matching every `arm,primecell` node. Required properties include node name `tn@...`, compatible `qcom,coresight-tnoc`, `arm,primecell`, `reg`, APB `clocks`/`clock-names = "apb_pclk"`, `in-ports`, and `out-ports`.

## Control Flow
Validation requires full CoreSight graph connectivity and PrimeCell-compatible clock naming. Additional properties are rejected.

## State And Persistence
The DT stores MMIO, APB clock, and trace routing graph. Runtime state is the active CoreSight route and hardware aggregation configuration.

## Dependencies And Integration Points
It integrates with PrimeCell/AMBA probing, graph endpoints, TPDM/ITNOC inputs, funnels, and TMC sinks.

## Risks
The custom select is important; removing it can cause schema collisions with generic PrimeCell devices. Broken graph endpoints block trace path construction.

## Test Signals
`dtbs_check` validates graph and PrimeCell clock shape. CoreSight path enablement and trace capture validate runtime integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-tnoc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-tpda.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-tpda.yaml

## Purpose
This schema describes Qualcomm Trace, Profiling and Diagnostics Aggregator devices that packetize and timestamp TPDM data using MIPI STPv2 and forward it over ATB.

## Important APIs, Types, And Functions
It uses custom selection on `qcom,coresight-tpda`. Required properties include node name `tpda@...`, compatible `qcom,coresight-tpda`, `arm,primecell`, `reg`, APB clock with `apb_pclk`, `in-ports`, and `out-ports`; `label` is optional.

## Control Flow
Validation requires both input and output CoreSight graph sides. The description also documents sysfs integration-test commands that generate TPDM test data and observe sink write pointers.

## State And Persistence
The DT records TPDA MMIO, clock, and graph links. Runtime state is aggregation, packetization, and active CoreSight route state.

## Dependencies And Integration Points
It integrates with TPDM sources, funnels, TMC sinks, graph bindings, and PrimeCell/AMBA clocking.

## Risks
A trace path must contain only one TPDA between a TPDM source and sink; graph mistakes can create invalid topology. Missing APB clock prevents register access.

## Test Signals
`dtbs_check` validates the node; CoreSight integration tests, sink `rwp` movement, and trace capture are direct runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-tpda.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-tpdm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-tpdm.yaml

## Purpose
This binding describes Qualcomm Trace, Profiling and Diagnostics Monitor devices that collect implementation-defined, basic count, tenure count, CMB, and DSB datasets and forward them to TPDA/funnels.

## Important APIs, Types, And Functions
Compatible is either `qcom,coresight-static-tpdm` or `qcom,coresight-tpdm`, `arm,primecell`. Required properties are `compatible`, `reg`, `clocks`, and `clock-names`; dataset properties include `qcom,dsb-element-bits`, `qcom,cmb-element-bits`, `qcom,dsb-msrs-num`, and `qcom,cmb-msrs-num`. `out-ports` is optional graph output.

## Control Flow
Custom selection prevents PrimeCell overmatching. Validation enforces enum bounds for dataset widths and MSR counts, while graph output connects TPDM to TPDA or funnel.

## State And Persistence
The DT records monitor MMIO, clock, dataset capabilities, and trace graph output. Runtime state is dataset collection and CoreSight route state.

## Dependencies And Integration Points
It integrates with PrimeCell/AMBA, CoreSight graph routing, TPDA aggregators, funnels, and TMC sinks.

## Risks
Incorrect dataset element width or MSR count can make TPDA/driver programming wrong. Static TPDM nodes lack MMIO, so driver handling must match the compatible branch.

## Test Signals
`dtbs_check` validates properties and graph shape. Runtime signals include TPDM source enablement, integration-test data generation, and sink trace movement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom,coresight-tpdm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom-soc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom-soc.yaml

## Purpose
This schema enforces Qualcomm SoC-compatible naming conventions for component nodes rather than a specific hardware block.

## Important APIs, Types, And Functions
The `select` matches Qualcomm compatible strings containing SoC families such as APQ, IPQ, MDM, MSM, QCM, QCS, QRU/QDU, SA, SC, SDM/SDA/SDX/SM, X1E/X1P, plus names like Glymur and Milos. The allowed `compatible` patterns prefer `qcom,SoC-IP` format while preserving legacy wildcard and enum exceptions.

## Control Flow
When selection matches a compatible string, validation checks it against preferred patterns, legacy patterns, or explicit exceptions. `additionalProperties: true` means the schema only polices naming.

## State And Persistence
There is no hardware state. The schema persists naming policy in machine-readable form.

## Dependencies And Integration Points
It integrates with every Qualcomm component binding by adding a cross-cutting dt-schema naming check.

## Risks
Overly broad regex changes can reject valid legacy compatibles or accept new names that violate policy. New legacy exceptions should be rare and explicit.

## Test Signals
`dt_binding_check` and `dtbs_check` surface naming violations for Qualcomm component nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom-soc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom.yaml

## Purpose
This large root-node schema catalogs Qualcomm boards and SoCs across APQ, IPQ, MDM, MSM, QCM/QCS/QRB, QDU/QRU, SA/SAR, SC, SDM/SDA, SM, and X1 families.

## Important APIs, Types, And Functions
It constrains the root node name to `/` and validates many exact `compatible` chains. The catalog covers phones, tablets, routers, Chromebooks using the depthcharge boot flow, development boards, industrial boards, Windows-on-Arm systems, robotics boards, and recent Qualcomm reference designs. Chains encode board, revision/SKU, module, platform, and SoC fallbacks.

## Control Flow
Validation selects one `oneOf` branch and enforces exact item order. Many ChromeOS entries use revision-specific and newest-revision branches, so the schema doubles as a compatibility ABI table.

## State And Persistence
The schema stores immutable root platform identity only. Device resources, firmware links, and runtime state are handled by other DT nodes.

## Dependencies And Integration Points
It integrates with Qualcomm board DTS files, machine matching, platform quirks, ChromeOS boot-flow expectations, and SoC-specific driver matching.

## Risks
The file is high-risk for maintenance because the table is very large and many entries differ only by revision, SKU, or product-family fallback. Reordering or collapsing entries can break userspace, bootloader, or kernel board matching.

## Test Signals
`dtbs_check` over all Qualcomm DTBs is essential. Runtime signals include correct board name/platform match, firmware handoff, and SoC driver probing on representative boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/rda.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/rda.yaml

## Purpose
This root platform schema identifies RDA Micro 8810PL boards, specifically Orange Pi 2G-IoT and Orange Pi i96.

## Important APIs, Types, And Functions
The compatible list is a board enum (`xunlong,orangepi-2g-iot` or `xunlong,orangepi-i96`) followed by `rda,8810pl`.

## Control Flow
Validation enforces the root node name `/` and the ordered two-item compatible list.

## State And Persistence
The schema records immutable platform identity only.

## Dependencies And Integration Points
It integrates with RDA 8810PL DTS files and platform matching.

## Risks
New boards need explicit enum additions. Missing the SoC fallback prevents shared RDA support from matching.

## Test Signals
`dtbs_check` validates root compatible shape; boot-time platform probe confirms runtime use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/rda.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/realtek.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/realtek.yaml

## Purpose
This root platform schema catalogs Realtek RTD multimedia/NAS boards.

## Important APIs, Types, And Functions
It validates board-to-SoC compatible chains for RTD1195, RTD1293, RTD1295, RTD1296, RTD1395, RTD1501s, RTD1619, RTD1861b, and RTD1920s boards from Realtek, Synology, MeLE, ProBox2, Xnano, Zidoo, and Banana Pi.

## Control Flow
`oneOf` selects the SoC family branch and enforces exact compatible ordering.

## State And Persistence
It stores root platform identity only.

## Dependencies And Integration Points
It integrates with Realtek DTS files and platform matching for media and NAS SoCs.

## Risks
Realtek SoC names are close and product boards are varied; incorrect fallback can bind the wrong platform support.

## Test Signals
`dtbs_check` validates DTS root compatible lists; successful boot and media/storage peripheral probing validate runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/realtek.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/rockchip.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/rockchip.yaml

## Purpose
This large root platform schema catalogs Rockchip boards across RK30xx, RK31xx, RK32xx, RK33xx, RK35xx, RV11xx, PX30, RK3576, RK3588/RK3588S, and related families.

## Important APIs, Types, And Functions
It fixes `$nodename` to `/` and validates hundreds of exact compatible chains for SBCs, Chromebooks, tablets, handheld consoles, NAS/router boards, SOM/carrier combinations, EVBs, and vendor products. Many chains encode board variants, module fallbacks, Google ChromeOS revision chains, and SoC fallbacks such as `rockchip,rk3399`, `rk3566`, `rk3568`, `rk3576`, `rk3588`, and `rk3588s`.

## Control Flow
dt-schema selects one `oneOf` branch and enforces all compatible strings in order. Long ChromeOS and SOM chains preserve a hierarchy from exact revision through product family to generic SoC.

## State And Persistence
The schema stores immutable board identity only. Runtime resources and device state live in peripheral nodes and drivers.

## Dependencies And Integration Points
It integrates with Rockchip DTS files, platform matching, board-specific quirks, and SoC driver selection across a wide product set.

## Risks
The table is very large and high-churn. Similar product names, revision chains, and RK3588/RK3588S/RK3576 distinctions make accidental fallback changes a real compatibility risk.

## Test Signals
`dtbs_check` over Rockchip DTBs is essential. Runtime platform match, regulator/peripheral probe, and boot on representative boards validate the compatible chains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/rockchip.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/rockchip/pmu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/rockchip/pmu.yaml

## Purpose
This schema describes Rockchip Power Management Unit syscon blocks used to control SoC power domains, including CPU-core power.

## Important APIs, Types, And Functions
It selects Rockchip PMU compatibles for PX30, RK3066, RK3128, RK3288, RK3368, RK3399, RK3528, RK3562, RK3568, RK3576, RK3588, and RV1126. Compatible must be the SoC-specific PMU string followed by `syscon` and `simple-mfd`. Required properties are `compatible` and `reg`; optional child objects include `power-controller` and `reboot-mode`.

## Control Flow
The `select` block targets PMU compatibles. Validation requires a three-item compatible chain and one register resource, while permitting only declared child objects.

## State And Persistence
The DT records PMU registers and optional child functions. Runtime state is in syscon, power-domain, and reboot-mode drivers.

## Dependencies And Integration Points
It integrates with Rockchip power-domain controllers, reboot-mode handling, and syscon/simple-mfd infrastructure.

## Risks
Missing `simple-mfd` can prevent child devices from probing. Wrong PMU register range can affect power-domain control and reboot behavior.

## Test Signals
`dtbs_check` validates PMU nodes. Runtime signals include power-domain registration, suspend/resume behavior, and reboot-mode operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/rockchip/pmu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/samsung/samsung-boards.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/samsung/samsung-boards.yaml

## Purpose
This schema catalogs Samsung board-level root compatible chains across Exynos and S5PV210 platforms.

## Important APIs, Types, And Functions
It validates many board-to-SoC chains for phones, tablets, Chromebook/ODROID/Arndale platforms, Artik boards, SMDK boards, TM2, Trats, Gear, Rinato, and other Samsung or third-party products. Fallbacks include Exynos3/4/5/7/8/9 SoC identifiers and S5PV210.

## Control Flow
The schema selects one ordered `oneOf` compatible branch for each board or board family. It fixes the root node to `/`.

## State And Persistence
The root compatible list stores immutable board identity. Peripheral state is outside this schema.

## Dependencies And Integration Points
It integrates with Samsung DTS files, board quirks, and Exynos/S5P platform matching.

## Risks
Samsung product names and Exynos variants are numerous. Incorrect fallback ordering can break shared SoC support or board-specific quirks.

## Test Signals
`dtbs_check` across Samsung DTBs validates root compatibles; representative board boot validates platform matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/samsung/samsung-boards.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/samsung/samsung-secure-firmware.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/samsung/samsung-secure-firmware.yaml

## Purpose
This binding describes Samsung secure firmware nodes used as a conduit for secure monitor services.

## Important APIs, Types, And Functions
The schema requires `compatible = "samsung,secure-firmware"` and a single `reg` range.

## Control Flow
Validation is strict, requiring compatible and reg while rejecting additional properties.

## State And Persistence
The DT records secure firmware interface registers. Runtime state is held by secure firmware and kernel firmware-call glue.

## Dependencies And Integration Points
It integrates with Samsung/Exynos firmware interfaces and any platform code that uses secure services.

## Risks
Incorrect MMIO region can break secure calls or map unrelated registers. The strict schema requires updates before adding new firmware properties.

## Test Signals
`dtbs_check` validates the node. Runtime signals include successful secure firmware probe and secure-service calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/samsung/samsung-secure-firmware.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/samsung/samsung-soc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/samsung/samsung-soc.yaml

## Purpose
This schema validates Samsung SoC root-compatible fallback strings independent of specific boards.

## Important APIs, Types, And Functions
It fixes the root node to `/` and allows SoC-level compatibles including `samsung,s3c2416`, `s3c2440`, `s3c6410`, `s5pv210`, and multiple Exynos SoCs from Exynos3250 through ExynosAutoV920.

## Control Flow
The `compatible` property is an enum, so validation accepts one SoC string rather than a board fallback chain.

## State And Persistence
It records immutable SoC identity only.

## Dependencies And Integration Points
It complements `samsung-boards.yaml` and integrates with SoC-level DTS/platform matching.

## Risks
Board DTS files usually need board-level compatibles; using only a SoC enum loses board-specific identity. New SoCs require explicit enum additions.

## Test Signals
`dtbs_check` validates SoC root compatibles; platform boot confirms SoC-level matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/samsung/samsung-soc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/socionext/milbeaut.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/socionext/milbeaut.yaml

## Purpose
This root platform binding identifies Socionext Milbeaut M10V evaluation boards.

## Important APIs, Types, And Functions
The compatible list is `socionext,milbeaut-m10v-evb`, `socionext,sc2000a`.

## Control Flow
Validation is a single ordered compatible check with other root properties allowed.

## State And Persistence
The schema stores immutable platform identity only.

## Dependencies And Integration Points
It integrates with Milbeaut DTS files and platform matching for the SC2000A SoC.

## Risks
The binding covers one board chain; new boards or SoC variants need explicit updates.

## Test Signals
`dtbs_check` validates root compatible shape; boot confirms platform match.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/socionext/milbeaut.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/socionext/synquacer.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/socionext/synquacer.yaml

## Purpose
This root platform binding identifies Socionext SynQuacer developer boxes.

## Important APIs, Types, And Functions
It validates `socionext,developer-box`, `socionext,synquacer`.

## Control Flow
The schema enforces a two-item ordered compatible list and allows other root properties.

## State And Persistence
It records immutable board and SoC-family identity only.

## Dependencies And Integration Points
It integrates with SynQuacer DTS files and platform matching.

## Risks
Derivative boards need explicit compatible additions. Missing the generic fallback can break shared SynQuacer support.

## Test Signals
`dtbs_check` validates root compatibles; boot and platform driver probing confirm runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/socionext/synquacer.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/socionext/uniphier.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/socionext/uniphier.yaml

## Purpose
This schema catalogs Socionext UniPhier platform root compatibles.

## Important APIs, Types, And Functions
It validates compatible chains for LD4, Pro4, SLD8, Pro5, PXs2, LD6b, LD11, LD20, PXs3, NX1, and additional board prefixes such as Buffalo LinkStation and PXs3 reference boards, all falling back to the relevant `socionext,uniphier-*` SoC string.

## Control Flow
`oneOf` selects one SoC or board branch. Some branches are pure SoC strings and others are board-to-SoC chains.

## State And Persistence
It stores immutable platform identity only.

## Dependencies And Integration Points
It integrates with UniPhier DTS files and platform matching.

## Risks
Pure SoC branches validate less board identity. Board-specific additions should keep the SoC fallback to preserve generic driver matching.

## Test Signals
`dtbs_check` validates root compatible lists; boot-time platform and peripheral probing validate runtime integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/socionext/uniphier.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sp810.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sp810.yaml

## Purpose
This schema describes ARM SP810 system controllers, including clock selection support for multiple outputs.

## Important APIs, Types, And Functions
It requires `compatible = "arm,sp810"` plus `reg`. Optional clock-provider properties include `#clock-cells = <1>`, `clock-names` for `refclk`, `timclk`, and `apb_pclk`, `clocks` with matching inputs, and `assigned-clocks`/`assigned-clock-parents`.

## Control Flow
Validation requires the register range and constrains clock names and clock cell count. The example demonstrates an SP810 node acting as a selectable clock provider.

## State And Persistence
The DT describes system controller registers and clock input/output relationships. Runtime state is clock mux selection and register programming.

## Dependencies And Integration Points
It integrates with common clock framework, clock provider/consumer bindings, and ARM Versatile/RealView-style platform controllers.

## Risks
Clock name/order mismatches can produce wrong parent selection. Omitting `#clock-cells` prevents the node from being used as a provider.

## Test Signals
`dt_binding_check` validates examples; clock registration and consumer clock resolution validate runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sp810.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/spear.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/spear.yaml

## Purpose
This root platform schema catalogs ST SPEAr SoC evaluation boards.

## Important APIs, Types, And Functions
It validates board-to-SoC chains for SPEAr1310 EVB, SPEAr1340 EVB, SPEAr300 EVB, SPEAr310 EVB, SPEAr320 EVB, and SPEAr600 EVB.

## Control Flow
Validation uses a `oneOf` list of exact compatible chains and allows other root properties.

## State And Persistence
It records immutable platform identity only.

## Dependencies And Integration Points
It integrates with SPEAr DTS files and platform matching.

## Risks
The schema is narrow and board-specific. New boards need explicit additions and correct SoC fallback strings.

## Test Signals
`dtbs_check` validates compatible chains; platform boot confirms runtime matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/spear.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sprd/sprd.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sprd/sprd.yaml

## Purpose
This root platform schema catalogs Spreadtrum/Unisoc ARM boards.

## Important APIs, Types, And Functions
It validates compatible chains for SC9860G-1H10, SC9863A boards including Unisoc UMS512-1H10 and Samsung Galaxy A03 Core, Sharkl3, and UMS9620 boards.

## Control Flow
The root node name is `/`; `oneOf` selects the board/SoC branch and enforces exact ordering.

## State And Persistence
It stores immutable board and SoC identity only.

## Dependencies And Integration Points
It integrates with SPRD/Unisoc DTS files and platform matching.

## Risks
Vendor naming has changed over time, so board additions must preserve existing Spreadtrum/Unisoc compatible conventions. Wrong fallback can affect SoC driver matching.

## Test Signals
`dtbs_check` validates root compatible strings; boot and platform probe validate runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sprd/sprd.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sti.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sti.yaml

## Purpose
This schema catalogs STMicroelectronics STi set-top-box platform root compatibles.

## Important APIs, Types, And Functions
It validates compatible chains for STiH407 B2120, STiH410 B2120, and STiH418 B2199 boards, each followed by its SoC fallback.

## Control Flow
`oneOf` selects one ordered board-to-SoC branch and allows normal root properties.

## State And Persistence
The schema records immutable platform identity only.

## Dependencies And Integration Points
It integrates with STi DTS files and platform matching.

## Risks
Board names are similar across SoC generations; using the wrong fallback can break SoC-specific support.

## Test Signals
`dtbs_check` validates root compatible lists; boot-time SoC/platform match confirms integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sti.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/stm32/st,mlahb.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/stm32/st,mlahb.yaml

## Purpose
This binding describes the STM32 master AHB bus interconnect node used on STM32MP1 platforms.

## Important APIs, Types, And Functions
It requires a node name matching `ahb@...`, compatible `st,mlahb`, `st,stm32mp1-mlahb`, `simple-bus`, one `reg` range, and standard bus `#address-cells`, `#size-cells`, and `ranges`.

## Control Flow
Validation enforces the bus-compatible chain and requires address translation properties needed for child devices on the bus.

## State And Persistence
The DT describes an interconnect bus window and address translation. Runtime state is standard platform bus enumeration of children.

## Dependencies And Integration Points
It integrates with simple-bus handling, STM32MP1 address maps, and child peripheral bindings.

## Risks
Missing `ranges` or incorrect address/size cells can make child devices unreachable. Compatible order must include `simple-bus` for generic enumeration.

## Test Signals
`dtbs_check` validates bus shape; child device creation and probing validate runtime integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/stm32/st,mlahb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/stm32/st,stm32-syscon.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/stm32/st,stm32-syscon.yaml

## Purpose
This schema describes STM32 system configuration controllers, including syscfg/syscon blocks that may also provide clocks or firewall-related controls.

## Important APIs, Types, And Functions
Compatible branches include STM32F4 and STM32F7 syscfg with `syscon`, STM32MP157 syscfg with `syscon` and `simple-mfd`, and STM32MP25 syscfg variants. Properties include `reg`, optional clocks, `#clock-cells`, and child function nodes.

## Control Flow
Validation selects the variant branch and enforces strict properties. The schema allows declared child object behavior through `simple-mfd` when applicable.

## State And Persistence
The DT describes persistent syscfg registers and optional clock provider semantics. Runtime state is syscon/regmap and child-function driver state.

## Dependencies And Integration Points
It integrates with STM32 syscon users, common clock framework, simple-mfd child probing, and STM32 platform drivers.

## Risks
Variant-compatible order matters for syscon and MFD behavior. Missing clocks or clock cells can break consumers that rely on syscfg-derived clocks.

## Test Signals
`dtbs_check` validates syscfg nodes; syscon lookup, child probe, and clock registration validate runtime integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/stm32/st,stm32-syscon.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/stm32/stm32.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/stm32/stm32.yaml

## Purpose
This root platform schema catalogs STM32 boards and SoCs across STM32F, STM32H, STM32MP1, and STM32MP2 families.

## Important APIs, Types, And Functions
It validates many ordered compatible chains for Discovery/Nucleo/Eval boards, DH/Octavo/Engicam/PHYTEC/Seeed/Avenger96 boards, DHCOM/DHCOR SOMs, and STM32MP15/13/25 variants, ending in the appropriate ST SoC fallback such as `st,stm32mp157`, `st,stm32mp135`, or `st,stm32mp257`.

## Control Flow
The root node name is `/`; `oneOf` selects a precise board, module, and SoC fallback chain. Some branches are board families with intermediate SOM fallbacks.

## State And Persistence
It records immutable platform identity only.

## Dependencies And Integration Points
It integrates with STM32 board DTS files, machine selection, and SoC/board-specific driver quirks.

## Risks
SOM/carrier fallback ordering is the main maintenance risk. New boards should preserve module and SoC fallback hierarchy so common support still matches.

## Test Signals
`dtbs_check` validates root compatible lists; boot on representative STM32 boards validates runtime matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/stm32/stm32.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sunplus,sp7021.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sunplus,sp7021.yaml

## Purpose
This root platform binding identifies Sunplus SP7021 boards.

## Important APIs, Types, And Functions
It validates board strings `sunplus,sp7021-achip` and `sunplus,sp7021-demo-v3` followed by `sunplus,sp7021`.

## Control Flow
The root node name is `/`; validation selects the single SP7021 board branch and enforces compatible ordering.

## State And Persistence
It stores immutable board/SoC identity only.

## Dependencies And Integration Points
It integrates with Sunplus SP7021 DTS files and platform matching.

## Risks
New board variants require schema additions. Missing the SoC fallback can break shared SP7021 code.

## Test Signals
`dtbs_check` validates compatible chains; boot-time platform match confirms integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sunplus,sp7021.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sunxi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sunxi.yaml

## Purpose
This large root-node schema catalogs Allwinner/Sunxi boards across A-series, H-series, R-series, V-series, F-series, T-series, and related SoC families.

## Important APIs, Types, And Functions
It validates a very large set of board-to-SoC compatible chains for tablets, SBCs, TV boxes, routers, embedded modules, EVBs, Pine64/Orange Pi/Banana Pi/Libretech/Lichee/OLinuXino products, and many vendor boards. Fallbacks include SoC strings such as `allwinner,sun4i-a10`, `sun5i-a13`, `sun7i-a20`, `sun8i-*`, `sun9i-a80`, `sun20i-d1`, `sun50i-*`, and others.

## Control Flow
`oneOf` selects one exact compatible branch and enforces ordering from specific board or module through generic SoC fallback. `additionalProperties: true` leaves other root-node fields to generic validation.

## State And Persistence
The schema stores immutable platform identity only. Peripheral resources and runtime state live in child nodes and drivers.

## Dependencies And Integration Points
It integrates with the broad Sunxi DTS tree, board-specific quirks, and Allwinner SoC/platform matching.

## Risks
The catalog is large and high-churn. Similar board names and multiple SoC generations make wrong fallback chains likely when adding entries. Maintaining stable compatibles is important because bootloaders and kernels rely on them.

## Test Signals
`dtbs_check` across Sunxi DTBs is the primary validation. Runtime signals include correct board detection, regulator/peripheral initialization, and successful boot on representative boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sunxi.yaml -->
