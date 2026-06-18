<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/cfe/cfe_api.c -->
## sources/distributed-fs/ceph-client/arch/mips/fw/cfe/cfe_api.c

**Purpose:** Provides Linux-side stubs for the Broadcom CFE IOCB firmware API.

**Important APIs/types/functions:** `cfe_init()` stores the dispatch entry and handle. `cfe_iocb_dispatch()` invokes firmware. Device APIs include `cfe_open`, `cfe_close`, `cfe_read{,blk}`, `cfe_write{,blk}`, `cfe_ioctl`, `cfe_inpstat`, `cfe_getstdhandle`, and `cfe_getdevinfo`. Firmware APIs include CPU start/stop, environment get/set/enum, memory enum, ticks, cache flush, exit, firmware info, and `cfe_die()`.

**Control flow:** Each API fills a `struct cfe_xiocb` with a function code, status, handle, flags, parameter size, and union payload, dispatches it, then returns status or a payload result. `cfe_die()` prints through CFE if the entry seal and Broadcom PRId checks pass, applies BMIPS register workarounds, delays, and exits firmware.

**State, dependencies, integration:** Static `cfe_dispfunc` and `cfe_handle` are persistent early firmware state; `cfe_seal` validates the entry point. The file depends on CFE public/internal headers, MIPS PRId registers, memory barriers, and BMIPS CPU conditionals.

**Risks and test signals:** Pointer width is fragile, hence the `intptr_t` dispatch signature and `cfe_xptr_t` casts. `cfe_die()` uses `vsprintf()` into 128 bytes and must be kept to short fatal messages. Test every IOCB command on a CFE emulator/board, 32/64-bit pointer conversions, CFE absence fallback to panic, and BMIPS XKS01 disabling paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/cfe/cfe_api.c -->
