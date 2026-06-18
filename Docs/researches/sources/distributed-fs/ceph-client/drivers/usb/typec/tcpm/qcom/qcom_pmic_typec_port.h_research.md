# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec_port.h

## Purpose

`qcom_pmic_typec_port.h` declares the Qualcomm PMIC Type-C port resource description and probe API.

## Important APIs, Types, and Functions

`PMIC_TYPEC_MAX_IRQS` bounds port IRQ resources. `struct pmic_typec_port_irq_params` maps virtual IRQ IDs to platform IRQ names. `struct pmic_typec_port_resources` stores the IRQ count and parameter table. It declares the PM8150B resource table and `qcom_pmic_typec_port_probe()`.

## Control Flow

There is no executable flow. The header defines static configuration consumed by the top-level compatible match and the port implementation.

## State and Persistence Behavior

Resource tables are static configuration. Runtime state is opaque as `struct pmic_typec_port`.

## Dependencies and Integration Points

It depends on platform devices and TCPM declarations and is shared by the top-level Qualcomm PMIC driver and port implementation.

## Risks and Test Signals

Risks include IRQ name/count drift from DT bindings and hidden lifetime assumptions for the opaque port state. Test signals are compile coverage and successful platform IRQ lookup for every PM8150B port IRQ resource.
