# sources/distributed-fs/openafs/src/WINNT/afsd/cm_ioctl.h

Purpose: public interface and wire-structure definitions for Windows OpenAFS cache-manager pioctl handlers implemented mainly in `cm_ioctl.c`.

Important APIs/types/functions: `cm_ioctl_t` tracks input/output allocation bases, current input/output cursors, copied byte counts, and flags such as `CM_IOCTLFLAG_DATAIN`, `CM_IOCTLFLAG_LOGON`, `CM_IOCTLFLAG_USEUTF8`, and `CM_IOCTLFLAG_DATAOUT`. Server preference structs (`cm_SPref_t`, `cm_SPrefRequest_t`, `cm_SPrefInfo_t`, `cm_SSetPref_t`) define get/set server preference payloads. `cm_cacheParms_t` carries cache metrics. `cm_ioctlQueryOptions_t` is an extensible pioctl option block with `literal` and `fid` fields guarded by `CM_IOCTL_QOPTS_HAVE_*` macros. The header declares sysname globals, UTF-8 pioctl prefix constants, RX stats flags, and a large set of pioctl handler prototypes.

Control flow and integration: pioctl front ends allocate/fill `cm_ioctl_t`, parse paths/query options using the helpers declared here, and dispatch to handlers by opcode. Handler declarations are grouped by functional area: ACLs, cache flushing, volume/cell/server preference operations, mount point/symlink manipulation, token lifecycle, submount creation, RX encryption/stats, UUID/unicode controls, memory dump, path availability, Unix mode, verify data, and caller access.

State and persistence: the header itself stores no data except extern declarations, but it defines ABI-sensitive structures consumed by external tools and third-party pioctl callers. Comments explicitly warn that query option flags must remain consistent across implementations.

Dependencies: includes `cm_user.h` for internal builds, but can expose only pioctl interface structures under `__CM_IOCTL_INTERFACES_ONLY__` with a local `cm_fid_t` definition.

Risks: structure layouts and flag values are public ABI; changing field order, sizes, or macros can break existing clients. Flexible trailing arrays (`servers[1]`) require careful length validation by handlers.

Test signals: ABI size/layout checks, 32/64-bit build coverage, UTF-8 prefix handling, query-option compatibility with older clients, and command-level pioctl coverage for every declared handler.
