# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/util.S

Purpose: provides shared FPSP helper routines for overflow/underflow result selection, instruction decoding, opcode reads, destination-format/rounding-precision lookup, and integer data-register writeback.

Important APIs/types/functions: exported labels are `ovf_r_k`, `ovf_r_x2`, `ovf_r_x3`, `ovf_res`, `get_fline`, `g_rndpr`, `g_opcls`, `g_dfmtou`, `unf_sub`, and `reg_dest`. Static tables `tblovfl` and `tblunf` select results by precision and rounding mode. Result constants encode infinities, largest finite values, zeros, and smallest denormals in internal extended format.

Control flow: overflow helpers choose precision from kernel exception context, opclass, force-precision fields, destination format, or FPCR; `ovf_res` combines precision and rounding mode into a table dispatch and writes the selected internal extended result while preserving sign. `get_fline` reads the interrupted opcode through `mem_read`. `g_rndpr`, `g_opcls`, and `g_dfmtou` decode E1/E3 command words. `unf_sub` mirrors overflow selection for catastrophic underflow. `reg_dest` indexes a table of byte/word/long write handlers for `D0-D7`.

State and persistence: no persistence. It mutates the current FPSP frame: `FPSR_CC`, `USER_FPSR`, `LOCAL_EX/HI/LO`, and saved `USER_D0/USER_D1` where needed. Writes to `D2-D7` go directly to live data registers because only `D0-D1/A0-A1` are saved in the local frame.

Dependencies/integration: depends on `fpsp.h` bit definitions and on `mem_read`. Called by overflow, underflow, store, operand-error, and signaling-NaN handlers. Its decoding helpers are shared by code that must distinguish opclass 3 move-out instructions from register-destination operations.

Risks: table indexes pack precision in bits `{3:2}` and rounding mode in bits `{1:0}`; decoding errors change IEEE-visible results. The E1/E3 split is subtle and hardware-specific. `reg_dest` assumes `L_SCR1` contains correctly aligned data and that only `D0/D1` need saved-frame writes.

Test signals: check overflow result matrices for extended/single/double across RN/RZ/RM/RP and signs, underflow zero/smallest-denorm matrices, `g_rndpr` for FPCR and force-precision cases, `g_dfmtou` destination formats, `get_fline` fault propagation via `mem_read`, and all `reg_dest` register/size combinations.
