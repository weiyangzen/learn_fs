# sources/distributed-fs/lustre-release/include/uapi/linux/lnet/nidstr.h

## Purpose
This UAPI header assigns stable numeric IDs to Lustre Network Drivers and declares the shared NID/network string parsing, formatting, range parsing, and matching APIs used by kernel code and user utilities.

## Important APIs, Types, And Functions
The LND enum assigns values for active drivers such as `SOCKLND`, `O2IBLND`, `LOLND`, `GNILND`, `GNIIPLND`, `PTL4LND`, `KFILND`, `TOFULND`, `EFALND`, and `BXI3LND`, while retaining commented historical values. Formatting helpers include `libcfs_lnd2str_r()`, `libcfs_net2str_r()`, `libcfs_nid2str_r()`, and `libcfs_nidstr_r()` plus inline ring-buffer wrappers. Parsing and matching APIs include `libcfs_str2lnd()`, `libcfs_str2net()`, `libcfs_str2nid()`, `libcfs_strnid()`, `libcfs_str2anynid()`, `libcfs_stranynid()`, `cfs_parse_nidlist()`, `cfs_match_nid()`, `cfs_match_net()`, `cfs_ip_addr_parse()`, and `libcfs_ip_in_netmask()`.

## Control Flow
Formatting callers can either provide explicit buffers or use `libcfs_next_nidstring()` through inline helpers that return one of the shared fixed-size string slots. Parsing functions translate strings into LND IDs, network IDs, legacy NIDs, large NIDs, numeric ranges, and IP/netmask expressions. Matching functions compare a concrete NID, network, or IP address against parsed lists.

## State, Persistence, And Dependencies
The numeric LND values are persistent protocol/address ABI and must not be renumbered. The header declares a shared rotating string buffer contract through `LNET_NIDSTR_COUNT` and `LNET_NIDSTR_SIZE`, but the storage lives in implementation files. It depends on `lnet-types.h` and a forward-declared `struct list_head`.

## Integration Points
All LNet configuration paths, diagnostics, logs, NID parsers, LNDs, and user tools use these declarations. EFA LND depends on `EFALND`, `SOCKLND`, and string helpers for NID generation, TCP metadata discovery, logging, and module registration.

## Risks
Changing LND enum values breaks persisted NIDs and routing compatibility. The inline formatting wrappers return shared buffer slots, so callers must not assume indefinite lifetime or thread ownership beyond the implementation contract. Parser APIs mutate some input strings and consume `list_head` outputs, making ownership and cleanup with `cfs_free_nidlist()` or `cfs_expr_list_free_list()` important.

## Test Signals
Tests should cover every active LND string round trip, historical/reserved numeric stability, IPv4 and large-NID formatting, wildcard NID parsing, NID range min/max discovery, netmask matching, delimiter discovery, and cleanup of parsed expression lists.
