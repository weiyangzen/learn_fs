# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_regs.h

Purpose: Defines the main DCORE0 MME low-control MMIO register addresses. The block includes architecture status and command registers, sync-object programming, descriptor shortcuts, QM stall/log/shadow controls, EUS/PCU tuning, protection, EU/SBTE controls, counters, debug, clock, and ETF memory wrap addresses at 0x40CB000-0x40CB4EC.

Important APIs/types/functions: Exports 70 `mmDCORE0_MME_CTRL_LO_*` address macros, represented by `mmDCORE0_MME_CTRL_LO_ARCH_STATUS` (0x40CB000), `mmDCORE0_MME_CTRL_LO_CMD` (0x40CB004), `mmDCORE0_MME_CTRL_LO_ARCH_SYNC_OBJ_DW0` (0x40CB148), `mmDCORE0_MME_CTRL_LO_ARCH_SYNC_OBJ_ADDR0` (0x40CB14C), `mmDCORE0_MME_CTRL_LO_ARCH_SYNC_OBJ_VAL0` (0x40CB150), and `mmDCORE0_MME_CTRL_LO_ETF_MEM_WRAP_RM` (0x40CB4EC). There are no functions or types.

Control flow: Driver and firmware code reads status, programs descriptor-related registers, tunes control fields through mask constants, then writes command/control registers to launch or manage MME work.

State and persistence behavior: The file itself is stateless. The named registers hold live device state such as command, status, thresholds, debug counters, and protection settings until reset or explicit writes.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. `gaudi2_security.c` references this block in security/privilege region handling, and companion mask headers define field packing.

Risks: This is a central control surface; wrong addresses can stall the queue manager, alter protection, or misconfigure rate limiting. Generated-file drift against silicon is high impact.

Test signals: Gaudi2 driver build, security-region list validation, MME bring-up tests, command/status polling tests, register dump decode, and error-injection around QM stall and SBTE/EU fields.
