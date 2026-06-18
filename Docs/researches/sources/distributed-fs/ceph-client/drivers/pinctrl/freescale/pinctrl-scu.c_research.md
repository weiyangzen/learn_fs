# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-scu.c

## Purpose
Provides the System Controller Unit IPC-backed pin configuration helpers used by i.MX SoCs where pad mux/config registers are controlled by firmware rather than direct MMIO. It lets the common i.MX pinctrl core get/set pad state and parse SCU-format pin entries.

## Important APIs, Types, and Functions
Defines SCU pad RPC function IDs, wake IRQ constants, packed RPC messages `imx_sc_msg_req_pad_set`, `imx_sc_msg_req_pad_get`, `imx_sc_msg_resp_pad_get`, and `imx_sc_msg_gpio_set_pad_wakeup`. Exported APIs are `imx_pinctrl_sc_ipc_init()`, `imx_pinconf_get_scu()`, `imx_pinconf_set_scu()`, and `imx_pinctrl_parse_pin_scu()`. A module-global `pinctrl_ipc_handle` stores the SCU IPC handle.

## Control Flow
Initialization enables SCU wake pad IRQ delivery and obtains the global IPC handle. `imx_pinconf_get_scu()` builds an `IMX_SC_RPC_SVC_PAD` / `IMX_SC_PAD_FUNC_GET` request and returns the firmware pad value. `imx_pinconf_set_scu()` treats one config word as a wakeup setting and sends `SET_WAKEUP`; otherwise it expects mux and config words, combines them with `BM_PAD_CTL_IFMUX_ENABLE`, `BM_PAD_CTL_GP_ENABLE`, and `BP_PAD_CTL_IFMUX`, then sends `IMX_SC_PAD_FUNC_SET`. `imx_pinctrl_parse_pin_scu()` consumes three big-endian DT cells: pin ID, mux mode, and config.

## State and Persistence Behavior
The only driver-local mutable state is `pinctrl_ipc_handle`. Actual pad state persists in SCU firmware/hardware. Parsed per-pin state is stored in the common i.MX `struct imx_pin` as SCU mux/config fields. Wakeup configuration may persist according to SCU policy and affects low-power behavior.

## Dependencies and Integration Points
Depends on `linux/firmware/imx/sci.h`, the i.MX pinctrl core, SCU RPC services, and i.MX pad-control bit definitions from `pinctrl-imx.h`. It is exported for SoC-specific i.MX SCU pinctrl drivers and integrates with DT pinctrl entries in SCU format.

## Risks
`pinctrl_ipc_handle` is global, so multiple SCU pinctrl instances assume one SCU endpoint. `num_configs == 1` is overloaded as wakeup configuration; callers must preserve that convention. Packed message sizes and function IDs must match firmware ABI. Failure to initialize IPC before get/set calls will break all pad operations.

## Test Signals
SCU handle acquisition, wake IRQ enablement, successful pad get/set RPCs, correct parsing of three-cell pin entries, wakeup-only configuration calls, mux/config calls with expected firmware values, SCU RPC error propagation, and suspend/resume wake events are useful signals.
