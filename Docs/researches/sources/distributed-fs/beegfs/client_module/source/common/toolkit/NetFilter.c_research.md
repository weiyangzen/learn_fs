# sources/distributed-fs/beegfs/client_module/source/common/toolkit/NetFilter.c

## Purpose
Implements IP/CIDR allow-list filtering for client networking. The filter is loaded from a configured file into an array of IPv6-form entries; IPv4 rules are represented as IPv4-mapped IPv6 addresses.

## Important APIs and control flow
`NetFilter_construct`, `NetFilter_init`, `NetFilter_uninit`, and `NetFilter_destruct` manage allocation and parsed state. `NetFilter_isAllowed` allows all traffic if no entries exist and otherwise delegates to `NetFilter_isContained`. `NetFilter_isContained` always permits IPv4 and IPv6 loopback, then masks the input address and compares it to pre-masked entries. `parse_NetFilterEntry` accepts IPv4 or IPv6 text with a slash prefix, validates prefix bounds, builds masks with `beegfs_make_in6_addr_mask_from_prefix`, and stores `mask` plus `compare`. `__NetFilter_prepareArray` loads lines with `Config_loadStringListFile`, preallocates a worst-case array, and appends only successfully parsed entries.

## State, dependencies, integration
State is an in-memory `filterArray` and length. Dependencies include `Config`, `StrCpyList`, kernel `in4_pton`/`in6_pton`, `SocketTk` address helpers, and Linux IPv6 comparison helpers. `DatagramListener` uses the filter when sending UDP messages to node NICs.

## Risks and test signals
Invalid rows are logged but ignored, so a partially malformed file may silently reduce policy strictness. `kstrtou8(slash + 1, ...)` assumes parsing set `slash`; rules without a slash should be tested. Cover IPv4 `/0..32`, IPv6 `/0..128`, loopback bypass, empty filename, load failure, and malformed prefixes.
