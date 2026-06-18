# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec_pdphy_stub.c

## Purpose

`qcom_pmic_typec_pdphy_stub.c` provides no-op PD PHY callbacks for Qualcomm PMIC Type-C controllers that have a Type-C port block but no PD PHY hardware, such as the PMI632 resource path.

## Important APIs, Types, and Functions

`qcom_pmic_typec_pdphy_stub_probe()` installs stub `set_pd_rx`, `set_roles`, and `pd_transmit` callbacks plus no-op start/stop functions. `qcom_pmic_typec_pdphy_stub_pd_transmit()` logs the transmit type and immediately calls `tcpm_pd_transmit_complete(..., TCPC_TX_SUCCESS)`.

## Control Flow

Probe attaches stub callbacks to the shared `tcpc_dev`. TCPM can then call PD operations without NULL callbacks even though no hardware messages are sent. Start returns success and stop does nothing.

## State and Persistence Behavior

The stub stores no additional state and changes no hardware. Its only externally visible behavior is debug logging and immediate transmit completion.

## Dependencies and Integration Points

It depends on TCPM, USB PD types, and the shared Qualcomm PMIC container. It integrates no-PD-PHY PMIC variants into the same top-level driver as full PD-capable PMICs.

## Risks and Test Signals

Risks include reporting PD transmit success without actual PD transport if TCPM attempts PD negotiation on stub-only hardware, and relying on higher-level capabilities/configuration to avoid unsupported PD flows. Test signals include PMI632 probe, TCPM startup without PD PHY resources, stub callbacks invoked without crashes, and no regulator/IRQ side effects.
