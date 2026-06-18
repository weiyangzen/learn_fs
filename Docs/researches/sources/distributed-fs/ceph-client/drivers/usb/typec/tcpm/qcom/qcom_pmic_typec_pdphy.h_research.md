# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec_pdphy.h

## Purpose

`qcom_pmic_typec_pdphy.h` declares the Qualcomm PMIC PD PHY resource description and probe APIs.

## Important APIs, Types, and Functions

`PMIC_PDPHY_MAX_IRQS` bounds IRQ resources. `struct pmic_typec_pdphy_irq_params` maps a virtual IRQ ID to a named platform IRQ. `struct pmic_typec_pdphy_resources` stores the number of IRQs and the fixed-size parameter array. It declares `pm8150b_pdphy_res`, `qcom_pmic_typec_pdphy_probe()`, and `qcom_pmic_typec_pdphy_stub_probe()`.

## Control Flow

There is no executable control flow. The header supplies resource tables to the top-level compatible match and lets the top-level driver select real or stub PD PHY probing.

## State and Persistence Behavior

The resource structures are static configuration data. Runtime PD PHY state is opaque as `struct pmic_typec_pdphy`.

## Dependencies and Integration Points

It depends on platform devices and regmap and is shared by the top-level PMIC driver, real PD PHY implementation, and stub implementation.

## Risks and Test Signals

Risks include IRQ count/resource-name drift between DT and resource tables and the opaque type hiding lifetime constraints from callers. Test signals are compile coverage, PM8150B IRQ lookup, and PMI632 stub probe selection.
