<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/lib/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/fw/lib/Makefile

**Purpose:** Builds shared generic firmware monitor helpers for MIPS.

**Important APIs/types/functions:** Always builds `cmdline.o`; builds `call_o32.o` only for `CONFIG_64BIT`.

**Control flow:** Kbuild conditionally adds objects to the arch library; no runtime logic exists.

**State, dependencies, integration:** Integrates generic boot argument parsing and the 64-bit-to-O32 call bridge with firmware-specific users.

**Risks and test signals:** Missing `call_o32.o` on 64-bit firmware paths breaks 32-bit PROM calls. Test 32-bit and 64-bit MIPS builds with firmware code using `call_o32`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/lib/Makefile -->
