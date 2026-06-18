# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec.h

## Purpose

`qcom_pmic_typec.h` defines the shared top-level state object used by the Qualcomm PMIC Type-C port and PD PHY subdrivers.

## Important APIs, Types, and Functions

`struct pmic_typec` stores the device, TCPM port, embedded `struct tcpc_dev`, pointers to PD PHY and port sub-block state, and start/stop callbacks for each block. `tcpc_to_tcpm()` converts a `tcpc_dev` callback receiver back to the owning `pmic_typec`.

## Control Flow

The header has no executable flow. It defines how subdrivers install TCPM callbacks and lifecycle functions during probe.

## State and Persistence Behavior

The structure is runtime-only state allocated by the top-level platform driver and used until remove. Callback pointers are installed by port and PD PHY probe helpers.

## Dependencies and Integration Points

It assumes users include the TCPM declarations that define `struct tcpm_port` and `struct tcpc_dev`. It is the central integration contract between `qcom_pmic_typec.c`, `qcom_pmic_typec_port.c`, `qcom_pmic_typec_pdphy.c`, and the PD PHY stub.

## Risks and Test Signals

Risks include callback pointer ordering, incomplete callback installation when a sub-block probe fails, and tight container-of coupling. Test signals are compile coverage and probe paths for both real and stub PD PHY configurations.
