# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/chrome/google,cros-ec-typec.yaml

## Purpose
Chrome OS devices have an Embedded Controller(EC) which has access to Type C port state. It is a Chrome EC binding used for Chrome OS embedded-controller Type-C connector enumeration and role-switch integration. The binding is maintained by Benson Leung <bleung@chromium.org>, Abhishek Pandit-Subedi <abhishekpandit@chromium.org>, Andrei Kuchynski <akuchynski@chromium.org>, ukasz Bartosik <ukaszb@chromium.org>, plus 1 more and gives dt-schema a canonical contract for nodes matching `google,cros-ec-typec`, `google,cros-ec-ucsi`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum google,cros-ec-typec, google,cros-ec-ucsi), `#address-cells` (const 1), `#size-cells` (const 0). Required properties are `compatible`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses child-node patterns `^connector@[0-9a-f]+$`. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/connector/usb-connector.yaml#. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=chrome/google,cros-ec-typec.yaml`
- run `make dtbs_check` on DTS files using `google,cros-ec-typec`, `google,cros-ec-ucsi`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
