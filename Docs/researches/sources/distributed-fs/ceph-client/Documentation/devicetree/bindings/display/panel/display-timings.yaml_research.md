<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/display-timings.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/display-timings.yaml

Purpose: generic Devicetree binding schema for a `display-timings` child node that lists one or more panel timing modes and optionally marks a native/default mode. It is shared by simple panels and display interfaces that need datasheet timing values in DTS rather than hard-coded driver tables.

Important APIs/types/functions: the schema defines `$nodename: display-timings`, optional `native-mode` as a phandle, `patternProperties` for timing child nodes matching `^timing`, and references `panel-timing.yaml#` for each timing entry. It uses `additionalProperties: false` to keep the timing container limited to the native-mode selector and timing children.

Control flow: validation accepts a node named `display-timings`, checks that `native-mode` points at one of the timing children when present, and validates each `timing*` child through `panel-timing.yaml`. If `native-mode` is absent, the binding documentation states that consumers treat the first timing node as native.

State and persistence behavior: there is no runtime state. The file standardizes persistent DTS timing data: pixel clock, active area, porches, sync lengths, and polarity flags. Drivers read those values at probe time to program display controller timings.

Dependencies/integration points: integrates with `panel-timing.yaml#`, `panel-common.yaml#` users that allow `display-timings`, simple-panel style drivers, and board DTS panel nodes. It is transport-neutral and can describe timings for RGB, LVDS, or other fixed-timing panels.

Risks: phandle mistakes or relying on implicit first-node ordering can select the wrong mode. Timing triplets must use min/typ/max ordering understood by `panel-timing.yaml`; incorrect units or polarity flags can produce a valid but unusable display mode. Because this schema is generic, panel-specific electrical constraints must be enforced elsewhere.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/display-timings.yaml` and validate DTS nodes that include multiple timing children, no native-mode, and a native-mode phandle. Negative cases should include non-`timing*` children, unknown container properties, invalid timing property shapes, and stale phandle labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/panel/display-timings.yaml -->
