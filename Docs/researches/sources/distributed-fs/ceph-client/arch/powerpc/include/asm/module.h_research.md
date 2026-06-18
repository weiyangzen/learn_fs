# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/module.h

Purpose: defines PowerPC module architecture state, PLT/stub section requirements, TOC/GOT metadata, and dynamic ftrace module hooks.

Important APIs/types/functions: 32-bit `struct ppc_plt_entry` models a four-instruction jump stub. `struct mod_arch_specific` tracks 64-bit stubs, GOT/PCREL or TOC sections, ELFv1 OPD ranges, 32-bit PLT sections, ftrace trampolines, and optional out-of-line ftrace stubs. Module builds create `.stubs`, `.mygot`, `.plt`, or `.init.plt` sections as needed. `module_trampoline_target` and `module_finalize_ftrace` support dynamic ftrace.

Control flow: module loader fills arch-specific fields while resolving relocations and creating stubs/PLTs. Ftrace finalization analyzes or creates trampolines after load.

State and persistence: per-module `mod_arch_specific` persists while the module is loaded. Stub/PLT/GOT/TOC sections are allocated in module memory.

Dependencies and integration points: depends on generic module infrastructure, PowerPC relocation code, ELF ABI v1/v2, PC-relative kernel support, and dynamic ftrace.

Risks: 32-bit relative branch range limitations require correct PLT generation. 64-bit TOC/GOT metadata is ABI-sensitive. Ftrace trampoline target resolution must not misidentify module code.

Test signals: load/unload modules on 32-bit and 64-bit PowerPC, exercise far-call relocations, ELFv1 OPD modules, PCREL builds, dynamic ftrace enable/disable, and module strict RWX checks.
