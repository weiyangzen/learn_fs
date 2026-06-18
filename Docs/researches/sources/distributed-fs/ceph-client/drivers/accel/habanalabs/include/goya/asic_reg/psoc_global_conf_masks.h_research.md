# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/psoc_global_conf_masks.h

Purpose: supplies 325 field shift/mask constants for the PSOC global configuration block. The fields cover boot and reset state machines, scratchpad/semaphore values, SPI image status, interrupt aggregation, target IDs, eMMC voltage stable indication, MII speed/address, boot straps, memory repair, outstanding transaction/mask requests, reset source/configuration, pad voltage/default/input/select controls, and trace address bits.

Important APIs/types/functions: no functions or types. Key field groups include `PSOC_GLOBAL_CONF_BOOT_SEQ_RE_START_IND`, `PSOC_GLOBAL_CONF_BOOT_SEQ_FSM_*`, `PSOC_GLOBAL_CONF_BTL_STS_*`, `PSOC_GLOBAL_CONF_TIMEOUT_INTR_*`, `PSOC_GLOBAL_CONF_PERIPH_INTR_*`, `PSOC_GLOBAL_CONF_SW_ALL_RST_*`, `PSOC_GLOBAL_CONF_RST_SRC_*`, `PSOC_GLOBAL_CONF_TRACE_ADDR_MSB_MASK`, and `PSOC_GLOBAL_CONF_PAD_SEL_*`.

Control flow: callers read status registers, mask fields with these constants, branch on boot/reset/interrupt state, or prepare writes to restart boot and assert resets. Goya/Gaudi reset flows write `mmPSOC_GLOBAL_CONF_BOOT_SEQ_RE_START` and `SW_ALL_RST`; CoreSight code masks and writes trace address MSBs.

State and persistence: persistent state is in PSOC registers, including scratchpad and cold/non-reset flop fields that can survive parts of reset sequencing. The header itself is stateless.

Dependencies and integration: included by `goya_regs.h`, paired with `psoc_global_conf_regs.h`, and consumed by Goya driver boot, reset, interrupt, firmware, CoreSight, and pin/pad configuration code.

Risks: reset and boot fields are high blast radius. Mispacked `SW_ALL_RST`, `UNIT_RST_N`, or watchdog/manual reset masks can reset unintended hardware. Scratchpad fields double as host/firmware mailboxes, so masks must match firmware ABI.

Test signals: firmware boot status, reset recovery, interrupt routing, CoreSight trace address setup, memory repair status reporting, pad configuration checks, and warm reboot scratchpad continuity are useful signals.
