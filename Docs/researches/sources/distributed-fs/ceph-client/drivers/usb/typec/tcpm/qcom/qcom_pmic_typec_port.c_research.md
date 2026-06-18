# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec_port.c

## Purpose

`qcom_pmic_typec_port.c` implements the Qualcomm PMIC Type-C port-controller half of the TCPM adapter. It maps PMIC Type-C status/config registers to TCPM callbacks for CC, VBUS, VCONN, polarity, and DRP toggling.

## Important APIs, Types, and Functions

`struct pmic_typec_port` stores device, TCPM port, regmap/base, IRQ data, VBUS regulator and state, VBUS mutex, cached CC, debounce state and delayed work, and a spinlock for register atomicity. Installed TCPM callbacks are `qcom_pmic_typec_port_get_vbus()`, `set_vbus()`, `set_cc()`, `get_cc()`, `set_polarity()`, `set_vconn()`, and `start_toggling()`. Lifecycle functions are `qcom_pmic_typec_port_probe()`, `qcom_pmic_typec_port_start()`, and `qcom_pmic_typec_port_stop()`.

## Control Flow

Probe allocates state, validates IRQ resources, gets `vdd-vbus`, initializes locks/work, requests named IRQs with `IRQF_NO_AUTOEN`, installs TCPM callbacks, and assigns start/stop functions. Start enables PMIC interrupt masks, starts in Try.SNK mode, configures software VCONN control and exit thresholds, stores the TCPM port, and enables IRQs. IRQs read misc status and notify TCPM of VBUS or CC changes unless a software CC debounce window is active. VBUS set toggles the regulator and polls for vSafe5V/vSafe0V. CC get decodes source or sink status registers based on attach, orientation, and mode bits. CC set programs source current when sourcing and debounces before TCPM re-reads.

## State and Persistence Behavior

Runtime state tracks regulator-backed VBUS enablement, cached requested CC, and a short software debounce flag. PMIC hardware maintains attach/orientation/status registers. The VBUS mutex serializes regulator and state changes, while the spinlock protects register sequences and debounce flags.

## Dependencies and Integration Points

It depends on regmap, platform named IRQs, regulator core, delayed work, TCPM, Type-C mux-related orientation integration, and the shared Qualcomm PMIC container. Polarity is intentionally left to the Qualcomm QMP PHY.

## Risks and Test Signals

Risks include returning success even when vSafe polling warns on timeout, `set_cc()` not writing sink/source mode command directly except through toggling paths, 2 ms debounce hiding genuine quick CC changes, DT IRQ-name dependence, and VBUS notifications while under regulator transitions. Test signals include get/set VBUS with vSafe polling, CC decode for source/sink/audio/debug cases, Try.SNK/DRP toggling, VCONN orientation inversion, IRQ-driven TCPM notifications, debounce behavior, and start/stop IRQ enablement.
