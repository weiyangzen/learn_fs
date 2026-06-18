# sources/distributed-fs/ceph-client/arch/parisc/include/asm/sections.h

Purpose: extends generic section declarations with PA-RISC function descriptor and alternatives-section symbols.

Important APIs/types/functions: typedefs `func_desc_t` as `Elf64_Fdesc` on 64-bit and declares `__alt_instructions`/`__alt_instructions_end`.

Control flow: alternatives code walks the alternative instruction section; module/core code may use function descriptor typing for PA-RISC ABI support.

State and persistence: linker-defined section ranges persist in the kernel image. Dependencies and integration: depends on `elf.h`, generic sections, and `alternative.h`.

Risks and test signals: wrong section symbols prevent runtime patching. Test alternatives application, linker map inspection, and 64-bit function descriptor users.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
