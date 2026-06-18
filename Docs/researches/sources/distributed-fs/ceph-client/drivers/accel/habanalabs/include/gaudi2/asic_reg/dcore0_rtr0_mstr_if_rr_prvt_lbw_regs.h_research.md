# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_rtr0_mstr_if_rr_prvt_lbw_regs.h

Purpose: Defines DCORE0 RTR0 master-interface range-register addresses for private LBW traffic. The block describes secured range minima/maxima, non-secured range minima/maxima, range masks, security-region configuration, decoders, access-error capture, and RAZWI error response at 0x4142600-0x4142748.

Important APIs/types/functions: Exports 83 `mmDCORE0_RTR0_MSTR_IF_RR_*` address macros, including `mmDCORE0_RTR0_MSTR_IF_RR_PRVT_LBW_SEC_RANGE_MIN_SHORT_0` (0x4142600), `mmDCORE0_RTR0_MSTR_IF_RR_PRVT_LBW_SEC_RANGE_MIN_SHORT_1` (0x4142604), `mmDCORE0_RTR0_MSTR_IF_RR_PRVT_LBW_SEC_RANGE_MIN_SHORT_2` (0x4142608), `mmDCORE0_RTR0_MSTR_IF_RR_PRVT_LBW_SEC_RANGE_MIN_SHORT_3` (0x414260C), `mmDCORE0_RTR0_MSTR_IF_RR_PRVT_LBW_SEC_RANGE_MIN_SHORT_4` (0x4142610), and `mmDCORE0_RTR0_MSTR_IF_RR_PRVT_LBW_RAZWI_ERR_RESP` (0x4142748). There are no functions or C types.

Control flow: Security and address-decoder initialization writes allowed ranges and masks; runtime fault handling reads access-error and RAZWI registers when traffic violates the configured windows.

State and persistence behavior: The header has no software state. The hardware registers persist address-range policy and last-error information until reset or explicit writes.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. These range registers integrate with Gaudi2 security setup, router decode, and HBW/LBW fabric access paths.

Risks: Private/shared or HBW/LBW register windows are similarly named but enforce different traffic classes. Bad range masks can overexpose memory or block legitimate traffic.

Test signals: Secure/nonsecure access tests, range-boundary probes, RAZWI/error-response injection, and register dump comparison for the private LBW policy window.
