<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/module.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/module.h

**Purpose:** Adds Alpha-specific module metadata on top of the generic module header. It records the GOT section index needed for Alpha GP-relative relocation handling and declares the small-data section flag.

**Important APIs/types/functions:** `struct mod_arch_specific { unsigned int gotsecindex; }`, `ARCH_SHF_SMALL`, and the module-only inline assembly that creates an aligned `.got` section.

**Control flow:** There is no runtime control flow in the header. Module loading code consumes `mod_arch_specific` while resolving module sections and Alpha relocations; the `MODULE` preprocessor branch emits the GOT section at compile time.

**State and persistence behavior:** The state is loader-visible module metadata, not persistent storage. `gotsecindex` persists only for the lifetime of a loaded module.

**Dependencies and integration points:** Depends on `asm-generic/module.h`, ELF section flags such as `SHF_ALPHA_GPREL`, and the Alpha module loader implementation.

**Risks:** Relocation failures or missing GOT section setup can break loadable modules that use GP-relative addressing. ABI drift in `mod_arch_specific` affects module loader expectations.

**Test signals:** Build and load Alpha kernel modules with GP-relative data, inspect section layout for `.got`, and compile both built-in and `MODULE` configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/module.h -->
