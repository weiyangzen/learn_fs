# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/tbldo.S

Purpose: defines the primary monadic FPSP dispatch table `tblpre`. The table maps a combined opcode/source-tag index to the correct software routine or special-case handler for unimplemented floating-point instructions.

Important APIs/types/functions: exported symbol is `tblpre`. Entries point to math routines such as `ssinh`, `stanh`, `stan`, `stwotox`, `stentox`, `scosh`, `sacos`, `ssin`, `scos`, log routines, integer-conversion routines, `ssincos`, and dyadic generic entries such as `pmod`, `prem`, and `pscale`. Special handlers include `szero`, `sinf`, `sone`, `src_nan`, `serror`, `t_operr`, `t_dz2`, `ld_pone`, `ld_pinf`, and `ld_ppi2`.

Control flow: this file is data-only. The caller, normally `do_func`, uses a 10-bit index where the upper seven bits are opcode and lower three bits are source tag. Normal, zero, infinity, NaN, denormal, and invalid tag cases have separate entries, allowing common special values to bypass general algorithms.

State and persistence: no mutable or persistent state. The table is static read-only dispatch data assembled into the FPSP text/data image.

Dependencies/integration: tightly integrated with `do_func.S`, `get_op.S`, and all function implementations referenced by the table. The table layout is a contract: changing opcode order or source-tag meaning without updating the decoder will dispatch to incorrect routines.

Risks: because this is a positional table, missing or misordered entries cause silent incorrect emulation. Many unsupported opcode/tag combinations intentionally point to `serror`; accidental replacement with a real function would mask illegal instruction conditions. The repeated `fsincos` opcode range must stay consistent with hardware encodings.

Test signals: validate every documented opcode/tag pair against expected target labels, illegal-extension opcodes against `serror`, normal/zero/inf/NaN/denormal dispatch for functions in this subset, and `fsincos` opcode variants across `$30-$37`.
