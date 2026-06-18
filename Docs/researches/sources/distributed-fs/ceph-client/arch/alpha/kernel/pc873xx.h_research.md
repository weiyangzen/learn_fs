# sources/distributed-fs/ceph-client/arch/alpha/kernel/pc873xx.h

**Purpose:** Private header for PC873xx Super I/O support. It defines configuration-register indexes, model identifiers, and function prototypes used by platform setup code and `pc873xx.c`.

**Important APIs/types/functions:** Register constants include `REG_FER`, `REG_FAR`, `REG_PTR`, `REG_FCR`, `REG_PCR`, `REG_KRR`, `REG_PMC`, `REG_TUP`, `REG_SID`, `REG_ASC`, and `REG_IRC`. Model constants are `PC87303`, `PC87306`, `PC87312`, `PC87332`, and `PC87334`. Prototypes cover `pc873xx_probe()`, `pc873xx_get_base()`, `pc873xx_get_model()`, `pc873xx_enable_epp19()`, and `pc873xx_enable_ide()`.

**Control flow:** None; it is declarative.

**State and persistence behavior:** None. Constants describe hardware register addressing used by `pc873xx.c`.

**Dependencies and integration points:** Included by the PC873xx implementation and any Alpha platform file that needs Super I/O probing or feature enables.

**Risks:** Register constants must match the National PC873xx configuration protocol. Exposing `pc873xx_get_model()` without an `__init` prototype annotation in callers could cause section mismatch warnings if used incorrectly. Model `PC87312` exists but probe code in this subset does not identify it.

**Test signals:** Build platform files that include this header; verify constants against the chip datasheet and ensure every prototype has a matching implementation and expected init section usage.
