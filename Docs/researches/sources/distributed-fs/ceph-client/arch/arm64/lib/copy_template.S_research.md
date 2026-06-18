# sources/distributed-fs/ceph-client/arch/arm64/lib/copy_template.S

Purpose: common ARM64 copy template included by usercopy routines, parameterized by macros for user/kernel load/store behavior and optional MOPS copy.

Important APIs/types/functions: register aliases `dstin`, `src`, `count`, `dst`, temporary registers, macro calls `ldrb1/ldrh1/ldr1/ldp1/strb1/strh1/str1/stp1/cpy1`, MOPS alternative block, small/tail/large-copy labels, and `.Lexitfunc`.

Control flow: starts with `dst = dstin`, optionally uses MOPS, aligns source to 16 bytes, copies leading bytes in increasing address order, handles sub-64 byte tails, and uses a 64-byte software-pipelined loop for large ranges. The template deliberately avoids the older backward-tail technique so `memmove`-like overlap behavior remains simpler for its instantiations.

State and persistence: no standalone symbol. It mutates registers and writes through whichever store macros the including file provides.

Dependencies/integration: included by `copy_from_user.S` and `copy_to_user.S`, and depends on their exception labels, macro definitions, and ARM64 alternative patching.

Risks: as an include template, register alias conflicts or missing labels in including files break correctness. Fault labels must line up with the user-side operations. The algorithm assumes hardware handles unaligned accesses.

Test signals: both copy-from-user and copy-to-user test matrices, all tail sizes 0..63, source alignment permutations, large copies, partial user faults, and MOPS alternatives.
