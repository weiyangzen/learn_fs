# sources/distributed-fs/ceph-client/arch/microblaze/lib/libgcc.h

Purpose: shared local header for MicroBlaze libgcc-compatible 64-bit helper implementations.

Important APIs and state: defines `word_type`, endian-dependent `struct DWstruct` with high/low 32-bit halves, `DWunion`, and prototypes for 64-bit shift/compare/multiply helpers.

Control flow: preprocessor selects structure field order by `__BIG_ENDIAN` or `__LITTLE_ENDIAN`; otherwise compilation fails.

State and persistence: no runtime state.

Dependencies and integration: included by C libgcc helper files; must match ABI endian layout and compiler helper names.

Risks and test signals: wrong field order corrupts every 64-bit helper. Test helper behavior in big/little endian builds and ensure prototypes match exported symbols.
