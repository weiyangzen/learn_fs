# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_fline.S

Purpose: handles F-line exceptions that may represent unimplemented floating-point instructions, malformed `fmovecr`, or true illegal F-line instructions. It redirects unimplemented instruction vectors to `fpsp_unimp` and converts one special illegal-frame `fmovecr` case into the unimplemented-instruction path.

Important APIs/types/functions: exported label is `fpsp_fline`. External targets are `real_fline`, `fpsp_unimp`, `uni_2`, `mem_read`, and `fpsp_fmt_error`.

Control flow: before linking a frame, it checks `EXC_VEC-4(%sp)` for the unimplemented vector and branches to `fpsp_unimp` if present. Otherwise it adjusts the stack to account for a shorter frame, saves a local frame, reads the F-line and command word via `mem_read`, and checks for coprocessor id 1 plus `fmovecr` opcode. If matched, it synthesizes an unimplemented fsave frame (`VER_40` or `VER_41`), rewrites SR/PC/vector/EA/CMDREG fields, sets `UFLAG`, restores registers, and branches to `uni_2`. Non-matching instructions restore state and branch to `real_fline`.

State and persistence: no persistence. It rewrites the exception stack frame and FPSP command fields only for the emulated `fmovecr` conversion path.

Dependencies/integration: depends on `fpsp.h` frame constants, `mem_read` for fault-safe instruction fetch, `fpsp_unimp`/`uni_2` for software emulation, and `real_fline` for true illegal instructions.

Risks: stack-frame conversion is fragile because it manually shifts SR/PC fields and fsave sizes. Version-byte validation only accepts known 040 frame versions. Misidentifying an instruction as `fmovecr` would run the wrong emulation path.

Test signals: unimplemented vector dispatch, true illegal F-line dispatch, `fmovecr` with nonzero EA conversion, both original and revised unimplemented fsave versions, invalid fsave format to `fpsp_fmt_error`, and `mem_read` access faults.
