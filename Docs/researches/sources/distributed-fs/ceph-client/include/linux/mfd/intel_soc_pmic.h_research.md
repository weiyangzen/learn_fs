# sources/distributed-fs/ceph-client/include/linux/mfd/intel_soc_pmic.h

Purpose: This header defines the common Intel SoC PMIC parent state and helper for executing MIPI PMIC sequence elements. It is shared by Cherry Trail/Whiskey Cove/Basin Cove style PMIC code and child IRQ domains.

Important APIs, types, and functions: `enum intel_cht_wc_models` identifies several Cherry Trail Whiskey Cove board quirks. `struct intel_soc_pmic` stores the master IRQ, regmap, primary and chained regmap IRQ chip data for power button, TMU, BCU, ADC, charger, critical event, device pointer, SCU IPC handle, and board model. `intel_soc_pmic_exec_mipi_pmic_seq_element` applies a register write/masked update described by firmware/MIPI sequence data.

Control flow, state, and persistence: The parent PMIC driver sets up regmap and nested IRQ chips, detects board model quirks, and child drivers use the shared regmap/IRQ data. Firmware sequence execution writes PMIC registers through an I2C address/register/mask/value tuple. State is in PMIC registers, nested IRQ masks/status, and board quirk selection.

Dependencies and integration points: It depends on regmap and Intel SCU IPC. It integrates with ACPI-described PMIC children, power button, thermal, charger, ADC, BCU, GPIO, and regulator drivers.

Risks and test signals: Risks include nested IRQ chip mismatch, board quirk misdetection, executing firmware sequence writes on the wrong I2C address, and mask/value ordering bugs. Test signals include IRQ tree tests, ACPI sequence replay tests, board-specific quirk probes, charger/ADC interrupt tests, and regmap trace verification.
