<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/cfe/cfe_api_int.h -->
## sources/distributed-fs/ceph-client/arch/mips/fw/cfe/cfe_api_int.h

**Purpose:** Defines internal Broadcom CFE IOCB command numbers and parameter block layouts used by `cfe_api.c`.

**Important APIs/types/functions:** Provides `CFE_CMD_*` constants, `cfe_xptr_t`, payload structs for buffer, input status, environment, CPU control, time, exit status, memory info, firmware info, and the top-level `struct cfe_xiocb`.

**Control flow:** No executable code; firmware wrappers populate these structs and CFE fills status/result fields.

**State, dependencies, integration:** The ABI is persistent across firmware calls: all fields use fixed signed/unsigned 64-bit sizes, and pointer fields are signed `cfe_xptr_t`.

**Risks and test signals:** Layout drift breaks firmware calls silently. Test with compile-time size/offset checks if available and runtime smoke tests for each command family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/cfe/cfe_api_int.h -->
