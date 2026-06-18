# subset-b-000569 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dither.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dither.yaml

### Purpose
This YAML schema describes MediaTek display DITHER blocks, which reduce visible color-depth loss by approximating unavailable colors. The node is part of the MediaTek display pipeline and is expected to sit beside the central MMSYS configuration node.

### Important APIs, Types, And Functions
The binding API is the node contract: SoC-specific `compatible` strings, one MMIO `reg`, one interrupt, a power domain, one DITHER clock, optional `mediatek,gce-client-reg`, and optional graph `ports`. The graph exposes `port@0` as input, usually from POSTMASK or GAMMA, and `port@1` as output toward DSC, DP_INTF, DSI, LVDS, or another pipeline block.

### Control Flow
There is no executable control flow. Validation branches through `compatible.oneOf`: `mt8183` can stand alone, while several later SoCs must list their SoC string followed by the `mediatek,mt8183-disp-dither` fallback. Graph validation requires both input and output ports when `ports` is present.

### State, Persistence, And Dependencies
The persistent state is the devicetree description consumed at boot. Dependencies are MMSYS placement, power-domain providers, clock providers, interrupt controllers, graph endpoints, and optionally GCE command-engine metadata.

### Integration Points
The DRM/MediaTek display driver uses this node to discover the dither hardware and connect it into the component graph. GCE registration lets command queues program the block without synchronous CPU register writes.

### Risks
Incorrect fallback compatibles can bind the wrong register layout. Missing graph endpoints can leave a valid MMIO node disconnected from the display route. GCE tuple mistakes are hard to catch by schema because the referenced subsys IDs are chip-specific.

### Test Signals
Run `dt_binding_check` and SoC DTS checks for required `reg`, interrupt, power, and clock cells. Runtime signals are successful DRM component bind, valid graph endpoint resolution, and working low-bpp output without color-band artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dither.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dp.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dp.yaml

### Purpose
This schema defines MediaTek DisplayPort and embedded DisplayPort transmitter nodes. It distinguishes DP and eDP because DP may expose audio while eDP lacks some external DP features.

### Important APIs, Types, And Functions
The node API consists of `compatible`, one `reg`, one interrupt, required graph `ports`, and `max-linkrate-mhz`. Optional fields include `nvmem-cells` named `dp_calibration_data`, `power-domains`, `aux-bus`, and `#sound-dai-cells` for DP audio. `port@0` is the input from `dp_intf`; `port@1` is the output endpoint with required `data-lanes`.

### Control Flow
Schema branching is driven by compatible. The `allOf` reference pulls in sound DAI common rules, then removes `#sound-dai-cells` for eDP-compatible nodes. Link capabilities are constrained declaratively through `max-linkrate-mhz` and output endpoint `data-lanes`.

### State, Persistence, And Dependencies
The persistent data is calibration/link capability information in devicetree and optional nvmem. Dependencies include power domains, the DP AUX bus schema, graph/video interface schemas, nvmem providers, and sound DAI schema rules.

### Integration Points
The MediaTek DP driver uses the graph edge from the display pipeline and the output edge to a connector, bridge, Type-C mux, or panel path. Audio integration is exposed only for DP-compatible transmitters through the DAI cell contract.

### Risks
Using an eDP compatible with audio cells, or a DP compatible without expected audio/AUX handling, creates platform description drift. Invalid lane arrays or optimistic link rates can pass board review but fail link training.

### Test Signals
Use `dt_binding_check` for DAI, AUX, lane, and link-rate validation. Runtime signals are AUX transactions, nvmem calibration readout, stable link training at declared rates, and audio DAI registration only on DP variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dpi.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dpi.yaml

### Purpose
This binding documents the MediaTek DPI parallel/RGB display output controller. DPI converts the internal display pipeline into a parallel display interface, often feeding HDMI, LVDS, or external bridge hardware.

### Important APIs, Types, And Functions
The schema exposes SoC-specific `compatible` strings, MMIO `reg`, interrupts, clocks and `clock-names`, power domains, optional pinctrl, and graph `ports`. It also integrates common display timing and graph contracts through endpoint connectivity.

### Control Flow
The binding is declarative. Compatible entries select the hardware generation, while the required property set ensures the driver has register, clock, interrupt, and power resources before probing. Endpoint traversal controls data-flow topology from an upstream display block to the downstream bridge or connector.

### State, Persistence, And Dependencies
State persists as devicetree hardware description. Dependencies include clock and power-domain providers, interrupt controllers, pinctrl if board routing needs it, graph bindings, and downstream bridge or connector bindings.

### Integration Points
The MediaTek DRM component framework uses the node to bind the DPI encoder and connect it to adjacent display blocks. Downstream bridge/connector nodes use `remote-endpoint` links to form a complete DRM display path.

### Risks
Clock-name ordering is a common failure mode because schemas validate names but driver code depends on exact resources. Incorrect graph endpoints can make the controller probe but produce no active connector. Board-specific pinctrl omissions can look like display timing failures.

### Test Signals
`dt_binding_check` should validate compatible/resource cardinality and graph syntax. Runtime tests are DPI probe, clock enable sequencing, bridge attachment, mode-set success, and pixel output on representative boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dpi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dsc.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dsc.yaml

### Purpose
This schema defines MediaTek Display Stream Compression blocks. DSC compresses display stream slices before high-bandwidth output links such as DSI or DisplayPort.

### Important APIs, Types, And Functions
The node API includes supported `compatible` strings, one `reg`, one interrupt, power-domain and clock resources, optional `mediatek,gce-client-reg`, and graph `ports`. The ports describe input from an upstream block such as DITHER/MERGE and output to the next display interface.

### Control Flow
Schema control is compatible-driven and graph-driven. Validation accepts defined SoC/fallback compatible combinations, constrains resources to single MMIO/clock/interrupt entries, and requires the graph shape when `ports` is supplied.

### State, Persistence, And Dependencies
The devicetree node persists the hardware instance identity and command-queue register window. Dependencies include MMSYS topology, GCE command engine definitions, clock/power providers, interrupt controllers, and graph bindings.

### Integration Points
MediaTek DRM uses DSC components in multi-stage display pipelines, especially high-resolution DSI/DP modes where compression is needed. The block is coordinated with slice-producing upstream blocks and compressed-stream consumers.

### Risks
DSC blocks are sensitive to topology. A valid node with wrong endpoint routing can lead to bandwidth or mode failures. Fallback-compatible mistakes may hide register-layout differences. Missing GCE metadata can reduce command-queue support for atomic updates.

### Test Signals
Use binding checks for resource and graph validation. Runtime signals are component bind, command-queue programming where available, successful DSC-enabled modes, and correct behavior across compressed and uncompressed display routes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dsc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dsi.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dsi.yaml

### Purpose
This binding describes MediaTek MIPI DSI host controllers. The controller receives pixels from the display pipeline and drives a DSI panel or bridge.

### Important APIs, Types, And Functions
The schema defines the `compatible` set, `reg`, interrupts, clocks and `clock-names`, PHY and power resources, optional resets, and graph `ports`. It also participates in the common DSI controller and video-interface contracts through endpoints and child panel/bridge topology.

### Control Flow
Validation is declarative. Compatible strings select the supported host variant. Required resources make the host probeable, while graph ports determine pipeline input and downstream DSI device connectivity.

### State, Persistence, And Dependencies
Persistent state is the boot-time hardware description: register range, clocks, PHY relation, power domain, and endpoint graph. Dependencies include DSI PHY nodes, clock/reset/power providers, interrupt controllers, graph bindings, and any downstream panel or bridge schema.

### Integration Points
The MediaTek DRM DSI driver binds as both an encoder/bridge participant and a MIPI DSI host. Endpoint links connect it to upstream display components and panel/bridge consumers.

### Risks
DSI failures often stem from resource ordering or missing PHY/clock relationships. A graph that validates but points to the wrong upstream interface can leave the host active with no pixels. Dual-DSI or split pipelines need careful endpoint pairing.

### Test Signals
`dt_binding_check` should cover required resources and graph syntax. Runtime tests include host registration, panel attachment, mode set, lane/PLL setup, command transfer, and suspend/resume power sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,dsi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,ethdr.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,ethdr.yaml

### Purpose
This schema documents the MediaTek ETHDR display block used for HDR and enhanced display processing in VDOSYS pipelines. It composes multiple inputs and prepares output for later display stages.

### Important APIs, Types, And Functions
The binding exposes `compatible`, multiple register regions or named resources where required by the source schema, interrupts, power domains, clocks, optional GCE client registers, and graph `ports`. Its graph model is richer than simple pass-through blocks because ETHDR can receive multiple overlay/mixer inputs and emit processed output.

### Control Flow
There is no runtime control flow in the file. Validation constrains the hardware description by compatible and by required resource cardinality. Graph ports encode display data-flow ordering, while GCE metadata encodes the command-programming path.

### State, Persistence, And Dependencies
State persists as DT properties consumed by DRM and command-queue drivers. Dependencies include VDOSYS/MMSYS integration, power and clock domains, interrupt routing, graph schemas, and GCE bindings.

### Integration Points
ETHDR sits between overlay/mixer stages and output blocks in MediaTek display pipelines. It integrates with atomic commit programming through the same display component and GCE mechanisms used by other MediaTek display processors.

### Risks
The main risk is topology mismatch: ETHDR processing requirements differ from simpler one-input blocks. Missing or misordered clocks/registers can pass casual review but fail probe. The padding binding explicitly notes ETHDR-related alignment needs, so pipeline width handling should be reviewed together.

### Test Signals
Binding checks should verify all required resources and graph ports. Runtime signals are successful component binding, HDR path enablement, multi-input route validation, and display modes that exercise ETHDR with and without padding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,ethdr.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,gamma.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,gamma.yaml

### Purpose
This binding describes MediaTek GAMMA color-correction blocks. The block applies gamma lookup/transformation in the display pipeline before later stages such as DITHER or POSTMASK.

### Important APIs, Types, And Functions
The API includes SoC/fallback `compatible` entries, one `reg`, one interrupt, one power-domain reference, one clock, optional `mediatek,gce-client-reg`, and graph `ports`. `port@0` is the input, and `port@1` sends corrected pixels to the next pipeline block.

### Control Flow
The schema validates compatible fallback order and required resources. Port validation is declarative and ensures the graph has both input and output when topology is expressed.

### State, Persistence, And Dependencies
The persistent state is the DT node and graph. Dependencies include MMSYS sibling placement, display clock and power domains, interrupt controller routing, graph endpoint bindings, and optional GCE command-engine definitions.

### Integration Points
MediaTek DRM discovers the GAMMA component from this node and inserts it into the display route. GCE metadata allows command queue programming of gamma registers during atomic display updates.

### Risks
Color blocks can appear optional in topology, so missing endpoints may silently bypass expected processing. Incorrect compatible fallback can select wrong LUT capabilities. Bad GCE register offsets can affect runtime programming without schema-visible type errors.

### Test Signals
Use `dt_binding_check` plus DTS validation for required properties. Runtime signals are component bind, gamma LUT programming, visible color transform changes, and correct ordering relative to DITHER/POSTMASK in DRM pipeline dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,gamma.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,hdmi-ddc.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,hdmi-ddc.yaml

### Purpose
This schema defines the MediaTek HDMI DDC I2C controller used to access HDMI DDC pins for EDID and related display transactions.

### Important APIs, Types, And Functions
The node contract is small: `compatible` for supported SoCs, one `reg`, one interrupt, one clock, and `clock-names = "ddc-i2c"`. `additionalProperties: false` keeps the node limited to the DDC controller resources.

### Control Flow
There is no executable flow. The schema accepts only listed compatible values and requires the register, interrupt, and clock resources needed by the I2C/DDC driver.

### State, Persistence, And Dependencies
The persistent hardware description names the DDC controller and its clock. Dependencies include the peripheral clock provider, interrupt controller, and HDMI connector/encoder nodes that reference the DDC bus.

### Integration Points
The HDMI encoder or connector uses this I2C adapter for EDID reads. It is separate from the HDMI transmitter node so board descriptions can connect DDC cleanly through connector properties.

### Risks
The controller register region is small, so incorrect size or base addresses are easy to overlook. A wrong clock-name breaks driver lookup. HDMI may probe but lack EDID if this node or connector link is wrong.

### Test Signals
Run `dt_binding_check` for required fields. Runtime signals are DDC I2C adapter creation, successful EDID reads, hotplug display mode discovery, and no clock lookup errors during HDMI probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,hdmi-ddc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,hdmi.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,hdmi.yaml

### Purpose
This binding describes legacy MediaTek HDMI encoders capable of producing HDMI 1.4a or MHL 2.0 signals from a parallel input.

### Important APIs, Types, And Functions
The schema defines `compatible`, one `reg`, one interrupt, four clocks named `pixel`, `pll`, `bclk`, and `spdif`, one HDMI PHY named `hdmi`, `mediatek,syscon-hdmi`, and graph `ports`. `port@0` receives DPI output, while `port@1` connects to an HDMI connector or external bridge.

### Control Flow
Validation is fixed-resource and graph-oriented. The required set ensures the encoder has clocks, PHY, syscon, and two display endpoints. No conditional runtime logic is implemented in the YAML.

### State, Persistence, And Dependencies
Persistent state is the DT hardware contract. Dependencies include MMSYS syscon registers, HDMI PHY, clock providers, interrupt routing, graph bindings, connector/bridge nodes, and often the separate HDMI DDC node.

### Integration Points
The MediaTek HDMI driver binds this encoder into DRM through its DPI input and connector/bridge output. Audio-related clocks support S/PDIF and bit-clock paths.

### Risks
Clock order and names are critical. Missing `mediatek,syscon-hdmi` prevents register integration with system configuration. The output endpoint description allows connector or bridge targets, so board DTS must match the actual DDC and hotplug topology.

### Test Signals
Binding checks should validate required clocks, PHY, syscon, and ports. Runtime signals are PHY attach, EDID over DDC, hotplug detection, HDMI modeset, and audio clock availability where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,hdmi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,merge.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,merge.yaml

### Purpose
This schema defines MediaTek MERGE blocks, which combine two slice-per-line inputs into one side-by-side output for split display pipelines.

### Important APIs, Types, And Functions
The node exposes SoC/fallback `compatible` strings, one `reg`, one interrupt, one power-domain reference, a defined set of clocks, optional `mediatek,gce-client-reg`, and graph `ports`. Ports describe one or more input endpoints and an output endpoint to the next display block.

### Control Flow
The schema validates compatible choices and resource cardinality. The functional data flow is represented by graph endpoints rather than code: inputs converge at MERGE and output continues downstream.

### State, Persistence, And Dependencies
The DT node persists the register, clock, power, interrupt, command-queue, and graph topology. Dependencies include MMSYS/VDOSYS routing, GCE bindings, graph schemas, and upstream slice-producing blocks.

### Integration Points
MediaTek DRM uses MERGE when dual/sliced pipelines must become a single stream before later blocks. It is relevant to high-resolution panels and display paths using split or DSC blocks.

### Risks
MERGE is topology-sensitive. A graph that omits one slice or points both endpoints to the same source can validate poorly at runtime even if schema constraints pass. Clock lists can differ by SoC generation.

### Test Signals
Use schema checks and board DTS graph validation. Runtime tests should exercise split-to-merged modes, command-queue programming, dual-pipeline atomic commits, and output correctness at high resolutions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,merge.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,mt8195-hdmi-ddc.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,mt8195-hdmi-ddc.yaml

### Purpose
This schema documents the MT8195-series HDMI DDC block. It models the DDC channel used by MT8195 HDMI transmitters for EDID and related I2C transactions.

### Important APIs, Types, And Functions
The binding requires `compatible`, one clock, and a power-domain reference. Unlike older HDMI DDC bindings, this MT8195 schema does not define separate `reg` or interrupt properties in the visible contract, matching the SoC integration style.

### Control Flow
Validation accepts the MT8195-series compatible and required power/clock resources. There is no runtime control flow in the schema.

### State, Persistence, And Dependencies
The persistent state is the DDC resource relationship in devicetree. Dependencies include the HDMI transmitter, display clock provider, PM domain provider, and connector/bridge nodes that need EDID access.

### Integration Points
This node is paired with the MT8195 HDMI TX binding. It supplies the DDC service path used during connector discovery and mode enumeration.

### Risks
Because the contract is sparse, board integration errors may surface only at runtime. Missing power-domain linkage can make DDC fail while the HDMI node itself appears valid. Confusing this binding with older `mediatek,hdmi-ddc.yaml` can add invalid properties.

### Test Signals
Use `dt_binding_check` for the MT8195 DDC node and runtime EDID reads through the HDMI connector. Probe logs should show clock and power-domain acquisition without legacy register/interrupt assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,mt8195-hdmi-ddc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,mt8195-hdmi.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,mt8195-hdmi.yaml

### Purpose
This schema defines the MT8195-series HDMI-TX encoder. It is the newer HDMI transmitter binding for MT8195 display pipelines.

### Important APIs, Types, And Functions
The API includes `compatible`, `reg`, interrupts, clocks and names, power domains, graph `ports`, and an `allOf` reference to `sound/dai-common.yaml`. The input port is fed by a display pipeline component, and the output port connects to a connector or bridge.

### Control Flow
The schema is declarative. Required resources must be present before the transmitter can bind. The `allOf` sound reference validates HDMI audio DAI properties when present.

### State, Persistence, And Dependencies
Persistent state is the hardware description for MMIO, interrupts, clocks, PM domains, graph links, and optional audio DAI metadata. Dependencies include display clock/power providers, graph schemas, connector/bridge nodes, the MT8195 HDMI DDC binding, and sound DAI common rules.

### Integration Points
The MT8195 HDMI driver participates in DRM as an encoder/bridge and can expose audio through the sound DAI path. It consumes display input and publishes an output edge to board-level HDMI connectivity.

### Risks
The MT8195 binding differs from older MediaTek HDMI, so copying legacy PHY/syscon/DDC assumptions can create invalid or nonfunctional nodes. Audio properties must remain aligned with the DAI schema.

### Test Signals
Validate with `dt_binding_check`. Runtime checks include HDMI TX probe, DDC/EDID operation through its paired DDC node, connector modeset, power-domain transitions, and optional DAI registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,mt8195-hdmi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,od.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,od.yaml

### Purpose
This binding describes MediaTek display overdrive blocks. OD adjusts pixel transitions to improve perceived panel response.

### Important APIs, Types, And Functions
The schema exposes `compatible`, one MMIO `reg`, one interrupt, clocks, optional `mediatek,gce-client-reg`, and graph `ports`. The graph represents input from an upstream display block and output to the next stage.

### Control Flow
Validation is based on compatible values, required resources, and graph shape. The file contains no executable algorithms; overdrive behavior is implemented in the driver and hardware.

### State, Persistence, And Dependencies
The DT node persists the register window, interrupt, clock, command-queue, and pipeline connectivity. Dependencies include MediaTek display topology, clock providers, interrupt controllers, GCE definitions, and graph bindings.

### Integration Points
The OD component integrates with the MediaTek DRM component framework and can be programmed as part of display atomic updates when present in a route.

### Risks
The title has a spelling error in source (`overdirve`), but the schema contract is unaffected. Graph mistakes can place OD in an unsupported route. Optional GCE data must match the chip register map.

### Test Signals
Run schema validation for resource and endpoint structure. Runtime signals are component bind, overdrive register programming, route enablement with OD in the path, and no visual artifacts when OD is enabled or bypassed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,od.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,ovl-2l.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,ovl-2l.yaml

### Purpose
This schema documents MediaTek two-layer overlay blocks. OVL-2L composites a smaller number of memory-backed layers than the full OVL block.

### Important APIs, Types, And Functions
The binding defines compatible/fallback strings, `reg`, one interrupt, power-domain and clock resources, `iommus` for memory fetch, optional `mediatek,gce-client-reg`, and graph `ports`. The output port feeds the next display pipeline stage such as RDMA, COLOR, or WDMA.

### Control Flow
The schema validates SoC compatibility and mandatory memory/display resources. Data-flow is encoded by graph endpoints; memory access is encoded by the IOMMU phandle.

### State, Persistence, And Dependencies
State persists in devicetree as the OVL-2L instance identity, memory master, clock/power resources, and route connectivity. Dependencies include IOMMU bindings, MMSYS/VDOSYS, clocks, PM domains, interrupts, GCE, and graph bindings.

### Integration Points
The MediaTek DRM driver uses OVL-2L as an overlay plane source in display pipelines. IOMMU integration is required for framebuffer access.

### Risks
Missing or wrong `iommus` can cause DMA faults rather than schema-visible display failures. Fallback-compatible errors can select wrong layer capabilities. Incorrect graph routing can send output to unsupported downstream blocks.

### Test Signals
Use binding checks and DTS IOMMU validation. Runtime signals are plane enablement, framebuffer scanout through IOMMU, command-queue updates, and correct blend behavior with one or two active layers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,ovl-2l.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,ovl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,ovl.yaml

### Purpose
This binding describes MediaTek full overlay blocks. OVL reads memory-backed layers and alpha-blends them into the display pipeline.

### Important APIs, Types, And Functions
The schema includes many SoC/fallback compatible combinations, one `reg`, one interrupt, power-domain, one OVL clock, required `iommus`, optional GCE register metadata, and optional graph `ports`. `port@0` is input from MMSYS or VDOSYS routing; `port@1` outputs to COLOR, RDMA, or WDMA.

### Control Flow
Compatible `oneOf` entries encode hardware-generation fallback rules, including display and MDP3 OVL variants. Required IOMMU and clock/power resources ensure the driver has memory and display access. Graph ports encode pipeline flow.

### State, Persistence, And Dependencies
Persistent state is the DT description of blending hardware and its memory-master identity. Dependencies include MediaTek IOMMU, display clock and PM domains, interrupts, GCE, graph schemas, and MMSYS placement.

### Integration Points
OVL is a primary DRM plane-composition block in MediaTek display pipelines. It can feed display output or WDMA capture paths.

### Risks
Confusing display OVL and MDP3 OVL compatibles may select wrong driver capabilities. IOMMU master IDs are SoC-specific and critical. Pipeline routes with OVL-to-WDMA versus OVL-to-display need explicit graph review.

### Test Signals
Binding checks should catch required IOMMU and resources. Runtime tests include multi-plane blending, alpha formats, DMA/IOMMU fault absence, GCE-assisted atomic commits, and routes to both display and WDMA where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,ovl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,padding.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,padding.yaml

### Purpose
This schema defines MediaTek display Padding blocks. Padding adds pixels to layer width/height with specified colors, especially to satisfy VDOSYS1 mixer alignment requirements.

### Important APIs, Types, And Functions
The binding requires compatible/fallback strings, one `reg`, one power domain, one clock, and required `mediatek,gce-client-reg`. The GCE phandle array identifies command engine, subsys ID, register offset, and register size.

### Control Flow
The YAML has no executable flow. Compatible selection distinguishes display padding and MDP3 padding. Required GCE metadata reflects that this block is command-queue programmed.

### State, Persistence, And Dependencies
Persistent state is the hardware instance plus GCE programming window. Dependencies include VDOSYS1/MMSYS, clock and PM domain providers, and GCE dt-bindings.

### Integration Points
Padding integrates with MediaTek display paths that feed mixers requiring two-pixel or four-pixel alignment. It is especially relevant when ETHDR is enabled.

### Risks
The source description warns that bypass mode still requires registers cleared to zero; otherwise undefined behavior can occur. Since no graph ports are modeled here, route correctness depends on surrounding MMSYS configuration and driver data.

### Test Signals
Run binding checks for required GCE tuple and resources. Runtime validation should include odd-width layers, ETHDR-enabled paths requiring four-pixel alignment, bypass-mode register clearing, and command-queue programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,padding.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,postmask.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,postmask.yaml

### Purpose
This schema describes MediaTek POSTMASK display blocks, which apply post-processing masks in the display pipeline before later color or output stages.

### Important APIs, Types, And Functions
The binding exposes SoC/fallback `compatible` values, one `reg`, one interrupt, power-domain and clock resources, optional `mediatek,gce-client-reg`, and graph `ports`. Ports describe input from upstream display processing and output to blocks such as DITHER.

### Control Flow
The schema validates compatible fallback order, required resources, and optional graph topology. There is no imperative control flow.

### State, Persistence, And Dependencies
The DT node persists MMIO, interrupt, power, clock, GCE, and graph data. Dependencies include MMSYS/VDOSYS, GCE definitions, graph schemas, and the display component driver.

### Integration Points
POSTMASK is inserted into MediaTek DRM routes as a display component and can be programmed through normal atomic update paths, including GCE where present.

### Risks
Since POSTMASK often sits between other color-processing blocks, wrong endpoint ordering can alter visual output while still producing a picture. GCE offsets and compatible fallback must match the SoC register map.

### Test Signals
Use `dt_binding_check` and DTS graph validation. Runtime signals include component bind, route construction with POSTMASK between expected neighbors, mask programming, and successful suspend/resume of power and clock resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,postmask.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,rdma.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,rdma.yaml

### Purpose
This binding documents MediaTek display RDMA blocks. RDMA reads pixels from memory or pipeline sources and forwards them to display output processing.

### Important APIs, Types, And Functions
The schema defines compatible/fallback strings, one `reg`, one interrupt, power-domain and clock resources, optional `iommus`, optional `mediatek,gce-client-reg`, and graph `ports`. Ports connect RDMA input and output within the MediaTek display graph.

### Control Flow
Compatible `oneOf` entries encode SoC generations and fallback rules. Required register/interrupt/power/clock resources validate probeability, while IOMMU and graph properties encode optional memory and route integration.

### State, Persistence, And Dependencies
Persistent state includes the RDMA instance identity, command-queue window, memory-master relation, and route endpoints. Dependencies include clock/power domains, interrupt routing, optional IOMMU, GCE, graph bindings, and MMSYS configuration.

### Integration Points
RDMA is a central MediaTek DRM component for scanout paths. It can bridge memory-backed data and downstream encoders such as DPI/DSI/DP via the component graph.

### Risks
RDMA participates in both direct memory read and pipeline forwarding paths, so missing IOMMU or graph properties can fail differently by route. Compatible fallback mismatches can break register programming.

### Test Signals
Validation should include schema checks for required resources and DTS graph edges. Runtime tests are scanout from memory, route enablement to each output type, IOMMU fault absence, interrupt delivery, and GCE atomic updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,rdma.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,split.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,split.yaml

### Purpose
This schema defines MediaTek SPLIT blocks, which divide one display stream into multiple outputs for split-panel or multi-pipeline operation.

### Important APIs, Types, And Functions
The binding includes `compatible`, one `reg`, one interrupt, power-domain and clock resources, optional `mediatek,gce-client-reg`, and graph `ports`. The graph describes one input and multiple possible downstream outputs.

### Control Flow
Validation is compatible/resource based. Display data flow is declarative: incoming pixels are split through graph endpoints toward downstream pipeline halves.

### State, Persistence, And Dependencies
DT persists the split block resources and topology. Dependencies include MMSYS/VDOSYS routing, GCE, clock/power providers, interrupt controllers, graph bindings, and downstream paired display components.

### Integration Points
MediaTek DRM uses SPLIT in dual-pipeline modes where one logical display stream must be processed by parallel hardware paths before merge, DSC, DSI, or panel output.

### Risks
Split pipelines are highly order-sensitive. A missing endpoint may only affect high-resolution or dual-link modes. GCE metadata and compatible fallback must match the SoC to keep atomic commits synchronized.

### Test Signals
Use binding checks and graph validation. Runtime tests should cover split-panel modes, dual-output route construction, atomic commits across both halves, and fallback to non-split modes where the hardware supports it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,split.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,ufoe.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,ufoe.yaml

### Purpose
This binding documents MediaTek UFOe display compression blocks. UFOe compresses display streams before downstream output interfaces.

### Important APIs, Types, And Functions
The schema defines compatible strings, one `reg`, one interrupt, one power-domain reference, one clock, optional graph `ports`, and optional `mediatek,gce-client-reg`. The ports connect input from an upstream display block and output to the next block.

### Control Flow
The schema validates compatible/resource cardinality and graph port requirements when `ports` is present. Compression behavior is runtime driver/hardware behavior, not implemented in YAML.

### State, Persistence, And Dependencies
Persistent data is the DT node with MMIO, interrupt, power, clock, command-queue, and graph information. Dependencies include MMSYS, GCE, graph schemas, and downstream display interface bindings.

### Integration Points
UFOe integrates with MediaTek DRM as a compression component in display routes that require reduced bandwidth before DSI or other outputs.

### Risks
Compression blocks must match downstream capabilities. A route that enables UFOe toward an unsupported sink can fail modeset. Optional graph or GCE omissions can leave runtime behavior different from intended pipeline design.

### Test Signals
Run `dt_binding_check` and board graph validation. Runtime signals are component bind, compressed route modeset, command-queue programming, and display correctness on modes requiring UFOe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,ufoe.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,wdma.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,wdma.yaml

### Purpose
This binding describes MediaTek WDMA blocks, which write display pipeline output back to memory.

### Important APIs, Types, And Functions
The node API includes compatible/fallback strings, one `reg`, one interrupt, power-domain and clock resources, optional `mediatek,gce-client-reg`, and memory-related integration through the platform. WDMA receives data from display pipeline components and writes it to memory buffers.

### Control Flow
The YAML validates the fixed resource set and compatible choices. Runtime writeback sequencing is handled by the DRM/MediaTek driver and hardware.

### State, Persistence, And Dependencies
The persistent devicetree state identifies the writeback hardware, clock/power/interrupt resources, and optional GCE programming window. Dependencies include memory/IOMMU setup in the SoC, MMSYS routing, clocks, PM domains, interrupts, and GCE definitions.

### Integration Points
WDMA integrates with MediaTek DRM writeback or memory-output paths and can be a downstream target from OVL or RDMA depending on the SoC pipeline.

### Risks
Writeback paths can be under-tested compared with scanout. Missing memory/IOMMU integration may appear as DMA faults. GCE register tuple mistakes affect asynchronous writeback programming.

### Test Signals
Binding checks should validate required resources. Runtime signals include WDMA probe, writeback job completion interrupts, correct memory output contents, DMA fault absence, and command-queue operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/mediatek/mediatek,wdma.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/dp-controller.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/dp-controller.yaml

### Purpose
This schema defines Qualcomm MSM DisplayPort host controllers compatible with VESA DisplayPort. It covers DP, eDP, SST, and MST-capable variants across many SoCs.

### Important APIs, Types, And Functions
The node API includes layered `compatible` choices, `reg` blocks for AHB/AUX/link/stream/MST register windows, interrupts, `clocks` and `clock-names`, one DP PHY, power-domain, optional OPP table, optional `aux-bus`, optional audio `#sound-dai-cells`, deprecated top-level `data-lanes`, and graph `ports`. Output endpoint properties include `data-lanes` and `link-frequencies`.

### Control Flow
The `allOf` chain is the core logic. eDP variants disallow sound DAI cells. Some DP variants require either `aux-bus` or audio cells, while older variants disallow `aux-bus` and require audio cells. Additional conditionals set register and clock counts for SST-only, two-stream MST, four-stream MST, and Glymur variants.

### State, Persistence, And Dependencies
Persistent state is the DT description of controller register windows, PHY link, clocks, power, OPP, and graph. Dependencies include DP AUX bus, sound DAI schema, video-interface endpoints, PHY providers, display clock controllers, PM domains, and MDSS interrupt parents.

### Integration Points
The msm DP driver consumes this node under MDSS, connects to DPU output through `port@0`, and exposes a connector, Type-C mux, bridge, or PHY-linked output through `port@1`.

### Risks
The schema uses `clocks-names` in conditionals while the property is `clock-names`; this typo weakens conditional validation for clock-name counts. Deprecated compatible fallbacks and top-level lane properties can preserve old DTS but should not be copied. MST register/clock cardinality must match the specific controller instance.

### Test Signals
Run `dt_binding_check` with examples for SST, eDP, MST, and AUX/audio variants. Runtime signals include DP probe, PHY attach, AUX transactions, link training at declared frequencies, audio registration for DP-only variants, and MST stream bring-up where declared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/dp-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/dpu-common.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/dpu-common.yaml

### Purpose
This common schema defines shared properties for Qualcomm DPU display-controller nodes. SoC-specific DPU bindings reference it to avoid duplicating interrupt, power, OPP, and port requirements.

### Important APIs, Types, And Functions
The common contract includes interrupt resources, one power domain, optional `operating-points-v2`/`opp-table`, and graph `ports`. It defines required baseline resources that SoC-specific bindings extend with compatible, register, clock, and clock-name details.

### Control Flow
The file is selected only by explicit `$ref`; it is not a standalone compatible match. Validation flow is composition: SoC-specific schemas import this common shape, then add stricter resource cardinality and `unevaluatedProperties: false`.

### State, Persistence, And Dependencies
State persists in the final composed devicetree node. Dependencies include graph bindings, OPP bindings, PM domains, interrupt parent configuration, and SoC-specific DPU schemas.

### Integration Points
Every referenced Qualcomm DPU binding relies on this file for shared DRM display-controller requirements. It standardizes the graph output ports used to connect DPU interfaces to DSI, DP, HDMI, or other encoders.

### Risks
Changes here have broad blast radius because many SoC DPU bindings inherit it. Too-loose common constraints can let bad DTS pass; too-strict constraints can break valid SoC-specific variants.

### Test Signals
Run binding checks for all SoC-specific DPU schemas that reference this file. Regression signals include unchanged validation for DPU interrupt, power-domain, OPP, and ports across MSM8998, QCM2290, SC7180, SC7280, and later families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/dpu-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/dsi-controller-main.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/dsi-controller-main.yaml

### Purpose
This schema defines Qualcomm MDSS DSI controller nodes across many Snapdragon and related SoCs. It models both the host controller and graph connections to DPU and panels/bridges.

### Important APIs, Types, And Functions
The node contract includes SoC-specific compatible plus `qcom,mdss-dsi-ctrl` fallback, one `reg` named `dsi_ctrl`, one interrupt, clocks and names, one DSI PHY, optional syscon for DSIv2, dual-DSI booleans, assigned clocks/parents, power-domain/OPP, regulator supplies, and graph `ports`. Endpoint properties include `data-lanes` and `qcom,te-source`.

### Control Flow
The schema imports the generic DSI controller binding, then uses many `if` branches keyed by compatible to enforce platform-specific clock counts and exact `clock-names`. Older platforms require `assigned-clocks` and `assigned-clock-parents`; newer SM8750/Kaanapali variants use twelve clocks including PLL, esync, osc, and source clocks.

### State, Persistence, And Dependencies
Persistent state is the controller hardware description, PHY relationship, clocks, power, OPP, regulators, and graph. Dependencies include DSI PHY nodes, clock controllers, MDSS interrupt parents, power domains, graph/video-interface schemas, and generic DSI schema.

### Integration Points
The msm DSI driver binds under MDSS, receives pixels from DPU through `port@0`, and drives a panel/bridge through `port@1`. Dual-DSI properties coordinate master/sync behavior between two controller nodes.

### Risks
Clock-name ordering is the highest-risk contract because each compatible branch lists exact names. Deprecated `phy-names` remains allowed but should not guide new DTS. Dual-DSI booleans are only structurally validated, so board-level pairing still needs review.

### Test Signals
Binding checks should cover each compatible family. Runtime signals include DSI host registration, PHY clock-parent setup, panel attach, TE source operation, dual-DSI synchronization, and OPP/power-domain transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/dsi-controller-main.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/gmu.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/gmu.yaml

### Purpose
This binding describes Qualcomm Adreno A6xx-and-newer Graphics Management Units. GMU firmware/hardware manages GPU power and efficiency.

### Important APIs, Types, And Functions
The schema accepts versioned `qcom,adreno-gmu-*` compatibles with `qcom,adreno-gmu` fallback, x-series GMUs, and `qcom,adreno-gmu-wrapper`. It defines `reg`/`reg-names`, clocks/names, HFI and GMU interrupts, CX/GX power domains, IOMMU, `qcom,qmp`, OPP table, and wrapper-specific reduced requirements.

### Control Flow
The `allOf` chain branches by exact GMU compatible. Each branch fixes register-window names and clock lists for 615/618/630, 623, 635/660/663, 640, 650, 730/740/750/x185, 840, and x285. Non-wrapper GMUs require clocks, interrupts, IOMMU, and OPP; wrapper nodes require only wrapper register and power-domain resources.

### State, Persistence, And Dependencies
Persistent state is the GMU resource map and power-management topology. Dependencies include GPU clock controllers, CX/GX power domains, SMMU, AOSS/QMP for newer GMUs, OPP tables, interrupts, and the GPU node referencing GMU.

### Integration Points
The Adreno GPU driver uses GMU nodes to initialize firmware/HFI, vote clocks and power, and manage GPU performance states.

### Risks
Compatible-specific register/clock lists are easy to copy incorrectly between GPU generations. Missing `qcom,qmp` on newer GMUs should be caught by schema. Wrapper versus full GMU requirements differ substantially.

### Test Signals
Use binding checks per GMU generation. Runtime signals include GMU firmware boot, HFI interrupt handling, OPP transitions, CX/GX power sequencing, IOMMU setup, and GPU suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/gmu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/gpu.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/gpu.yaml

### Purpose
This schema defines Qualcomm Adreno and older AMD Imageon GPU nodes. It is selected for `qcom,adreno` or `amd,imageon` compatible strings.

### Important APIs, Types, And Functions
The binding API includes compatible patterns that encode chip ID or GPU/patch level, clocks/names, register windows, one interrupt, interconnects, IOMMU streams, SRAM/OCMEM phandles, OPP table, one power domain, optional `zap-shader` child with memory-region and firmware name, cooling cells, nvmem efuse cells, and optional `qcom,gmu`.

### Control Flow
The `allOf` chain branches by compatible regex to enforce generation-specific clock counts and names across a3xx, a4xx, a5xx, a6xx, and newer parts. GMU-attached devices use `qcom,gmu` to delegate power management to the GMU node.

### State, Persistence, And Dependencies
Persistent state describes GPU resources, memory address translation, interconnect bandwidth paths, firmware memory, thermal cooling interface, and optional GMU linkage. Dependencies include clock controllers, SMMU, interconnect providers, power domains, reserved memory, nvmem, OPP tables, and GMU binding.

### Integration Points
The msm/adreno DRM driver consumes this node for GPU probe, memory management, firmware loading, performance scaling, thermal integration, and GMU-managed power on newer devices.

### Risks
Regex-compatible parsing means string accuracy is important; wrong patch levels can select wrong driver data. IOMMU list cardinality is broad, so semantic stream-ID errors may only appear as faults. Zap shader memory must match firmware expectations.

### Test Signals
Validate with `dt_binding_check` for representative GPU generations. Runtime signals include GPU probe, ring submission, IOMMU fault absence, OPP/interconnect scaling, GMU link operation, zap shader load, and thermal cooling registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/gpu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/hdmi.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/hdmi.yaml

### Purpose
This binding describes Qualcomm MSM HDMI transmitter nodes used with MDSS/MDP display pipelines.

### Important APIs, Types, And Functions
The schema defines compatible values for HDMI TX variants, register ranges and names, interrupts, clock resources, power supplies/regulators, PHY linkage, DDC/I2C relationships, and graph ports connecting MDP input to connector or bridge output.

### Control Flow
The binding is declarative. Compatible and resource lists constrain the transmitter generation, while graph endpoints define the route from display controller to external HDMI sink.

### State, Persistence, And Dependencies
Persistent state is the DT hardware description for TX registers, clocks, regulators, PHY, DDC, and graph. Dependencies include MDSS interrupt hierarchy, HDMI PHY bindings, clock/regulator providers, DDC I2C adapter, graph schemas, and connector bindings.

### Integration Points
The msm HDMI driver binds as a display encoder/bridge. It consumes pixels from MDP/MDSS and exposes connector behavior including EDID and hotplug through associated DDC/PHY resources.

### Risks
HDMI nodes are sensitive to PHY and DDC topology. A display path may bind without EDID if DDC is wrong. Regulator omissions can appear as unstable hotplug or link failures.

### Test Signals
Run binding checks and board DTS validation. Runtime signals include HDMI TX probe, PHY attach, EDID reads, HPD interrupt delivery, modeset at common resolutions, and audio/clock behavior if supported by the variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/hdmi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/mdp4.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/mdp4.yaml

### Purpose
This schema documents Qualcomm MDP4 display controller nodes. MDP4 is an older display controller generation used before MDP5/DPU.

### Important APIs, Types, And Functions
The binding includes compatible values, MMIO `reg` and names, interrupts, clocks and names, optional power-domain/interconnect resources, IOMMU, and graph `ports` describing output interfaces.

### Control Flow
Validation is resource and graph based. There is no executable control flow; compatible selection maps the node to an older MDP4 driver path.

### State, Persistence, And Dependencies
Persistent DT state describes the controller register block, interrupt, clocks, memory translation, and output graph. Dependencies include MDSS or platform interrupt parents, clock providers, IOMMU, graph bindings, and downstream HDMI/DSI/LCDC-style outputs depending on the SoC.

### Integration Points
The msm DRM driver uses MDP4 as the display controller for older Qualcomm platforms. Its graph ports connect scanout to HDMI, DSI, or related encoders.

### Risks
Older bindings may coexist with legacy DTS assumptions, so strict validation can expose historical naming differences. Missing IOMMU or clock names can cause probe/runtime failures rather than schema-only failures.

### Test Signals
Run `dt_binding_check` for the MDP4 example and existing DTS files. Runtime signals are MDP4 probe, IRQ handling, scanout, output encoder attach, and suspend/resume clock sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/mdp4.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/mdss-common.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/mdss-common.yaml

### Purpose
This common schema defines shared Qualcomm MDSS display-subsystem properties for modern SoC-specific MDSS bindings. It is explicitly not auto-selected for legacy `qcom,mdss` nodes.

### Important APIs, Types, And Functions
The common MDSS contract includes node-name pattern, one `reg` named `mdss`, one power domain, clocks, interrupts, interrupt-controller properties, address/size cells, `ranges`, optional resets, optional IOMMU, and interconnects. SoC-specific schemas add exact compatible, clock names, and child pattern constraints.

### Control Flow
The file uses `select: false` and is consumed through `$ref`. Validation composition lets each SoC binding inherit the MDSS bus/interrupt/power shape while defining allowed children.

### State, Persistence, And Dependencies
Persistent state is the MDSS bus container and interrupt controller description. Dependencies include clock/power/reset providers, interconnect providers, SMMU, child DPU/DSI/DP/PHY schemas, and the graph topology below child nodes.

### Integration Points
Modern Qualcomm MDSS bindings import this schema for the parent display subsystem that hosts DPU, DSI, DP, and PHY children.

### Risks
Because many SoC-specific bindings depend on it, common-property changes can have wide validation impact. The schema validates structure but child compatibility semantics remain in each SoC wrapper.

### Test Signals
Run binding checks for all SoC-specific MDSS schemas that reference it. Regression signals are stable validation of interrupt-controller, `ranges`, reg-names, power, clocks, and child bus address layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/mdss-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,adreno-rgmu.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,adreno-rgmu.yaml

### Purpose
This binding describes RGMU blocks attached to certain Qualcomm Adreno GPUs. RGMU is a resource/power management unit for applicable GPU generations.

### Important APIs, Types, And Functions
The node contract includes `compatible`, register resources, clocks and names, power domains, interrupts, operating points, and GPU power-management integration properties. It is similar in role to GMU but targets the RGMU-supported hardware path.

### Control Flow
Validation is compatible and resource based. There is no executable flow; the schema ensures the GPU power-management driver receives the required register, clock, interrupt, and power resources.

### State, Persistence, And Dependencies
Persistent state describes RGMU register space and power/clock topology. Dependencies include GPU clock controllers, power-domain providers, interrupt controller, OPP table, and the corresponding GPU node.

### Integration Points
The Adreno driver uses RGMU data when bringing up GPUs that rely on this management unit for power/performance operations.

### Risks
RGMU and GMU nodes are not interchangeable; copying properties between bindings can describe the wrong hardware. Clock and power-domain naming must match the exact SoC.

### Test Signals
Use binding checks for the example DTS. Runtime signals include GPU probe with RGMU attachment, successful OPP transitions, interrupt handling, and suspend/resume without power-management errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,adreno-rgmu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,eliza-mdss.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,eliza-mdss.yaml

### Purpose
This schema defines the Qualcomm Eliza SoC MDSS parent. It encapsulates DPU, DSI, DP, and DSI PHY child nodes for that platform.

### Important APIs, Types, And Functions
The binding references `mdss-common.yaml`, fixes `compatible = "qcom,eliza-mdss"`, defines three display clocks, optional IOMMU, two interconnects named `mdp0-mem` and `cpu-cfg`, and patternProperties for `qcom,eliza-dpu`, `qcom,eliza-dp`, `qcom,eliza-dsi-ctrl`, and `qcom,eliza-dsi-phy-4nm` children.

### Control Flow
Validation composes the common MDSS parent contract with Eliza-specific child compatibility checks. Child nodes remain fully validated by their own DPU/DP/DSI/PHY schemas.

### State, Persistence, And Dependencies
Persistent state is the Eliza display subsystem bus, interrupt controller, clocks, power domain, interconnects, SMMU, and children. Dependencies include RPMh power/interconnect providers, display clocks, DPU/DSI/DP/PHY bindings, and graph endpoints.

### Integration Points
The MDSS parent hosts child display controllers and routes their interrupts through the MDSS interrupt controller. Example topology shows DPU outputs to two DSI controllers and one DP controller.

### Risks
PatternProperties only constrain child compatibles; resource correctness remains delegated. Eliza-specific DSI uses the SM8750 DSI clock model, so child clock lists must match that branch.

### Test Signals
Run binding checks for the whole example. Runtime signals include MDSS parent probe, child population, interconnect votes, SMMU attachment, DPU-to-DSI/DP graph resolution, and interrupt routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,eliza-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,glymur-mdss.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,glymur-mdss.yaml

### Purpose
This schema defines the Qualcomm Glymur MDSS parent, a subsystem containing DPU and DP display blocks.

### Important APIs, Types, And Functions
It imports `mdss-common.yaml`, fixes `compatible = "qcom,glymur-mdss"`, defines display AHB, hf AXI, and core clocks, optional IOMMU and interconnects, and constrains child nodes with patternProperties for Glymur DPU, DP, and PHY-compatible blocks.

### Control Flow
Validation is composed: common MDSS properties are inherited and Glymur-specific child compatible filters are applied. Runtime display routing remains represented by child graph endpoints.

### State, Persistence, And Dependencies
Persistent state covers MDSS bus resources, interrupts, power, clocks, interconnects, IOMMU, and child display nodes. Dependencies include Qualcomm display clock controllers, RPMh power/interconnect providers, DP/DPU/PHY bindings, and graph schemas.

### Integration Points
The parent node hosts DPU and DP controllers and provides interrupt-controller behavior for children under the MDSS address space.

### Risks
Glymur DP controllers may have complex MST/SST resource requirements inherited from `dp-controller.yaml`. The parent schema does not fully validate child internals, so child schemas must be run together.

### Test Signals
Use `dt_binding_check` on Glymur MDSS examples and full DTS. Runtime signals are MDSS bus probe, DPU/DP child creation, interconnect voting, graph resolution, and DP link training.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,glymur-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,kaanapali-mdss.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,kaanapali-mdss.yaml

### Purpose
This binding defines the Qualcomm Kaanapali MDSS parent. It contains DPU, DSI, and DSI PHY child blocks for that SoC family.

### Important APIs, Types, And Functions
The schema imports `mdss-common.yaml`, sets `compatible = "qcom,kaanapali-mdss"`, defines the platform clock set, and constrains child compatibles for Kaanapali DPU, DSI controller, and DSI PHY nodes.

### Control Flow
Validation applies common MDSS rules plus Kaanapali child compatible filters. The display data path is encoded by child graph endpoints rather than parent control flow.

### State, Persistence, And Dependencies
Persistent state includes parent MDSS resources and child bus topology. Dependencies include display clocks, PM domains, optional IOMMU/interconnects from the common schema, DPU/DSI/PHY child schemas, and graph bindings.

### Integration Points
The Kaanapali MDSS parent provides address space, interrupts, and power/clock context for its DPU and DSI children. The DSI child uses the newer high-clock-count branch in the DSI controller schema.

### Risks
Child compatibility filters do not replace child schema validation. Kaanapali DSI clock names are numerous, and a parent node can validate while a child still fails due to clock/resource mismatch.

### Test Signals
Binding checks should run on the complete MDSS example. Runtime signals are parent probe, DPU/DSI child population, DSI PHY attach, graph connectivity, and panel modeset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,kaanapali-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,mdp5.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,mdp5.yaml

### Purpose
This schema describes Qualcomm MDP5 display controllers. MDP5 is the display engine generation used on several pre-DPU Snapdragon platforms.

### Important APIs, Types, And Functions
The binding includes SoC-specific compatible strings with `qcom,mdp5` fallback, register resources, one interrupt, clocks and names, power-domain, optional IOMMU, and graph `ports`. The ports represent outputs to DSI, DP, HDMI, or other display interfaces.

### Control Flow
Validation constrains compatible pairs and required controller resources. The schema relies on graph endpoints to express which display interface each MDP5 output drives.

### State, Persistence, And Dependencies
Persistent state is the MDP5 hardware description: register window, clocks, interrupt, power domain, memory translation, and output graph. Dependencies include MDSS parent interrupt-controller behavior, clock/PM/IOMMU providers, graph bindings, and downstream interface schemas.

### Integration Points
The msm DRM driver uses MDP5 as the central display controller under legacy `qcom,mdss` parents. It drives child outputs through the graph.

### Risks
MDP5 platforms vary in clock availability and output count. A graph may validate with missing outputs but not match board hardware. IOMMU omission can cause scanout memory faults.

### Test Signals
Use binding checks plus existing DTS validation. Runtime signals include MDP5 probe, IRQ delivery, plane scanout, graph-resolved encoder attachment, IOMMU fault absence, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,mdp5.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,mdss.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,mdss.yaml

### Purpose
This binding describes legacy Qualcomm Mobile Display Subsystem parent nodes using `compatible = "qcom,mdss"`. It encapsulates MDP5, DSI, HDMI, eDP, PHY, and related children.

### Important APIs, Types, And Functions
The parent API includes node-name pattern, `compatible`, two or three register regions named `mdss_phys`, `vbif_phys`, and optional `vbif_nrt_phys`, one interrupt, interrupt-controller cells, one power domain, clock sets, address/size cells, `ranges`, optional reset, and interconnects. PatternProperties allow MDP5, DSI, PHY, and HDMI child nodes.

### Control Flow
The schema validates the MDSS bus container and permits known child node patterns with compatible filters. It does not deeply validate child nodes inline; those are handled by child schemas.

### State, Persistence, And Dependencies
Persistent state is the display-subsystem bus, VBIF register map, interrupt controller, clocks, power domain, and child address space. Dependencies include GCC/MMCC clocks, power domains, interrupt controller, interconnects, and child display bindings.

### Integration Points
Legacy msm DRM platforms use this parent to route child interrupts and instantiate MDP5/DSI/HDMI/PHY nodes below the MDSS address space.

### Risks
This legacy binding overlaps conceptually with `mdss-common.yaml` but has different register names and child constraints. Mixing modern and legacy parent contracts can produce invalid DTS.

### Test Signals
Run binding checks on legacy MDSS examples and DTS files. Runtime signals are MDSS parent probe, interrupt-domain registration, child population, clock/power enablement, and MDP5-to-output graph resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,msm8998-dpu.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,msm8998-dpu.yaml

### Purpose
This schema defines the MSM8998 DPU display-controller node.

### Important APIs, Types, And Functions
The binding references `dpu-common.yaml`, fixes `compatible = "qcom,msm8998-dpu"`, requires four register regions named `mdp`, `regdma`, `vbif`, and `vbif_nrt`, and five clocks named `iface`, `bus`, `mnoc`, `core`, and `vsync`.

### Control Flow
Validation composes common DPU requirements with MSM8998-specific register and clock layouts. Graph ports from the common schema connect DPU outputs to DSI controllers.

### State, Persistence, And Dependencies
Persistent state includes DPU register windows, clocks, interrupt parent, OPP/power data, and graph ports. Dependencies include the MSM8998 MDSS parent, MMCC clocks, RPM power domains, OPP tables, and DSI child nodes.

### Integration Points
The msm DPU driver uses this node under `qcom,msm8998-mdss`; the example exposes two DPU output ports feeding two DSI controllers.

### Risks
MSM8998 uses a distinct `regdma` region and non-realtime VBIF. Omitting or reordering these register names can break driver access. Clock naming differs from newer DPU variants.

### Test Signals
Binding checks should validate exact register and clock names. Runtime signals include DPU probe, RegDMA access, VBIF setup, OPP scaling, and dual-DSI graph resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,msm8998-dpu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,msm8998-mdss.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,msm8998-mdss.yaml

### Purpose
This schema defines the MSM8998 MDSS parent, hosting MSM8998 DPU, DSI controllers, and DSI PHYs.

### Important APIs, Types, And Functions
It references `mdss-common.yaml`, fixes `compatible = "qcom,msm8998-mdss"`, defines clocks named `iface`, `bus`, and `core`, allows one IOMMU, and constrains children to `qcom,msm8998-dpu`, `qcom,msm8998-dsi-ctrl` plus `qcom,mdss-dsi-ctrl`, and `qcom,dsi-phy-10nm-8998`.

### Control Flow
Validation composes common MDSS rules with MSM8998 child-compatible filters. Child schemas validate DPU, DSI, and PHY internals.

### State, Persistence, And Dependencies
Persistent state is the MSM8998 MDSS bus, clocks, power, interrupt domain, IOMMU, and children. Dependencies include MMCC/RPM clocks, RPM power domains, SMMU, DPU/DSI/PHY bindings, and graph endpoints.

### Integration Points
This parent wires the MSM8998 DPU outputs to two DSI controllers and provides interrupt routing for the child display blocks.

### Risks
The binding title and child filters are MSM8998-specific; sharing with generic DPU/MDSS snippets can lose required MSM8998 clock and PHY naming. The parent can validate while child dual-DSI graph endpoints remain semantically incomplete.

### Test Signals
Run binding checks on full examples. Runtime signals are MDSS parent probe, IOMMU attachment, child creation, DPU-to-DSI graph resolution, and dual-panel/dual-DSI modeset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,msm8998-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,qcm2290-dpu.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,qcm2290-dpu.yaml

### Purpose
This schema defines the QCM2290 DPU display controller.

### Important APIs, Types, And Functions
It references `dpu-common.yaml`, fixes `compatible = "qcom,qcm2290-dpu"`, requires two register regions named `mdp` and `vbif`, and five clocks named `bus`, `iface`, `core`, `lut`, and `vsync`.

### Control Flow
Validation composes common DPU requirements with the QCM2290 resource layout. Ports from the common schema represent DPU outputs, usually to a single DSI controller.

### State, Persistence, And Dependencies
Persistent state includes DPU MMIO, clocks, power/OPP, interrupt parent, and graph. Dependencies include QCM2290 MDSS parent, GCC/DISPCC clocks, RPM power domains, OPP tables, and DSI bindings.

### Integration Points
The DPU child appears under `qcom,qcm2290-mdss` and feeds QCM2290 DSI through a graph endpoint.

### Risks
Clock order differs from SC7180/SC7280 families. The platform has a simpler two-register DPU layout, so copying four-register MSM8998 snippets would be invalid.

### Test Signals
Binding checks should validate exact register and clock lists. Runtime signals include DPU probe, LUT/core/vsync clock enablement, OPP scaling, interrupt delivery, and DSI graph output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,qcm2290-dpu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,qcm2290-mdss.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,qcm2290-mdss.yaml

### Purpose
This schema defines the QCM2290 MDSS parent for DPU and DSI display blocks.

### Important APIs, Types, And Functions
The binding imports `mdss-common.yaml`, fixes `compatible = "qcom,qcm2290-mdss"`, defines clocks named `iface`, `bus`, and `core`, allows one IOMMU, defines interconnects named `mdp0-mem` and `cpu-cfg`, and constrains DPU, DSI, and DSI PHY child compatibles.

### Control Flow
Common MDSS validation is composed with QCM2290-specific child filters. The schema validates the parent bus and delegates child internals.

### State, Persistence, And Dependencies
Persistent state includes the MDSS register block, clocks, power, interrupts, interconnect paths, IOMMU, and child bus. Dependencies include QCM2290 GCC/DISPCC, RPM power/interconnect providers, SMMU, DPU/DSI/PHY bindings, and graph endpoints.

### Integration Points
The MDSS parent hosts the QCM2290 DPU and DSI controller and provides the interrupt-controller context used by child nodes.

### Risks
The title says `QCM220`, likely a typo for QCM2290. Interconnect naming must match the common and driver expectations. Child compatible filters do not enforce complete child resource correctness.

### Test Signals
Use `dt_binding_check` on the example and full DTS. Runtime signals include MDSS probe, interconnect votes, IOMMU attach, child creation, DPU-to-DSI graph resolution, and panel modeset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,qcm2290-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,qcs8300-mdss.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,qcs8300-mdss.yaml

### Purpose
This binding defines the QCS8300 MDSS parent, containing DPU, DP/eDP, DSI, and PHY children.

### Important APIs, Types, And Functions
It references `mdss-common.yaml`, fixes `compatible = "qcom,qcs8300-mdss"`, defines three display clocks, one IOMMU, up to three interconnects/names, and child filters for `qcom,qcs8300-dpu`, `qcom,qcs8300-dp`, `qcom,qcs8300-dsi-ctrl`, `qcom,qcs8300-dsi-phy-5nm`, and `qcom,qcs8300-edp-phy`.

### Control Flow
Validation composes common MDSS properties and QCS8300 child-compatible constraints. The example also uses fallback compatibles to SA8775P for DPU/DP/DSI/PHY child schemas.

### State, Persistence, And Dependencies
Persistent state includes MDSS resources, interrupt domain, clocks, reset, power, interconnects, SMMU, and child display nodes. Dependencies include QCS8300/SA8775P clock and power bindings, DPU/DP/DSI/PHY schemas, and graph endpoints.

### Integration Points
The parent hosts a DPU, DSI path, DSI PHY, eDP PHY, and DP controller. It connects DPU outputs to DSI and DP through child graph endpoints.

### Risks
Fallback to SA8775P-compatible child bindings means resource lists must follow the fallback schema exactly. Three interconnect paths add review risk, especially `mdp1-mem` on multi-interface routes.

### Test Signals
Run binding checks for the complete QCS8300 example. Runtime signals are parent probe, child instantiation, SMMU/interconnect setup, DSI panel output, DP/eDP PHY attach, and DP link training.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,qcs8300-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sa8775p-mdss.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sa8775p-mdss.yaml

### Purpose
This schema defines the SA8775P MDSS parent. It covers a display subsystem with DPU, DP/eDP, DSI, and PHY children.

### Important APIs, Types, And Functions
The binding imports `mdss-common.yaml`, fixes `compatible = "qcom,sa8775p-mdss"`, defines display AHB, hf AXI, and core clocks, optional IOMMU, up to three interconnect paths, and child compatible filters for SA8775P DPU, DP, DSI controller, DSI PHY, and eDP PHY.

### Control Flow
Validation is common MDSS plus SA8775P child constraints. DP child nodes must follow the DP controller schema, including SA8775P MST register and clock cardinalities.

### State, Persistence, And Dependencies
Persistent state includes the MDSS parent register block, interrupts, clocks, reset, power, interconnects, SMMU, and child bus. Dependencies include SA8775P display clocks, RPMh power/interconnects, DPU/DP/DSI/PHY bindings, and graph endpoints.

### Integration Points
SA8775P MDSS hosts high-capability display paths with multiple memory interconnects and DP stream support. It provides interrupt-controller behavior for child blocks.

### Risks
SA8775P DP supports four-stream MST on some controllers, so child resource counts are easy to under-describe. Multi-path interconnect names must match driver expectations.

### Test Signals
Binding checks should cover DPU, DSI, DP, and PHY children together. Runtime signals are MDSS probe, interconnect voting, DP MST/SST bring-up, DSI output, and interrupt routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sa8775p-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sar2130p-mdss.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sar2130p-mdss.yaml

### Purpose
This binding defines the SAR2130P MDSS parent for DPU, DP, DSI, and PHY children.

### Important APIs, Types, And Functions
The schema imports `mdss-common.yaml`, fixes `compatible = "qcom,sar2130p-mdss"`, defines display clocks, optional IOMMU and interconnects, and constrains child compatibles for SAR2130P DPU, DP, DSI controller, and PHY blocks.

### Control Flow
Validation composes the common MDSS parent contract with SAR2130P child-compatible filters. Child DPU and DP resources are checked by their referenced schemas, including SC7280-style DPU fallback and SM8350-style DP fallback where applicable.

### State, Persistence, And Dependencies
Persistent state includes parent MDSS resources, interrupt controller state, power/clock/reset, interconnects, SMMU, and child display topology. Dependencies include display clock providers, RPMh power domains, DPU/DP/DSI/PHY bindings, and graph schemas.

### Integration Points
The parent coordinates SAR2130P display children and routes DPU outputs to DSI/DP interfaces via graph endpoints.

### Risks
SAR2130P often reuses fallback compatibles from nearby Qualcomm families. Mismatched fallback ordering can bind to the wrong resource model even when the parent compatible is correct.

### Test Signals
Use binding checks against full SAR2130P examples. Runtime signals include MDSS and child probe, graph resolution, DSI panel modeset, DP link training, interconnect votes, and SMMU attachment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sar2130p-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc7180-dpu.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc7180-dpu.yaml

### Purpose
This schema defines SC7180-family DPU display controllers, also covering SM6125, SM6350, and SM6375 variants.

### Important APIs, Types, And Functions
It references `dpu-common.yaml`, accepts four compatible values, requires two register regions named `mdp` and `vbif`, and defines six or seven clocks named `bus`, `iface`, `rot`, `lut`, `core`, `vsync`, and optionally `throttle`.

### Control Flow
The `allOf` branch requires at least seven clocks and names for SM6375 and SM6125. Other variants use the six-clock minimum. Common DPU ports connect outputs to DSI and DP.

### State, Persistence, And Dependencies
Persistent state includes DPU MMIO, clocks, interrupt, power/OPP, and graph outputs. Dependencies include SC7180-family MDSS parents, GCC/DISPCC clocks, RPMh/RPMPD power domains, OPP tables, and DSI/DP child nodes.

### Integration Points
The DPU child under SC7180-style MDSS feeds DSI and DP endpoints. The rotator and LUT clocks reflect hardware blocks in this DPU generation.

### Risks
SM6125/SM6375 need the throttle clock; copying the SC7180 six-clock example can under-specify those variants. Output port numbering should match DPU interface indices.

### Test Signals
Binding checks should cover all compatible variants. Runtime signals include DPU probe, optional throttle clock acquisition where required, DSI/DP graph resolution, OPP scaling, and scanout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc7180-dpu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc7180-mdss.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc7180-mdss.yaml

### Purpose
This schema defines the SC7180 MDSS parent, hosting SC7180 DPU, DSI, DP, and DSI PHY children.

### Important APIs, Types, And Functions
It imports `mdss-common.yaml`, fixes `compatible = "qcom,sc7180-mdss"`, defines clocks named `iface`, `ahb`, and `core`, allows one IOMMU, defines two interconnects `mdp0-mem` and `cpu-cfg`, and filters child compatibles for SC7180 DPU, DP, DSI controller, and `qcom,dsi-phy-10nm`.

### Control Flow
Common MDSS validation is composed with SC7180 child filters. Child schemas validate detailed DPU, DSI, DP, and PHY resources.

### State, Persistence, And Dependencies
Persistent state includes MDSS bus resources, interrupts, clocks, power domain, interconnects, SMMU, and child topology. Dependencies include GCC/DISPCC, RPMh/RPMPD, SMMU, DPU/DSI/DP/PHY bindings, and graph schemas.

### Integration Points
SC7180 MDSS wires DPU outputs to one DSI controller and one DP controller in the example. It also provides the interrupt parent for those children.

### Risks
The clock-name set uses both GCC and DISPCC AHB clocks, so `iface` versus `ahb` naming must not be swapped. Child DP/eDP and DSI resources must be checked with their own schemas.

### Test Signals
Binding checks should run on the full SC7180 example. Runtime signals are parent probe, interconnect votes, SMMU attach, DPU-to-DSI/DP graph resolution, DSI panel output, and DP link training.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc7180-mdss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc7280-dpu.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc7280-dpu.yaml

### Purpose
This schema defines SC7280-style DPU display controllers and related compatibles including SAR2130P, SC8280XP, SM8350, SM8450, and SM8550.

### Important APIs, Types, And Functions
The binding references `dpu-common.yaml`, accepts several compatible values, requires two register regions named `mdp` and `vbif`, and six clocks named `bus`, `nrt_bus`, `iface`, `lut`, `core`, and `vsync`.

### Control Flow
Validation is mostly fixed for this family: common DPU resources plus exact two-register and six-clock layout. Graph ports from the common schema express DPU interface outputs.

### State, Persistence, And Dependencies
Persistent state includes DPU registers, realtime/non-realtime bus clocks, AHB/core/LUT/vsync clocks, power/OPP, interrupt, and graph endpoints. Dependencies include SoC-specific MDSS parent, display/GCC clocks, RPMh power domains, OPP tables, and DSI/DP children.

### Integration Points
SC7280-family DPU nodes feed DSI and DP/eDP interfaces through MDSS graph ports. The `nrt_bus` clock differentiates this family from simpler QCM2290 layouts.

### Risks
This schema covers multiple SoCs; DTS authors must still use the correct SoC-specific MDSS parent and child outputs. Copying SC7180 clock names would omit `nrt_bus` and include invalid `rot`.

### Test Signals
Run binding checks for each compatible family represented in DTS. Runtime signals are DPU probe, bus and non-realtime bus clock control, graph output resolution, OPP scaling, and display scanout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc7280-dpu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc7280-mdss.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc7280-mdss.yaml

### Purpose
This schema defines the SC7280 MDSS parent, hosting SC7280 DPU, DSI, DP/eDP, and PHY children.

### Important APIs, Types, And Functions
It references `mdss-common.yaml`, fixes `compatible = "qcom,sc7280-mdss"`, defines display clocks, optional IOMMU, interconnects, and patternProperties for `qcom,sc7280-dpu`, `qcom,sc7280-dp`, `qcom,sc7280-edp`, `qcom,sc7280-dsi-ctrl`, and matching DSI/eDP PHY nodes.

### Control Flow
Validation composes common MDSS constraints with SC7280 child-compatible filters. Child DP validation distinguishes DP from eDP behavior, including sound/AUX rules in `dp-controller.yaml`.

### State, Persistence, And Dependencies
Persistent state includes MDSS register block, interrupt-controller behavior, clocks, power, interconnects, optional SMMU, and child address space. Dependencies include SC7280 display/GCC clocks, power domains, DPU/DSI/DP/PHY schemas, graph bindings, and OPP/interconnect providers.

### Integration Points
The parent hosts DPU outputs to DSI and DP/eDP controllers. It is the container through which msm DRM discovers and binds the SC7280 display subsystem.

### Risks
SC7280 supports both DP and eDP child paths; applying DP audio/AUX assumptions to eDP nodes is invalid. Child pattern filters must remain aligned with DSI/DP/PHY schema compatible lists.

### Test Signals
Binding checks should cover full SC7280 examples with DSI, DP, and eDP children. Runtime signals include MDSS probe, DPU/DSI/DP child binding, eDP versus DP behavior, graph resolution, and link/panel bring-up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/qcom,sc7280-mdss.yaml -->
