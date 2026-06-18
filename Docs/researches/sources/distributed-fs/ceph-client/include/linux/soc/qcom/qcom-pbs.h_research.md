# sources/distributed-fs/ceph-client/include/linux/soc/qcom/qcom-pbs.h

Purpose: This header exposes Qualcomm PMIC PBS trigger support for clients that need to execute PMIC programmable boot sequencer scripts.

Important APIs/types/functions: It declares PBS client data types and helper functions for acquiring a PBS client and triggering a sequence, with device-managed integration in the implementation.

Control flow: A driver obtains the PBS client associated with its device or phandle and calls the trigger helper when a PMIC-side sequence is required.

State and persistence: PBS state resides in PMIC hardware/firmware. Triggered sequences may alter regulators, resets, or PMIC registers until explicitly changed.

Dependencies and integration: Integrates with Qualcomm PMIC, regmap/SPMI, power/reset, and peripheral drivers needing PMIC scripts.

Risks and test signals: Wrong PBS trigger can affect board power state. Test probe deferral, absent PBS provider, trigger return codes, and hardware side effects on target boards.
