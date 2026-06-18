# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_axuser_regs.h

Purpose: auto-generated GPL-2.0 C preprocessor register map for the Gaudi2 `DCORE0_TPC0_CFG_AXUSER` slice, under the TPC prototype. It exports 19 `mmDCORE0_TPC0_CFG_AXUSER_*` MMIO address constants from `0x400BE00` through `0x400BE4C` for TPC configuration AXUSER attributes.

Important APIs/types/functions: no C types or functions are declared. The API is the macro set for high-bandwidth and low-bandwidth AXI user controls: `HB_ASID`, `HB_MMU_BP`, `HB_STRONG_ORDER`, `HB_NO_SNOOP`, `HB_WR_REDUCTION`, `HB_RD_ATOMIC`, `HB_QOS`, `HB_RSVD`, `HB_EMEM_CPAGE`, `HB_CORE`, `E2E_COORD`, write/read override low/high registers, and corresponding LB override registers.

Control flow: none in this file. Driver control flow is external: code includes `gaudi2_regs.h`, then passes these absolute register constants to MMIO read/write helpers or to tables describing protected register regions.

State and persistence behavior: the macros name persistent device register state in the TPC configuration block. Writes affect hardware AXUSER transaction tagging, security/domain selection, snoop/order behavior, QoS, and override routing until reset or reprogramming. The header itself stores no software state.

Dependencies and integration points: included by `gaudi2_regs.h`; reachable from Gaudi2 driver code that includes that aggregate header. It aligns with `gaudi2_blocks_linux_driver.h` block-base metadata for `DCORE0_TPC0_CFG` and with security/access logic in `gaudi2_security.c`, which relies on generated register ranges. Mask definitions for related TPC CFG fields live in `dcore0_tpc0_cfg_masks.h`.

Risks: incorrect addresses or stale generation can silently program the wrong TPC transaction attributes. AXUSER mistakes are security-sensitive because ASID, MMU bypass, secure/non-secure attributes, ordering, and snoop fields affect memory isolation and coherency. Since the file has only macros, compile success does not prove the values match the hardware specification.

Test signals: build coverage catches missing include guards or macro spelling regressions. Meaningful validation comes from generated-header diff review against the hardware register database, MMIO smoke tests that read/write documented AXUSER fields on Gaudi2 hardware, and security tests that ensure protected or privileged AXUSER controls cannot be misused from untrusted paths.
