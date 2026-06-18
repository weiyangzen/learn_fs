# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-x64.c

Purpose: implements the scalar x86-64 dynamic backend for EC GF combination code, emitting 64-bit register operations as a baseline dynamic path when no vector backend is selected.

Important APIs: exports `ec_code_gen_x64` with no required CPU flags and width `sizeof(uint64_t)`. Internal callbacks implement prolog/epilog, load/store, register copy, register XOR, and memory XOR. `ec_code_x64_regmap` maps virtual GF registers onto x86-64 registers.

Control flow: the prolog saves `REG_BP`, optionally `REG_BX` for interleaved source base caching, verifies at most 11 mapped registers, saves extra callee-saved registers, and records the loop address. Load and xorm functions either address a linear source buffer or load a source pointer from an interleaved pointer array when the source index changes. Epilog increments `REG_DX` and `REG_DI` by 8, loops while masked offset bits remain, restores saved registers, and returns.

State and integration: this backend relies on the neutral builder to keep register pressure within `EC_GF_MAX_REGS` and on `ec-code-intel.c` for byte emission. It writes no persistent state beyond generated code chunks. Risks include register-save ABI mistakes, invalid register pressure for large GF tables, loop-width assumptions, and interleaved base caching across source indexes. Test signals should cover all GF widths that approach the 11-register limit, compare with C fallback, and run under sanitizers or valgrind-like tools to catch ABI clobbering.
