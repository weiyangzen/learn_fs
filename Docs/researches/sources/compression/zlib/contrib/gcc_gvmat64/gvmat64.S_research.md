# sources/compression/zlib/contrib/gcc_gvmat64/gvmat64.S

Purpose: provides an x86-64 assembly implementation of zlib's `longest_match()` hot path for faster deflate matching.

Important APIs/types/functions: global symbols `longest_match` and `match_init`. Macros define zlib constants, stack local slots, saved registers, and hard-coded offsets into `deflate_state` such as `dsWindow`, `dsPrev`, `dsStrStart`, `dsMatchStart`, `dsLookahead`, and `dsNiceMatch`.

Control flow: the function saves callee-saved registers, maps System V arguments into working registers, reduces chain length when the previous match is good, computes the match limit and scan pointers, then walks the hash chain. Candidate matches are filtered by start/end word checks and compared in 8-byte groups. Longer matches update `s->match_start`; reaching `nice_match`, `MAX_MATCH`, chain exhaustion, or distance limit exits with the best length capped by lookahead.

State and persistence: mutates `deflate_state.match_start` and returns the best match length. It reads the window and prev arrays but does not allocate or persist state.

Dependencies/integration: tightly depends on `deflate_state` layout, zlib match constants, x86-64 instruction set, assembler syntax switches, and the deflate code selecting this symbol.

Risks: hard-coded structure offsets are the major hazard; any layout drift can corrupt memory. The comments describe Windows calling conventions, but the active code uses System V register mapping. Architecture, symbol underscore, and assembler dialect assumptions must match the build.

Test signals: covered only indirectly by zlib deflate correctness and performance tests when this object is linked.
