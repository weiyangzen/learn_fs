# Group Research: group_377_freebsd_src_sources_os_bsd_freebsd_src_sbin_ipfw_nat_c_sources_os_bs_c120eabe333e

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/freebsd-src`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/nat.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/nat.c

## Purpose
Implements the `ipfw nat` userland command support for in-kernel IPv4 NAT44 configuration, deletion, listing, and log/config display.

## Main Responsibilities
- Parses `ipfw nat <id> config ...` options into `struct nat44_cfg_nat` plus variable-length redirect payloads.
- Supports NAT address selection by static IPv4 address or dynamic interface address.
- Handles NAT flags such as `log`, `deny_in`, `same_ports`, `unreg_only`, `unreg_cgn`, `skip_global`, `reset`, `reverse`, `proxy_only`, and `udp_eim`.
- Parses `redirect_addr`, `redirect_port`, and `redirect_proto` rules, including LSNAT-style server pools.
- Implements NAT instance deletion with `IP_FW_NAT44_DESTROY`.
- Lists NAT instances and fetches either configuration or log data with `IP_FW_NAT44_LIST_NAT`, `IP_FW_NAT44_XGETCONFIG`, and `IP_FW_NAT44_XGETLOG`.

## Key Implementation Details
- `set_addr_dynamic()` walks routing interface sysctl data using `NET_RT_IFLIST` to find an interface by name and capture its first IPv4 address.
- Redirect parsing uses helpers inherited from `natd.c` style logic:
  - `StrToAddr()`
  - `StrToPortRange()`
  - `StrToProto()`
  - `StrToAddrAndPortRange()`
- Redirect records are packed into a single contiguous buffer after `ipfw_obj_header` and `nat44_cfg_nat`.
- `estimate_redir_addr()` and `estimate_redir_port()` pre-compute variable payload size before allocation.
- `setup_redir_port()` enforces equal local/public port range sizes and special SCTP constraints where target port remapping is not allowed.
- `nat_port_alias_parse()` validates `port_range` values as privileged-excluding ranges from 1024 through 65535.
- `nat_show_cfg()` mutates the local fetched copy of `n->mode` while printing flags, which is safe because fetched data is temporary display data.

## Kernel/Userland Interface
Uses `do_set3()` and `do_get3()` wrappers around ipfw socket operations:
- `IP_FW_NAT44_XCONFIG`
- `IP_FW_NAT44_DESTROY`
- `IP_FW_NAT44_LIST_NAT`
- `IP_FW_NAT44_XGETCONFIG`
- `IP_FW_NAT44_XGETLOG`

## Notable Edge Cases
- NAT ID must be numeric and greater than zero.
- `same_ports` and `port_range` are mutually exclusive.
- Optional redirect arguments are detected by checking whether the next token begins with a digit, so hostname-style optional addresses are not accepted in those positions.
- Dynamic interface NAT falls back to `INADDR_ANY` when the interface exists but has no IPv4 address.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/nat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/nat64clat.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/nat64clat.c

## Purpose
Implements `ipfw nat64clat` command handling for CLAT-side NAT64 translation instances.

## Main Responsibilities
- Handles `create`, `config`, `destroy`, `list`/`show`, and `stats [reset]`.
- Requires instance names unless operating on `all` for destroy/list.
- Parses and validates CLAT and PLAT IPv6 prefixes.
- Supports flags `log`/`-log` and `allow_private`/`-allow_private`.
- Retrieves and prints NAT64 CLAT statistics.

## Key Implementation Details
- Defaults PLAT prefix to `64:ff9b::/96` on create.
- Requires `clat_prefix`; `plat_prefix` is also tracked as a required create field though it has a default.
- Prefix validation is delegated to shared `ipfw_check_nat64prefix()`.
- Existing config is fetched before mutation in `nat64clat_config()`, then updated and written back.
- `nat64clat_foreach()` dynamically resizes list buffers on `ENOMEM`, then optionally sorts by set and numeric-aware name comparison.

## Kernel/Userland Interface
Uses:
- `IP_FW_NAT64CLAT_CREATE`
- `IP_FW_NAT64CLAT_CONFIG`
- `IP_FW_NAT64CLAT_DESTROY`
- `IP_FW_NAT64CLAT_STATS`
- `IP_FW_NAT64CLAT_RESET_STATS`
- `IP_FW_NAT64CLAT_LIST`

## Output Behavior
`nat64clat_show_cb()` prints:
- optional `set N`
- instance name
- `clat_prefix`
- `plat_prefix`
- optional `log`
- optional `allow_private`

## Notable Edge Cases
- `all` is accepted only for `destroy` and `list`/`show`.
- `config` requires at least one option.
- Prefix arguments to `config` must include `/length`; create parsing assumes a slash is present when converting length.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/nat64clat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/nat64lsn.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/nat64lsn.c

## Purpose
Implements `ipfw nat64lsn` command handling for large-scale stateful NAT64 instances.

## Main Responsibilities
- Handles create/config/destroy/list/show/stats for NAT64 LSN.
- Supports `list states` in addition to configuration listing.
- Parses IPv4/IPv6 prefixes, queue lengths, aging timers, state chunk counts, and feature flags.
- Fetches detailed runtime statistics and prints state table entries.

## Key Implementation Details
- Create defaults include:
  - `prefix6 64:ff9b::/96`
  - `max_ports NAT64LSN_MAX_PORTS`
  - queue length `NAT64LSN_JMAXLEN`
  - default host, portgroup, TCP, UDP, and ICMP aging values.
- `prefix4` is required on create.
- `nat64lsn_parse_prefix()` duplicates and splits the prefix string, validates family-specific prefix length, masks the prefix, and stores the length.
- `nat64lsn_apply_mask()` applies IPv4 or IPv6 prefix masks before sending config to kernel.
- `max_ports` remains accepted for old configuration compatibility but is otherwise marked unused in the command table.
- Config changes are restricted to mutable parameters; prefix changes are rejected through the default error path.
- `nat64lsn_print_states()` decodes paged `ipfw_nat64lsn_stg_v1` and `ipfw_nat64lsn_state_v1` records, printing IPv6 host, alias IPv4, protocol, flags, idle age, and destination.

## Kernel/Userland Interface
Uses:
- `IP_FW_NAT64LSN_CREATE`
- `IP_FW_NAT64LSN_CONFIG`
- `IP_FW_NAT64LSN_DESTROY`
- `IP_FW_NAT64LSN_STATS`
- `IP_FW_NAT64LSN_RESET_STATS`
- `IP_FW_NAT64LSN_LIST`
- `IP_FW_NAT64LSN_LIST_STATES`

## Output Behavior
- `show` prints config, including non-default timers when verbose or changed.
- `stats` prints packet, fragment, route, memory, job queue, host, portgroup, and state counters.
- `list states` pages through kernel state chunks until sentinel index `0xFF`.

## Notable Edge Cases
- IPv6 prefix length is limited to `<= 96`.
- `set != 0` filtering in `nat64lsn_states_cb()` means explicit set filtering is slightly different from files using `g_co.use_set`.
- State-dump buffer is fixed at 4096 bytes per request and reset between pages.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/nat64lsn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/nat64stl.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/nat64stl.c

## Purpose
Implements `ipfw nat64stl` support for stateless NAT64 translation instances backed by IPv4 and IPv6 ipfw tables.

## Main Responsibilities
- Handles `create`, `config`, `destroy`, `list`/`show`, and `stats [reset]`.
- Validates NAT64 prefixes via shared `ipfw_check_nat64prefix()`.
- Requires `table4`, `table6`, and `prefix6` at create time.
- Supports flags `log` and `allow_private`.
- Retrieves and displays stateless NAT64 counters.

## Key Implementation Details
- Provides `ipfw_check_nat64prefix()`, shared by NAT64 CLAT/LSN code.
- Rejects inappropriate NAT64 prefixes such as multicast, unspecified, loopback, invalid prefix lengths, and well-known prefix with non-96 length.
- Uses `table_fill_ntlv()` to encode table references for `table4` and `table6`.
- Default `prefix6` is `64:ff9b::/96`.
- Config-time table and prefix changes are compiled out under `#if 0`; only flags can be changed.

## Kernel/Userland Interface
Uses:
- `IP_FW_NAT64STL_CREATE`
- `IP_FW_NAT64STL_CONFIG`
- `IP_FW_NAT64STL_DESTROY`
- `IP_FW_NAT64STL_STATS`
- `IP_FW_NAT64STL_RESET_STATS`
- `IP_FW_NAT64STL_LIST`

## Output Behavior
`show` prints instance name, table names, prefix, and optional flags.

## Notable Edge Cases
- Prefix parser requires explicit `/length`.
- `all` is accepted only for destroy and list.
- The source comment notes one prefix validation check “looks incorrect,” highlighting a potential historical concern around prefix filtering.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/nat64stl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/nptv6.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/nptv6.c

## Purpose
Implements `ipfw nptv6` command handling for IPv6 network prefix translation instances.

## Main Responsibilities
- Handles `create`, `destroy`, `list`/`show`, and `stats [reset]`.
- Parses internal prefix, external prefix or external interface, and prefix length.
- Enforces RFC 6296-style prefix length consistency.
- Supports dynamic external prefixes via interface name.
- Retrieves and prints translation statistics.

## Key Implementation Details
- `nptv6_parse_prefix()` accepts IPv6 prefixes with optional `/length`, validating lengths from 8 through 64.
- Create requires:
  - `int_prefix`
  - exactly one external source: `ext_prefix` or `ext_if`
  - `prefixlen`, either explicitly or inferred from deprecated prefix suffixes.
- If prefix lengths are embedded in `int_prefix`/`ext_prefix` without `prefixlen`, the command works but warns to use `prefixlen`.
- Internal and static external prefixes are masked with `n2mask()` and `APPLY_MASK()`.
- Dynamic external interface mode stores `if_name` and sets `NPTV6_DYNAMIC_PREFIX`.

## Kernel/Userland Interface
Uses:
- `IP_FW_NPTV6_CREATE`
- `IP_FW_NPTV6_DESTROY`
- `IP_FW_NPTV6_STATS`
- `IP_FW_NPTV6_RESET_STATS`
- `IP_FW_NPTV6_LIST`

## Output Behavior
`show` prints:
- optional set
- instance name
- internal prefix
- either external prefix or external interface
- prefix length

## Notable Edge Cases
- Rejects specifying both `ext_prefix` and `ext_if`.
- Rejects mismatched embedded prefix lengths and explicit `prefixlen`.
- Interface names must fit in `cfg->if_name`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/nptv6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/tables.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/tables.c

## Purpose
Implements userland handling for in-kernel `ipfw table` objects, including creation, mutation, lookup, listing, information display, algorithm listing, and value listing.

## Main Responsibilities
- Handles table commands:
  - `add`
  - `delete`
  - `create`
  - `destroy`
  - `flush`
  - `modify`
  - `swap`
  - `info`
  - `detail`
  - `list`
  - `lookup`
  - `atomic add`
  - `lock`
  - `unlock`
- Parses table types: address, MAC, interface, number, and flow.
- Parses table value masks: legacy, skipto, pipe, fib, nat, dscp, tag, divert, netgraph, limit, IPv4 next-hop, IPv6 next-hop, and mark.
- Supports bulk entry add/delete and per-entry result reporting.
- Supports compatibility auto-create for legacy add operations into nonexistent tables.
- Fetches and prints table algorithm metadata and shared value metadata.

## Key Implementation Details
- `ipfw_table_handler()` centralizes command dispatch and validates whether `all` is legal for the selected operation.
- `table_create()` supports `type`, `valtype`, `algo`, `limit`, `locked`, `missing`, and `or-flush`.
- Default algorithms preserve compatibility:
  - `addr:radix`
  - `flow:hash`
  - `iface:array`
  - `number:array`
- `table_parse_type()` supports flow suboptions such as `src-ip`, `proto`, `src-port`, `dst-ip`, and `dst-port`.
- `table_do_modify_record()` serializes one or many `ipfw_obj_tentry` records under an `ipfw_obj_ctlv`; atomic operations set `IPFW_CTF_ATOMIC`.
- `tentry_fill_key_type()` parses keys for all supported table types, including IPv4/IPv6 CIDR, MAC masks, interface names, numbers, and flow tuple fields.
- `guess_key_type()` preserves legacy behavior and dry-run behavior by inferring table type from the key.
- `tentry_fill_value()` parses legacy values and typed values, including DSCP names, IPv4/IPv6 next-hop addresses, and hexadecimal marks.
- `table_show_entry()` formats entries according to table type and value mask.
- `tables_foreach()` fetches all tables, sorts them by numeric-aware table name, and filters by active set when needed.

## Kernel/Userland Interface
Uses:
- `IP_FW_TABLE_XCREATE`
- `IP_FW_TABLE_XMODIFY`
- `IP_FW_TABLE_XDESTROY`
- `IP_FW_TABLE_XFLUSH`
- `IP_FW_TABLE_XSWAP`
- `IP_FW_TABLE_XINFO`
- `IP_FW_TABLE_XADD`
- `IP_FW_TABLE_XDEL`
- `IP_FW_TABLE_XFIND`
- `IP_FW_TABLES_XLIST`
- `IP_FW_TABLE_XLIST`
- `IP_FW_TABLES_ALIST`
- `IP_FW_TABLE_VLIST`

## Output Behavior
- `info` prints table identity, type, refs, value type, algorithm, item count, size, and optional limit.
- `detail` adds algorithm class details, item sizes, and per-AF metadata when available.
- `list` prints entries and optionally table headers for `all`.
- Add/delete operations print per-entry status unless quiet behavior suppresses expected duplicate/not-found cases.

## Notable Edge Cases
- `atomic` is only accepted with `add`.
- `table swap` translates `EINVAL` and `EFBIG` into user-facing type/limit messages.
- Locked tables cause mutations to report `table is locked`.
- Legacy auto-create is deliberately warned as deprecated unless quiet.
- IPv4 strings accepted by `inet_aton()` but not `inet_pton()` can be rejected during type guessing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/tables.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/tests/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/tests/Makefile

## Purpose
Registers ipfw tests with the FreeBSD ATF test framework.

## Main Responsibilities
- Marks the package as `tests`.
- Adds one pytest test file: `test_add_rule.py`.
- Adds one shell ATF test: `ipfw_test`.
- Includes `bsd.test.mk`.

## Integration Points
- Relies on FreeBSD build infrastructure variables `ATF_TESTS_PYTEST` and `ATF_TESTS_SH`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/tests/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/tests/ipfw_test.sh -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/tests/ipfw_test.sh

## Purpose
Provides an ATF shell integration test for NPTv6 command behavior inside a vnet jail.

## Main Responsibilities
- Creates a vnet jail with an epair interface.
- Loads/requires `ipfw_nptv6`.
- Exercises valid NPTv6 create/list/destroy forms.
- Verifies invalid forms fail and leave no NPTv6 instances behind.

## Key Test Coverage
Valid cases:
- `int_prefix`, `ext_prefix`, and explicit `prefixlen`.
- Dynamic external prefix via `ext_if`.
- Prefixes with embedded `/64` plus explicit `prefixlen`.
- Deprecated embedded prefix length inference, checking warning output.

Invalid cases:
- Supplying both `ext_prefix` and `ext_if`.
- Mismatched embedded prefix lengths.
- Mismatched explicit `prefixlen`.

## Integration Points
- Sources `vnet.subr`.
- Uses `atf_check`, `jexec`, `ifconfig`, and `ipfw nptv6`.
- Requires root and `ipfw_nptv6`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/tests/ipfw_test.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/tests/test_add_rule.py -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/tests/test_add_rule.py

## Purpose
Pytest-based parser/serialization tests for `ipfw add` rule compilation, validating the exact ioctl/TLV byte structures emitted by `/sbin/ipfw`.

## Main Responsibilities
- Builds expected `IpFwXRule` structures using Python helper classes.
- Runs `ipfw` through `DebugIoReader` to capture generated ioctl records.
- Compares expected and actual byte output.
- Provides recursive object-diff printing to diagnose mismatched TLV/insn trees.

## Key Test Coverage
- Rule numbers and basic accept rules.
- IPv4/IPv6 zero-mask simplification.
- OR address blocks.
- Table references and table lookups.
- Lookup masks for mark, MAC, IPv4, jail, and IPv6 fields.
- Table value checks for legacy, NAT, NH4, and NH6 values.
- Comments.
- External actions such as `tcp-setmss` and `nptv6`.
- Stateful rule constructs: `check-state`, `keep-state`, and `record-state`.
- Action compilation for allow/accept/deny/reject/reset/unreach/count/queue/pipe/skipto/netgraph/divert/tee/call/setdscp/reass/return.
- Single instructions such as `prob`, protocol, and port matching.
- Source and destination port range compilation.

## Key Implementation Details
- `compile_rule()` wraps expected instructions in `CTlvRule` and optional object-name TLVs.
- `verify_rule()` asserts exactly one ioctl request is generated.
- `differ()` recursively compares object byte representations and prints missing/extra/different objects.

## Integration Points
Imports support from `atf_python.sys.netpfil.ipfw`, including instruction, ioctl, enum, and utility classes.

## Notable Edge Cases
- Some imports are broad because the test suite constructs many instruction variants.
- One `setfib` case is skipped because it depends on `net.fibs > 1`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/tests/test_add_rule.py -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/kldconfig/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/kldconfig/Makefile

## Purpose
Builds the `kldconfig` runtime utility.

## Main Responsibilities
- Sets `PACKAGE=runtime`.
- Builds `PROG=kldconfig`.
- Installs `kldconfig.8`.
- Includes `bsd.prog.mk`.

## Notes
The file is mostly copyright/license boilerplate plus minimal FreeBSD build metadata.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/kldconfig/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/kldconfig/kldconfig.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/kldconfig/kldconfig.c

## Purpose
Implements the `kldconfig` utility for reading and modifying the kernel module search path, normally `kern.module_path`.

## Main Responsibilities
- Reads the module path sysctl.
- Parses semicolon-separated module path components into a tail queue.
- Adds, inserts, removes, deduplicates, prints, and writes path components.
- Supports overriding the sysctl name with `-S`.

## Key Implementation Details
- `getmib()` resolves the sysctl name to a MIB once.
- `getpath()` reads current sysctl value with a two-step size/data sysctl call.
- `setpath()` rebuilds the path string and writes it back with `sysctl()`.
- `addpath()` canonicalizes via `realpath()` when possible, strips trailing slash, rejects duplicates unless forced, and supports insertion before previously inserted paths.
- `rempath()` mirrors path normalization before removal.
- `parsepath()` splits path strings on `;`, optionally enforcing uniqueness.
- `qstring()` reconstructs a semicolon-separated sysctl value.

## Command-Line Behavior
Options include:
- `-d` remove paths.
- `-f` suppress duplicate/missing diagnostics.
- `-i` insert before existing path elements.
- `-m` merge with existing path.
- `-n` dry run.
- `-r` print current path.
- `-S` select sysctl name.
- `-U` remove duplicates.
- `-v` verbose display.

## Notable Edge Cases
- With no arguments, it defaults to merge mode.
- `-r` cannot be combined with path arguments.
- If replacing a non-empty current path without merge/list/unique behavior, `changed` is set even before adding new entries.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/kldconfig/kldconfig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/kldload/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/kldload/Makefile

## Purpose
Builds the `kldload` runtime utility.

## Main Responsibilities
- Sets `PACKAGE=runtime`.
- Builds `PROG=kldload`.
- Installs `kldload.8`.
- Includes `bsd.prog.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/kldload/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/kldload/kldload.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/kldload/kldload.c

## Purpose
Implements `kldload`, the command-line utility for loading kernel linker modules.

## Main Responsibilities
- Loads one or more kernel modules using `kldload()`.
- Supports quiet, verbose, and already-loaded tolerant behavior.
- Warns when a bare `.ko` filename in the current directory may be shadowed by a module found in `kern.module_path`.

## Key Implementation Details
- `path_check()`:
  - Ignores names containing `/`.
  - Only checks names containing `.ko`.
  - Compares current-directory file `st_dev/st_ino` against files found through `kern.module_path`.
  - Warns if the module path version differs from the current directory file.
- Main loop attempts each module independently and accumulates errors.
- `-n` treats `EEXIST` as success.
- `-v` prints loaded module ID or already-loaded notice.
- `-q` suppresses warnings.

## Kernel/Userland Interface
- Reads `kern.module_path` through `sysctlnametomib()` and `sysctl()`.
- Loads modules with `kldload()`.

## Notable Edge Cases
- `ENOEXEC` prints a dmesg-oriented diagnostic instead of only `warn()`.
- If `path_check()` cannot find the bare `.ko` in module path, loading is skipped and counted as an error.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/kldload/kldload.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/kldstat/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/kldstat/Makefile

## Purpose
Builds the `kldstat` runtime utility.

## Main Responsibilities
- Sets `PACKAGE=runtime`.
- Builds `PROG=kldstat`.
- Installs `kldstat.8`.
- Links against `libutil`.
- Includes `bsd.prog.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/kldstat/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/kldstat/kldstat.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/kldstat/kldstat.c

## Purpose
Implements `kldstat`, which lists loaded kernel linker files and modules.

## Main Responsibilities
- Lists all loaded KLD files or a selected file by ID/name.
- Finds and displays a module by module name.
- Supports verbose module listing under each file.
- Supports humanized size output.
- Optionally displays module data fields.

## Key Implementation Details
- `printfile()` uses `kldstat()` to fetch `struct kld_file_stat`, then prints ID, refs, address, size, and name.
- Verbose mode prints pathname and contained modules via `kldfirstmod()`/`modfnext()`.
- `printmod()` fetches `struct module_stat` using `modstat()`.
- `-m` uses `modfind()`.
- `-n` uses `kldfind()`.
- Quiet mode returns success/failure without printing when searching.

## Kernel/Userland Interface
Uses:
- `kldnext()`
- `kldstat()`
- `kldfind()`
- `kldfirstmod()`
- `modfnext()`
- `modfind()`
- `modstat()`

## Output Behavior
- Default columns: ID, refs, address, size, name.
- `-h` uses `humanize_number()`.
- `-d` adds module data tuple printing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/kldstat/kldstat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/kldunload/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/kldunload/Makefile

## Purpose
Builds the `kldunload` runtime utility.

## Main Responsibilities
- Sets `PACKAGE=runtime`.
- Builds `PROG=kldunload`.
- Installs `kldunload.8`.
- Includes `bsd.prog.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/kldunload/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/kldunload/kldunload.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/kldunload/kldunload.c

## Purpose
Implements `kldunload`, the command-line utility for unloading kernel linker files.

## Main Responsibilities
- Unloads modules by file ID or by name.
- Supports forced unload.
- Supports verbose display before unloading.

## Key Implementation Details
- `-i` treats arguments as numeric file IDs.
- Without `-i`, arguments are resolved with `kldfind()`.
- `-f` selects `LINKER_UNLOAD_FORCE`; otherwise uses `LINKER_UNLOAD_NORMAL`.
- `-v` fetches `kld_file_stat` and prints module name and ID before unloading.
- `-n` is accepted as a backward-compatible no-op.

## Kernel/Userland Interface
Uses:
- `kldfind()`
- `kldstat()`
- `kldunloadf()`

## Notable Edge Cases
- ID parsing uses `atoi()` and checks only for negative values, so non-numeric strings become `0`.
- The error message for invalid ID references `optarg` even though the failing string is held in `filename`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/kldunload/kldunload.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ldconfig/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ldconfig/Makefile

## Purpose
Builds the `ldconfig` runtime utility.

## Main Responsibilities
- Sets `PACKAGE=runtime`.
- Builds `PROG=ldconfig`.
- Compiles `elfhints.c` and `ldconfig.c`.
- Adds include path for `libexec/rtld-elf`.
- Installs `ldconfig.8`.
- Includes `bsd.prog.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ldconfig/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ldconfig/elfhints.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ldconfig/elfhints.c

## Purpose
Implements ELF hints file reading, listing, directory validation, and atomic writing for `ldconfig`.

## Main Responsibilities
- Maintains a bounded directory list for runtime linker search hints.
- Reads existing ELF hints files.
- Reads directories from command-line arguments or list files.
- Applies security checks to untrusted directories.
- Writes updated hints files with selected endianness.
- Lists search directories and discovered shared libraries.

## Key Implementation Details
- `add_dir()` rejects untrusted directories that are not root-owned or are group/world-writable unless `insecure` is set.
- `list_elf_hints()` prints search directories and scans them for `lib*.so.<version>` names.
- `read_dirs_from_file()` parses whitespace-separated directory list files, ignoring comments and warning on trailing characters.
- `read_elf_hints()` mmaps an existing hints file privately, validates magic/version, handles forced big-endian compatibility, and extracts the colon-separated directory list.
- `COND_SWAP()` abstracts little-endian versus big-endian hints format conversion.
- `update_elf_hints()` optionally merges existing hints, treats regular files as directory-list files, and writes the final hints file.
- `write_elf_hints()` writes to `hintsfile.XXXXXX`, chmods it `0444`, writes the header and string table, then renames atomically.

## Data Constraints
- Maximum directories: `1024`.
- Maximum hints file size: `16 KiB`.

## Notable Edge Cases
- Missing hints files are allowed only when `must_exist` is false.
- Hints files with unexpected endianness are rejected when `force_be` is requested.
- Directory strings from an mmap are temporarily split in place because mapping is private writable.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ldconfig/elfhints.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ldconfig/ldconfig.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ldconfig/ldconfig.c

## Purpose
Provides the main command-line interface for `ldconfig`.

## Main Responsibilities
- Parses compatibility mode prefixes such as `-elf`, `-aout`, and `-32`.
- Chooses the appropriate hints file path.
- Dispatches to list or update ELF hints functions.
- Handles merge, rescan, insecure, big-endian, and custom hints file flags.

## Key Implementation Details
- `-aout` is explicitly unsupported.
- `-elf` is accepted and skipped for compatibility.
- `-32` selects the 32-bit ELF hints path.
- `-B` forces big-endian hints output/validation.
- `-R` requests rescan behavior.
- `-f` overrides hints file.
- `-i` sets global `insecure`.
- `-m` merges with current hints.
- `-r` lists current hints.
- `-s` and `-v` are accepted compatibility no-ops.

## Integration Points
Calls:
- `list_elf_hints()`
- `update_elf_hints()`

## Notable Edge Cases
- With no path arguments and not just reading, it enables rescan.
- Merge is forced when rescanning so existing hints are read before writing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ldconfig/ldconfig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ldconfig/ldconfig.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/ldconfig/ldconfig.h

## Purpose
Declares the shared interface between `ldconfig.c` and `elfhints.c`.

## Contents
- Include guard `LDCONFIG_H`.
- Includes `<stdbool.h>`.
- Declares global `bool insecure`, controlled by the `-i` flag.
- Declares:
  - `void list_elf_hints(const char *);`
  - `void update_elf_hints(const char *, int, char **, bool, bool);`

## Integration Points
This header is included by both the CLI driver and ELF hints implementation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ldconfig/ldconfig.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/md5/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/md5/Makefile

## Purpose
Builds the multi-algorithm digest utility installed as `md5` and many hard-linked command aliases.

## Main Responsibilities
- Builds `PROG=md5`.
- Creates links for MD5, RIPEMD160, SHA variants, and Skein variants, including GNU-style `*sum` names.
- Installs matching manual-page links.
- Links against `libmd`.
- Optionally enables Capsicum/Casper fileargs support when available and not bootstrapping.
- Adds tests subdirectory when tests are enabled.

## Supported Aliases
Includes:
- `md5`, `md5sum`
- `rmd160`, `rmd160sum`
- `sha1`, `sha1sum`
- `sha224`, `sha224sum`
- `sha256`, `sha256sum`
- `sha384`, `sha384sum`
- `sha512`, `sha512sum`
- `sha512t224`, `sha512t224sum`
- `sha512t256`, `sha512t256sum`
- `skein256`, `skein256sum`
- `skein512`, `skein512sum`
- `skein1024`, `skein1024sum`

## Notable Build Detail
`shasum` compatibility links are documented but commented out.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/md5/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/md5/md5.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/md5/md5.c

## Purpose
Implements FreeBSD’s multi-algorithm checksum utility, supporting BSD-style digest commands, GNU `*sum` compatibility, and partial Perl `shasum` compatibility.

## Main Responsibilities
- Selects digest algorithm based on executable name or `shasum -a`.
- Supports MD5, SHA1, SHA224, SHA256, SHA384, SHA512, SHA512/224, SHA512/256, RIPEMD160, Skein256, Skein512, and Skein1024.
- Reads files, stdin, or strings and emits checksums in several output formats.
- Verifies checksum files in BSD/GNU/Perl-compatible modes.
- Provides self-test vectors and a time trial benchmark.
- Optionally uses Capsicum/Casper fileargs for sandboxed file opening.

## Key Implementation Details
- `Algorithm[]` maps executable/program names to digest init/update/end/data functions and expected test output tables.
- Mode is inferred from `progname`:
  - `mode_bsd` for names like `md5`, `sha256`.
  - `mode_gnu` for names ending in `sum`.
  - `mode_perl` for `shasum`.
- Input modes:
  - binary
  - text
  - universal newline normalization
  - bit-string mode
- Output modes:
  - bare digest
  - tagged BSD format
  - reverse format
  - GNU format
- `gnu_check()` parses checksum files in both BSD tagged format and GNU format, building a linked list of checksum records.
- `MDInput()` streams data in 4096-byte blocks, optionally teeing stdin to stdout for passthrough mode.
- Universal mode normalizes CR/CRLF to LF before hashing.
- Bit input mode packs ASCII `0`/`1` characters into bytes and rejects non-byte-aligned input.
- `MDOutput()` handles normal printing and check-result reporting, including quiet/status behavior.
- `MDTimeTrial()` hashes a large fixed block workload and reports speed.
- `MDTestSuite()` hashes built-in vectors and marks failures.
- `safename()` uses `vis(3)` escaping before printing filenames.

## Command-Line Behavior
BSD-style options include:
- `-c string`
- `-p`
- `-q`
- `-r`
- `-s string`
- `-t`
- `-x`

GNU/Perl-style options include:
- `--check`
- `--ignore-missing`
- `--quiet`
- `--status`
- `--strict`
- `--tag`
- `--text`
- `--binary`
- `--warn`
- `--zero`
- `--version`

Perl-style adds:
- `-a`/`--algorithm`
- `-0`/`--01`
- `-U`/`--UNIVERSAL`

## Security/Capability Behavior
When built with Capsicum:
- Limits stdio rights early.
- Initializes fileargs with read/fstat/fcntl rights.
- Enters capability mode before opening input files through Casper.

## Notable Edge Cases
- GNU check mode rewrites `argv` to filenames parsed from checksum records.
- `ignoreMissing` suppresses missing-file failures only in checksum mode.
- BSD `-b` is a no-op for compatibility.
- In GNU mode, output defaults to true GNU format rather than historical FreeBSD reverse behavior.
- Exit code is `1` for operational failure or strict malformed checksum input, and `2` when checksums fail after successful processing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/md5/md5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/md5/tests/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/md5/tests/Makefile

## Purpose
Registers the md5 test script with the FreeBSD ATF test framework.

## Main Responsibilities
- Sets `PACKAGE=tests`.
- Adds shell ATF test `md5_test`.
- Includes `bsd.test.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/md5/tests/Makefile -->