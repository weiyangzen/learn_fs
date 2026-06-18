# sources/distributed-fs/ceph-client/arch/arm64/include/asm/module.lds.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/module.lds.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/module.lds.h

### Purpose
`module.lds.h` supplies ARM64 module linker-script fragments for architecture-specific sections.

### Important APIs, Types, And Functions
It defines section layout snippets for PLT/GOT, alternatives, unwind/metadata, or architecture note sections needed by ARM64 modules.

### Control Flow
There is no runtime flow. The linker consumes these macros while building modules, and the module loader later relies on the resulting section layout.

### State, Persistence, And Dependencies
The persistent output is ELF section placement in `.ko` files. It depends on the kernel module linker script and ARM64 module loader expectations.

### Integration Points
Used by Kbuild/module linking for ARM64 loadable modules.

### Risks
Misplaced sections break relocation, alternatives patching, or security metadata. Linker-script drift can be hard to diagnose until module load time.

### Test Signals
Build external and in-tree modules, inspect section tables, load/unload modules with alternatives and PLTs enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/module.lds.h -->
