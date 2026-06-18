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
