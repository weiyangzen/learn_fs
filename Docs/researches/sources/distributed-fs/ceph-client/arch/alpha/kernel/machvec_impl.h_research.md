# sources/distributed-fs/ceph-client/arch/alpha/kernel/machvec_impl.h

**Purpose:** Provides helper macros for instantiating Alpha machine vectors. It fills HAE/IACK defaults, MMU ASID limits, I/O operation tables, PCI operation hooks, and generic-versus-specific machine-vector placement/aliasing behavior.

**Important APIs/types/functions:** Defines HAE address fallbacks for IRONGATE, MARVEL, POLARIS, TSUNAMI, TITAN, WILDFIRE and optional one-window chips; fake `JENSEN_IACK_SC`, `T2_IACK_SC`, and `WILDFIRE_IACK_SC`; token-pasting macros `CAT1/CAT`; `DO_DEFAULT_RTC`; `DO_EV5_MMU`, `DO_EV6_MMU`, `DO_EV7_MMU`; `IO_LITE()`, `IO()`, `DO_*_IO` macros; `__initmv`; and `ALIAS_MV()`.

**Control flow:** No runtime code. System-specific `sys_*.c` files use these macros to initialize `struct alpha_machine_vector` fields. In generic kernels, vectors live in init data so setup can copy the selected one into `alpha_mv`. In non-generic kernels, `ALIAS_MV()` emits an assembler alias from `alpha_mv` to the single compiled vector and exports it.

**State and persistence behavior:** Affects placement and symbol aliasing of machine-vector objects at compile/link time. Runtime state is the selected `alpha_mv`, owned elsewhere.

**Dependencies and integration points:** Central to every Alpha system vector file. It connects core logic I/O functions such as `titan_ioremap`, `tsunami_pci_ops`, and `wildfire_pci_tbi` to the generic `alpha_mv` dispatch used by I/O, PCI, IRQ, and setup code.

**Risks:** Macro expansion must match exact symbol naming conventions for each core logic. Fake IACK values exist only to satisfy initialization and can be dangerous if accidentally used. Generic/non-generic aliasing is toolchain-sensitive and uses inline assembly due to GCC alias limitations.

**Test signals:** Build generic and non-generic Alpha kernels for each supported machine vector, inspect `alpha_mv` symbol resolution, boot enough to exercise I/O calls through machine vectors, and verify selected vector init data is not freed before copy in generic kernels.
