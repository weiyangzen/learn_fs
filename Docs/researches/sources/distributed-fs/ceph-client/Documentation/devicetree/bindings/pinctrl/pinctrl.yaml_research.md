## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/pinctrl.yaml

### Purpose
`pinctrl.yaml` is the generic pin controller device schema. It documents the Linux devicetree convention that controller nodes contain or own pin configuration state nodes referenced by client devices through `pinctrl-*` properties. It intentionally stays permissive because hardware-specific bindings define the contents and nesting of those state nodes.

### Important Schema APIs
The schema exposes the controller node name pattern `^(pinctrl|pinmux)(@[0-9a-f]+)?$`, the optional `#pinctrl-cells` provider shape, and the boolean `pinctrl-use-default` escape hatch for bootloader-provided pin states. It is maintained by Linus Walleij <linusw@kernel.org>, Rafał Miłecki <rafal@milecki.pl>. It does not declare child-state properties; those come from helper schemas such as `pinmux-node.yaml` and `pincfg-node.yaml` or from concrete SoC bindings.

### Validation Flow
Dt-schema first applies the core YAML meta-schema, then this file checks only the generic controller-level properties. `additionalProperties: true` is deliberate control flow: validation must continue in concrete bindings without this helper rejecting vendor registers, interrupts, clocks, GPIO provider properties, or vendor child node layouts.

### State And Persistence
There is no runtime state in this file. The persistent artifact is the binding contract consumed by `dt_binding_check` and by DTS authors. At runtime, Linux pinctrl drivers consume the resulting devicetree nodes and may either program hardware or honor `pinctrl-use-default` when the OS lacks a driver.

### Dependencies And Integration Points
The file integrates with every pinctrl provider binding that references `/schemas/pinctrl/pinctrl.yaml#`, including the Qualcomm TLMM and LPASS LPI schemas in this work item. It also anchors provider-style bindings that use `#pinctrl-cells` for hardware-indexed pin arrays.

### Risks
The permissive `additionalProperties` setting means this file cannot catch misspelled vendor properties by itself. That is acceptable only when concrete bindings close the schema with `unevaluatedProperties: false` or equivalent. Overusing `pinctrl-use-default` can hide missing driver support or board-specific mux requirements.

### Test Signals
Useful tests are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/pinctrl.yaml`, sample nodes named `pinctrl@...` and `pinmux@...`, and downstream concrete bindings that prove this helper composes without rejecting vendor-specific controller properties.
