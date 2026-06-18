# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/st,stm32-hdp.yaml

## Purpose
This schema describes the STM32 Hardware Debug Port mux/config block. It exposes internal debug signals onto GPIO-capable pins through pinmux-style state nodes rather than acting as a full GPIO controller. Source title: STM32 Hardware Debug Port Mux/Config. Description signal from the file: STMicroelectronics's STM32 MPUs integrate a Hardware Debug Port (HDP). It allows to output internal signals on SoC's GPIO.

## Important APIs, Types, and Schema Surface
- Lines read: 193.
- Compatible contract: st,stm32mp131-hdp, st,stm32mp151-hdp, st,stm32mp251-hdp. Top-level required properties: compatible, reg, clocks. Important top-level properties found in the schema: reg, clocks. Child-node patterns: ^hdp[0-7]-pins$. Function enum sample: pwr_pwrwake_sys, pwr_stop_forbidden, pwr_stdby_wakeup, pwr_encomp_vddcore, bsec_out_sec_niden, aiec_sys_wakeup, none, ddrctrl_lp_req, pwr_ddr_ret_enable_n, dts_clk_ptat, sram3ctrl_tamp_erase_act, gpoval0, pwr_sel_vth_vddcpu, pwr_mpu_ram_lowspeed, ca7_naxierrirq, pwr_okin_mr plus 231 more. Referenced schemas: pinmux-node.yaml#, pinctrl.yaml#.

## Control Flow
Validation selects the STM32MP HDP compatible, then validates pinmux state children that map internal debug signals to output-capable pins. It references generic pinmux and pinctrl schemas but does not expose generic GPIO provider behavior.

## State and Persistence Behavior
Persistent ABI is the HDP compatible and signal-to-pin mux state representation. Runtime state is the selected debug signal route applied by the platform driver from the static devicetree.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Risk is mostly enum drift between signal IDs and supported SoC variants. Tests should validate each compatible example and reject ordinary GPIO-controller properties.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/st,stm32-hdp.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.
