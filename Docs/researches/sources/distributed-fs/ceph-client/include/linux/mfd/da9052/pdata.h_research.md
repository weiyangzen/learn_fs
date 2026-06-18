## sources/distributed-fs/ceph-client/include/linux/mfd/da9052/pdata.h

Purpose: This header defines platform data for non-DT DA9052 PMIC board integrations.

Important APIs, types, and constants: `DA9052_MAX_REGULATORS` is 14. `struct da9052_pdata` contains LED platform data, an optional board init callback, IRQ and GPIO bases, an APM-use flag, and an array of regulator init-data pointers indexed by DA9052 regulator IDs.

Control flow: Board code passes this structure to the DA9052 MFD core. During initialization, the core may call `init(da9052)`, use IRQ/GPIO bases, provide LED data to LED children, and pass regulator init data to regulator children.

State and persistence: The structure is static board/runtime configuration. It has no persistence beyond platform device data and does not itself hold hardware state.

Dependencies and integration points: It forward-declares `struct da9052` and references LED and regulator platform data types supplied by including code. Integrates with DA9052 MFD, LED, GPIO, IRQ, APM, and regulator frameworks.

Risks: The regulator array must be ordered exactly as expected by DA9052 regulator descriptors. Callback failure semantics depend on core implementation. Legacy base-number fields can conflict with dynamically allocated GPIO/IRQ numbering.

Test signals: Board-file compile coverage, regulator init-data count/order checks, init callback success/failure behavior, LED platform data propagation, and IRQ/GPIO base assignment in child devices.
