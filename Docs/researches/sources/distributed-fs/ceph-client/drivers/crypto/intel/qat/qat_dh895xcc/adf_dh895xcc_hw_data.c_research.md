# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xcc/adf_dh895xcc_hw_data.c

Purpose: defines DH895xCC physical-function hardware characteristics and operation callbacks for the common QAT ADF layer.

Important APIs and functions: `adf_init_hw_data_dh895xcc()` fills `struct adf_hw_device_data` with BAR IDs, bank/ring counts, masks, firmware names, admin/arbiter/interrupt/reset/config callbacks, heartbeat callbacks, PF/VF messaging ops, CSR ops, and compression ops. Helpers derive accelerator/AE masks from fuses, compute capabilities from legacy fuse bits, return SKU, timestamp clock, SRAM/ETR/MISC BARs, and arbiter thread mappings. VF2PF interrupt helpers enable, disable, and atomically mask pending VF interrupts across lower/upper ERR registers. `adf_clean_hw_data_dh895xcc()` decrements class instance count.

Control flow: PF probe allocates hw data, calls this init function, then common ADF startup uses the populated callbacks for IRQ allocation, admin comms, arbiter setup, firmware config, SR-IOV, reset, and capability checks. VF2PF interrupt masking reads source and mask registers, disables all VF2PF sources, then re-enables only non-pending/non-disabled sources to avoid losing racing interrupts.

State and persistence: increments the static class instance counter and stores chip constants in `hw_data`. Runtime state such as fuse-derived masks and capability masks is kept by the caller in `hw_data`.

Dependencies and integration points: depends on gen2 QAT common config, CSR, PF/VF, heartbeat, admin, and compression helper layers. Firmware names match module firmware declarations in the PF driver.

Risks and test signals: fuse polarity is important because set bits disable units/features. VF2PF masking is race-sensitive and should be tested with simultaneous VF messages. Capability tests should cover disabled cipher/auth/PKE/compression slices. Probe tests should validate firmware names, BAR mapping, heartbeat clock, class instance accounting, and SR-IOV callback wiring.
