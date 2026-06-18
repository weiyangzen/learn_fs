# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/do_func.S

Purpose: FPSP dispatcher and special-case handler for unimplemented 68040 floating-point operations.

Important APIs and labels: exports `do_func`, `serror`, forced-result helpers (`snzrinx`, `szero`, `sinf`, `sone`, `spi_2`, `szr_inf`, `sopr_inf`), log special cases (`sslognp1`, `sslogn`, `sslog10`, `sslog2` and denormal variants), dyadic dispatchers `pmod`, `prem`, `pscale`, sincos special cases, and constant loaders `ld_ppi2`, `ld_mpi2`, `ld_pinf`, `ld_minf`, `ld_pone`, `ld_mone`, `ld_pzero`, `ld_mzero`.

Control flow and state: `do_func` clears `CU_ONLY`, detects `fmovecr` and jumps to `smovcr`, otherwise validates the opcode extension, combines opcode and source tag into an index into `tblpre`, points A0 at `ETEMP`, sanitizes FPCR, and jumps to the selected emulation routine. The rest of the file handles exceptional operand combinations for logs, mod/rem, scale, and sincos through tag jump tables, setting `USER_FPSR` condition/exception bits and returning results in FP0/FP1.

Dependencies and integration: shared FPSP tables and routines (`tblpre`, transcendental functions, `src_nan`, `dst_nan`, `t_operr`, `t_inx2`, `sto_cos`). State is the FPSP local frame and saved user status registers.

Risks and test signals: table index formation must match `tbldo` layout. Exceptional cases must exactly follow 68881/68040 semantics. Test unsupported opcodes, fmovecr, logs of negative/zero/one, mod/rem NaN/zero/inf combinations, fscale, fsincos, and FPSR flags.
