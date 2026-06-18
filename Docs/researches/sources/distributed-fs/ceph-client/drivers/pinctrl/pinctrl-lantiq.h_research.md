# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-lantiq.h

## Purpose
Defines the shared data contract for Lantiq pinctrl implementations: pinconf encodings, multifunction pin descriptors, group/function tables, SoC registration metadata, and the common registration prototype.

## Important APIs, Types, and Functions
Important definitions include `LTQ_MAX_MUX`, `MFPR_FUNC_MASK`, `LTQ_PINCONF_PACK`, `LTQ_PINCONF_UNPACK_PARAM`, and `LTQ_PINCONF_UNPACK_ARG`. Main types are `enum ltq_pinconf_param`, `struct ltq_cfg_param`, `struct ltq_mfp_pin`, `struct ltq_pin_group`, `struct ltq_pmx_func`, and `struct ltq_pinmux_info`. The header also enumerates GPIO pins `GPIO0` through `GPIO88` and declares `ltq_pinctrl_register`.

## Control Flow and State
There is no runtime flow in this header. It declares the persistent state that SoC drivers pass to the common core: pad descriptors, MFP mux capabilities, groups, functions, DT-readable config parameters, external interrupt maps, up to five MMIO bases and clocks, and a callback for applying mux values to hardware.

## Dependencies and Integration Points
Includes Linux pinctrl consumer, machine, pinconf, pinctrl, and pinmux headers plus local `core.h`. It is consumed by `pinctrl-lantiq.c` and by Lantiq SoC-specific pinctrl drivers that populate `struct ltq_pinmux_info`.

## Risks and Test Signals
Because this is a shared ABI inside the driver family, wrong struct fields or pinconf packing break all Lantiq variants. Risks include mismatch between `LTQ_MAX_MUX` and SoC tables, pin enum drift, and callback signature changes. Test signals are compile coverage for every Lantiq pinctrl user and boot-time mux/config application on representative boards.
