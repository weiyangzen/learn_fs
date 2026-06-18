# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_11_0_8_offset.h

Purpose: generated AMD MP 11.0.8-specific register-offset header. It gives PSP/SMU code symbolic offsets for the MP0 and MP1 SMN mailbox blocks on ASICs using the 11.0.8 MP layout, including the extended scratch registers needed by that firmware generation.

Important APIs and state: the file exports `mmMP0_SMN_C2PMSG_32..103` at `0x0060..0x00a7`, MP0 interrupt helper registers at `0x00c1..0x00c3`, `mmMP1_SMN_C2PMSG_32..103` at `0x0260..0x02a7`, MP1 interrupt helpers and `FPS_CNT` at `0x02c1..0x02c4`, and `mmMP1_SMN_EXT_SCRATCH0..7` at `0x03c0..0x03c7`. All `_BASE_IDX` values are `0`.

Control flow: none in this header. Its offsets feed PSP 11.0.8 runtime flows: `psp_v11_0_8.c` writes MP0 C2P registers to program ring base, size, write pointers, doorbells, TMR metadata, and bootloader commands; it also reads MP0 response/status registers while polling for firmware progress.

State and persistence: the macros are compile-time constants only. The underlying MP0 registers hold PSP boot and ring state, and MP1 scratch registers expose firmware-owned scratch data across driver interactions until reset or firmware overwrite. Because the extended scratch registers are full hardware locations, they must be treated as live device state rather than stable configuration.

Dependencies and integration: protected by `_mp_11_0_8_OFFSET_HEADER`. It is directly included by `amdgpu/psp_v11_0_8.c`, whose register access uses `WREG32_SOC15`, `RREG32_SOC15`, and `SOC15_REG_OFFSET`. It mirrors much of the generic MP 11.0 offset layout but omits generic-only entries such as `ACTIVE_FCN_ID`, `PUB_CTRL`, and PMI public MMU decode macros while adding the scratch range required for this ASIC-specific path.

Risks and test signals: MP 11.0.8 PSP initialization depends on exact MP0 mailbox offsets; a single wrong constant can leave firmware rings uninitialized or cause response polling to timeout. Extended scratch offsets are adjacent and easy to mis-index. Test signals include PSP boot on an MP 11.0.8 ASIC, ring create/destroy, TMR programming, secure display or firmware command traffic if supported, and no timeouts in the MP0 C2P polling paths.
