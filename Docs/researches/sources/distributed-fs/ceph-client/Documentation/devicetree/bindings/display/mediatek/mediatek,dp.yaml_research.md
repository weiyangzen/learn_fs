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
