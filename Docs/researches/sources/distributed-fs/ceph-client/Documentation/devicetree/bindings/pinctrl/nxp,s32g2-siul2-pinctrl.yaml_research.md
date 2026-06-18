## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/nxp,s32g2-siul2-pinctrl.yaml

### Purpose
`nxp,s32g2-siul2-pinctrl.yaml` describes the NXP S32G2 SIUL2 pin controller, whose mux registers are split across SIUL2_0 and SIUL2_1 MSCR and IMCR windows. It documents the six required register regions and the nested pin group layout used to program S32G2 pin mux and electrical state.

### Important Schema APIs
The controller requires `compatible`, `reg` and accepts compatible `nxp,s32g2-siul2-pinctrl`. Child nodes ending in `-pins` contain group nodes ending in `-grp[0-9]`. Each group composes `pinmux-node.yaml` and `pincfg-node.yaml`, then locally allows `pinmux`, bias flags, high impedance, open drain, input/output enablement, and `slew-rate` values of 83, 133, 150, 166, or 208 MHz. The packed `pinmux` value is `(PIN_ID << 4) | SSS`.

### Validation Flow
Top-level validation confirms the compatible string and exactly described MSCR/IMCR register regions, then pattern validation walks from `*-pins` containers to `*-grpN` configuration groups. Group schemas close unknown properties, so unsupported pinconf keys should fail. The example covers LLCE CAN input and output groups with separate SSS values.

### State And Persistence
No state is held by the YAML file. Persistent DTS data records hardware register windows and packed pinmux values that the Linux S32G2 SIUL2 pinctrl driver decodes into MSCR and IMCR writes. Reserved register index ranges noted in the description remain a driver and DTS correctness concern.

### Dependencies And Integration Points
The binding depends on the generic pinmux and pinconf helpers. It integrates with S32G2 board DTS files, the platform device created from `pinctrl@...`, and client devices that reference the `*-pins` state labels through standard `pinctrl-0` style properties.

### Risks
The schema cannot fully verify that a packed pin ID avoids reserved MSCR/IMCR indexes or that the selected 4-bit SSS is valid for a specific pad. Incorrect register-region ordering would direct the driver to the wrong SIUL2 window. Closed group properties reduce typo risk but require binding updates when the driver gains new pinconf features.

### Test Signals
Use `dt_binding_check` on the example, negative tests for misspelled group names and unsupported slew rates, and board boot tests that exercise CAN, GPIO, and input mux paths across both SIUL2 regions.
