# sources/distributed-fs/ceph-client/arch/powerpc/crypto/ppc-xlate.pl

Purpose: translates portable PowerPC assembly input into assembler syntax accepted by Linux, AIX, and macOS assemblers. It is used by the PowerPC crypto assembly generation path to normalize symbol naming, directives, local labels, register syntax, and newer instruction encodings.

Important APIs/types/functions: command-line inputs are `flavour` and output path. Directive handlers include `$globl`, `$text`, `$machine`, `$size`, `$asciz`, and `$quad`. Mnemonic shims include `cmplw`, `bdnz`, `bltlr`, `bnelr`, `beqlr`, `extrdi`, `vmr`, `mtspr`, `mfspr`, VSX unaligned memory helpers, and PowerISA 2.07 crypto helpers such as `vcipher`, `vshasigmaw`, and `vpmsumd`.

Control flow: the script opens the output as stdout, emits `<asm/ppc_asm.h>` for Linux, then reads stdin line by line. It strips comments and whitespace, canonicalizes local labels, parses an optional directive/instruction prefix and suffix, optionally removes register class prefixes, dispatches to a Perl code reference when a mnemonic needs translation, and prints either the rewritten line or the default instruction/directive.

State and persistence: persistent output is the generated assembly file only. In-memory state is limited to `%GLOBALS`, the target flavour, and local-label policy. No runtime kernel state is modified.

Dependencies and integration points: depends on Perl and assembler conventions for OpenSSL-derived PowerPC crypto sources. Linux integration relies on `_GLOBAL()` and PowerPC assembler headers; Power8 crypto assembly depends on the emitted `.long` encodings when the assembler does not know newer mnemonics.

Risks: flavour matching is regex-based, so new ABI strings can silently choose the wrong directive path. The `.quad` fallback notes 32-bit Perl arithmetic risk. Register and comment stripping are intentionally simple and can break unusual assembly syntax. The Linux ppc64le vrsave special case substitutes no-op/read-all behavior and must stay ABI-aware.

Test signals: regenerate all PowerPC crypto assembly flavours and build with both old and new binutils. Inspect emitted Linux ppc64le output for `_GLOBAL`, `.abiversion 2`, local labels, and raw instruction encodings for VMX/VSX crypto operations.
