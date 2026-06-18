# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec.c

## Purpose

`qcom_pmic_typec.c` is the top-level Qualcomm PMIC Type-C/TCPM platform driver. It aggregates the PMIC Type-C port block and, when present, the PD PHY block into one `tcpc_dev` registered with TCPM.

## Important APIs, Types, and Functions

`struct pmic_typec_resources` maps compatible data to `pmic_typec_port_resources` and optional `pmic_typec_pdphy_resources`. `qcom_pmic_typec_probe()` creates `struct pmic_typec`, obtains the parent regmap and `reg` base offsets, calls `qcom_pmic_typec_port_probe()`, calls either `qcom_pmic_typec_pdphy_probe()` or `qcom_pmic_typec_pdphy_stub_probe()`, gets the connector fwnode, allocates a DRM DP HPD bridge, registers the TCPM port, starts port and PD PHY blocks, and adds the bridge. `qcom_pmic_typec_remove()` stops PD PHY and port, unregisters TCPM, and releases the fwnode.

## Control Flow

Probe is resource-data driven: PM8150B gets both port and PD PHY resources using `reg[0]` and `reg[1]`, while PMI632 gets only the port and the stub PD callbacks. After both sub-blocks install their `tcpc_dev` callbacks, the top-level driver registers TCPM and starts hardware in port-before-PD-PHY order. Error paths unwind PD PHY start, port start, TCPM registration, and fwnode reference.

## State and Persistence Behavior

`struct pmic_typec` holds all runtime state and callback pointers, with sub-block state owned by the port and PD PHY probe helpers. No persistent storage exists; hardware state is configured on start and reset by sub-blocks.

## Dependencies and Integration Points

It depends on platform device matching, OF compatible data, parent regmap, TCPM, Type-C mux/connector fwnodes, regulators used by sub-blocks, and DRM AUX HPD bridge. It integrates Qualcomm PMIC Type-C hardware with the generic TCPM state machine.

## Risks and Test Signals

Risks include strict `reg` index expectations, missing connector child, start-order assumptions, optional PD PHY stub semantics for no-PD devices, and HPD bridge failures after hardware start. Test signals include PM8150B and PMI632 probes, regmap absence, missing connector, TCPM registration failure, port/PD PHY start failure unwind, remove ordering, and HPD bridge registration.
