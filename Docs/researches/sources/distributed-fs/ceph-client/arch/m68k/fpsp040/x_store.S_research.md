# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_store.S

Purpose: provides the shared `store` routine used by overflow and underflow handlers to write an internal extended-format operand to the actual user destination, whether FP register, Dn register for single move-out, or user memory in extended/single/double format.

Important APIs/types/functions: exported labels are `store`, `dest_ext`, `dest_dbl`, and `dest_sgl`. Static `fpreg_mask` converts FP register numbers to dynamic `fmovemx` masks. It calls `mem_write`, `get_fline`, `g_opcls`, `g_dfmtou`, and `reg_dest`.

Control flow: `store` first checks E3; E3 destinations are always FP registers from `CMDREG3B`. E1 non-opclass-3 also stores to an FP register from `CMDREG1B`. Opclass 3 move-out gets destination format through `g_dfmtou`: extended writes 12 bytes, double converts exponent/mantissa into 8-byte IEEE double, and single converts into 4-byte IEEE single. Single destination with null `EXC_EA` is written to Dn through `reg_dest`.

State and persistence: no persistence. It mutates the destination register or user memory, and mirrors `%fp0-%fp3` writes into `USER_FP0..USER_FP3` because exception handlers later restore those registers from the local frame. It may temporarily reinsert the sign bit into `LOCAL_EX`.

Dependencies/integration: depends on internal extended-format layout from `fpsp.h`, safe user memory write support from `mem_write`, and decoder helpers in `util.S`. Called by `x_ovfl.S` and `x_unfl.S`.

Risks: comments state no rounding is attempted during extended-to-single/double conversion; callers must round beforehand. Destination conversion assumes normal/inf encodings and direct bit extraction; denormal bias corrections are handled by underflow before calling `store`. Incorrect saved `%fp0-%fp3` mirroring would lose results on handler exit.

Test signals: E3 FP register stores for all registers, E1 register stores, opclass 3 memory stores for extended/double/single, single Dn destination, positive/negative infinity conversion, sign preservation, and `%fp0-%fp3` saved-frame synchronization.
