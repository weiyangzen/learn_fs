# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_hwinfo.c

Purpose: Reads and validates the firmware-built HWInfo key/value table, then provides lookup and packed-string accessors.

Important APIs/types/functions: `struct nfp_hwinfo` models the v2 header and packed string data. `nfp_hwinfo_read()` fetches and validates the table. `nfp_hwinfo_lookup()` searches unsorted packed `key\0value\0` pairs. `nfp_hwinfo_get_packed_strings()` and `_size()` expose raw packed data.

Control flow: Fetch first tries `NFP_RESOURCE_NFP_HWINFO`; if absent it falls back to a classic MU island address. `hwinfo_fetch()` polls up to `HWINFO_WAIT` while the table is updating or unavailable. Validation checks declared size, POSIX CRC32, and key/value string bounds before returning the allocated table.

State and persistence: Returned table is a heap snapshot of firmware data; caller owns freeing. Persistent data lives on device firmware/scratch memory, not in kernel state.

Dependencies/integration: Uses CPP reads, resource acquisition, CRC32 helper, NFP resource names from `nfp.h`, and logging macros from `nfp_cpp.h`. Higher layers use HWInfo for board policy/defaults.

Risks: Bad firmware tables can fail CRC or bounds checks. The walker must avoid reading past `size`; lookup assumes validated data. Waiting is interruptible and can fail during boot timing issues.

Test signals: Test valid/invalid CRC tables, updating-bit polling, resource-table and classic-location fetch paths, null lookup handling, and boundary cases with unterminated keys/values.
