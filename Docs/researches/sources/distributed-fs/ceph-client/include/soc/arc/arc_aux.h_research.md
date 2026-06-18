# sources/distributed-fs/ceph-client/include/soc/arc/arc_aux.h

Purpose: abstracts ARC auxiliary register access for code shared between ARC and non-ARC builds.

Important APIs and types: `read_aux_reg()` and `write_aux_reg()` map to ARC compiler builtins under `CONFIG_ARC`; otherwise they compile to harmless stubs. `READ_BCR(reg, into)` and `WRITE_AUX(reg, into)` copy between 32-bit auxiliary register values and typed bitfield structs, deliberately failing link-time through `bogus_undefined()` if sizes do not match.

Control flow: ARC platform code reads build/configuration registers into typed structs, modifies control words, and writes them back through the aux register programming model. Non-ARC users can include the header without introducing architecture-specific instructions.

State and persistence: no independent state exists; helpers read and write processor auxiliary registers, whose state is CPU-local hardware state.

Dependencies and integration points: depends on ARC compiler builtins and is used by MCIP and timer headers to expose register-level programming helpers.

Risks and test signals: risks include passing expressions with side effects into macros, strict-aliasing or layout assumptions in typed copies, non-ARC stub masking accidental runtime use, and wrong bitfield width. Test ARC compile/runtime register reads, non-ARC compile coverage, endian bitfield users, and size mismatch diagnostics.
