# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_pci.h

Purpose: declares the shared AIE2 hardware interface, firmware-facing metadata, register-index enums, runtime configuration categories, firmware feature bits, per-device private configuration, and prototypes for the AIE2 PSP/SMU/PM/message/context helpers.

Important APIs and types: `struct amdxdna_dev_hdl` is the live device-handle backing AIE2 ops, containing BAR bases, PSP handle, management mailbox resources, protocol version, AIE metadata, feature mask, execution-message ops, power/DPM state, mailbox pointers, async events, device status, and context count. `struct amdxdna_dev_priv` describes per-NPU constants: firmware path, runtime config table, DPM clocks, firmware feature table, column alignment, BAR-relative SRAM/PSP/SMU offsets, mailbox geometry, context limit, and `aie2_hw_ops`. `struct amdxdna_hwctx_priv` is the AIE2-private scheduler/mailbox state for a hardware context. Enums define SMU, SRAM, PSP register slots, runtime config categories, and firmware feature bits.

Control flow: implementation files include this header to translate generic AMD XDNA driver calls into AIE2-specific register, mailbox, PSP, SMU, and firmware-message operations. Macros such as `SMU_REG()`, `SRAM_GET_ADDR()`, `AIE2_SRAM_OFF()`, and `MBOX_SIZE()` normalize per-device BAR layouts.

State and persistence: this header defines state shape only. Runtime state lives in allocated `amdxdna_dev_hdl` and `amdxdna_hwctx_priv` instances; tables in register files persist as const data.

Dependencies and integration points: includes the private AIE2 message ABI, mailbox API, AMD PMF metric hooks, DRM UAPI, PCI conversion, and exported `aie2_ops`. It bridges register-table files, `aie2_pci.c`, `aie2_pm.c`, `aie2_psp.c`, `aie2_smu.c`, context code, and message code.

Risks: register-offset macros assume device-private tables are correct. Firmware feature gating uses bit operations on an `unsigned long` feature mask, so feature-table definitions must stay synchronized with firmware protocol. `HWCTX_MAX_CMDS` must remain a power of two for sequence indexing.

Test signals: compile all NPU register variants, probe every supported revision, validate PMF-disabled builds, and run firmware protocols with and without optional NPU command, preemption, temporal-only, and app-health features.
