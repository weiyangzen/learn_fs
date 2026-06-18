## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,lpass-lpi-common.yaml

### Purpose
`qcom,lpass-lpi-common.yaml` is the reusable common schema for Qualcomm LPASS Low Power Island TLMM controllers. It captures the GPIO-provider contract and the shared state-node pinconf/pinmux vocabulary used by LPASS LPI bindings such as Milos, SC7280, SC8280XP, SDM660, and SDM670.

### Important Schema APIs
The controller requires `gpio-controller`, `#gpio-cells`, and `gpio-ranges`, and optionally supports `gpio-reserved-ranges`. Its `$defs/qcom-tlmm-state` requires `pins` and `function`, composes `pincfg-node.yaml` and `pinmux-node.yaml`, and permits drive strengths 2 through 16 mA, `slew-rate` values 0 through 3, bus-hold/pull/disable bias controls, input enablement, and output high/low.

### Validation Flow
Concrete LPASS schemas first validate SoC-specific compatible, registers, clocks, and local pin/function enums, then reference this common schema through `allOf`. State nodes therefore inherit the generic pinconf and mux rules while concrete files close `unevaluatedProperties` and restrict legal GPIO names.

### State And Persistence
The YAML is stateless. DTS state persists LPASS audio pin mux, GPIO numbering, reserved ranges, and electrical settings used by the LPASS LPI pinctrl driver. Because LPASS pins often gate audio interfaces, stale pin states can affect audio bring-up and low-power transitions.

### Dependencies And Integration Points
It depends on `pinctrl.yaml`, `pincfg-node.yaml`, and `pinmux-node.yaml`. It integrates with the Linux GPIO and pinctrl subsystems, LPASS clock providers in the concrete bindings, and audio clients such as SoundWire, I2S, DMIC, and external master clock consumers.

### Risks
The common schema permits `additionalProperties: true`, so concrete LPASS bindings must close their schemas. Requiring `pins` and `function` is stricter than generic TLMM and should match driver expectations. GPIO reserved ranges must remain synchronized with firmware ownership or LPASS-internal reservations.

### Test Signals
Run dt-schema checks for this common schema and every LPASS consumer. Useful negative cases include missing `function`, unsupported `slew-rate`, wrong `#gpio-cells`, and reserved-range tuple errors; runtime tests should verify audio pin states and GPIO range registration.
