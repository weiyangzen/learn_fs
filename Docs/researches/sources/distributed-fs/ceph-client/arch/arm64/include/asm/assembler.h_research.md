## sources/distributed-fs/ceph-client/arch/arm64/include/asm/assembler.h

### Purpose
Provides the central ARM64 assembly macro library for exception entry, barriers, alternatives, per-CPU access, cache/TLB maintenance, page-table helpers, symbol export, GNU property notes, and Spectre mitigations.

### Important APIs, Types, And Functions
Notable macros include DAIF save/restore, single-step control, `esb`, `csdb`, `clearbhb`, `sb`, `nops`, endian selectors `CPU_BE/CPU_LE`, address pseudo-ops `adr_l/ldr_l/str_l`, per-CPU accessors, CTR/cache-line helpers, TCR/physical address helpers, cache maintenance loops, frame helpers, `EXPORT_SYMBOL_NOKASAN`, GNU property emission, `set_sctlr*`, and Spectre BHB mitigation macros.

### Control Flow
The header has no standalone flow; assembly files expand these macros into boot, exception, MMU, cache, KVM, crypto, and mitigation code. Many macros emit alternative sequences that patch at boot based on CPU capabilities or callbacks.

### State, Persistence, And Dependencies
Macros manipulate CPU registers, DAIF, debug registers, cache state, TCR/SCTLR, per-CPU offsets, and ELF metadata sections. Dependencies include alternative patching, bug/extable/offset/cpufeature/cputype/debug/page/pgtable/ptrace/thread headers and Linux export machinery.

### Integration Points
Included by most ARM64 `.S` files in this subset and beyond; it is foundational for low-level kernel assembly.

### Risks
This file has broad blast radius. Register clobber assumptions, missing barriers, incorrect alternatives, cache maintenance fixups, or mitigation patch callbacks can break boot, security, usercopy, KVM, or crypto assembly.

### Test Signals
Full ARM64 defconfig/allmodconfig builds, boot on varied CPUs, KVM tests, exception/usercopy/cache maintenance tests, Spectre mitigation validation, objdump inspection of alternatives, and crypto assembly builds that rely on `frame_push`/`adr_l` macros.
