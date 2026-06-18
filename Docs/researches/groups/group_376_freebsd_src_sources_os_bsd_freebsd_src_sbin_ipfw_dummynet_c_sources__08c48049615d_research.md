# Group Research: group_376_freebsd_src_sources_os_bsd_freebsd_src_sbin_ipfw_dummynet_c_sources__08c48049615d

Scope: `Docs/research_subset_a.md`, specifically the five requested FreeBSD `sbin/ipfw` source files. All listed files were read completely.

This group covers the userland command-line front end for FreeBSD `ipfw` and `dnctl`: argument dispatch, shared parser definitions, rule compilation/display, dummynet pipe/queue/scheduler configuration, and IPv6-specific rule operand handling. These files are not filesystem code themselves, but they are in the in-scope `sources/os/bsd/freebsd-src` source tree.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/dummynet.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/dummynet.c

## Purpose

`dummynet.c` implements userland support for FreeBSD dummynet objects in the `ipfw`/`dnctl` CLI. It parses `pipe`, `queue`/`flowset`, and `sched` configuration commands; formats kernel-returned dummynet object lists; deletes and flushes dummynet objects; loads empirical delay profile files; and supports RED/GRED plus newer AQM scheduler parameters for CoDel, FQ-CoDel, PIE, and FQ-PIE.

The file speaks the dummynet kernel ABI through `IP_DUMMYNET3` using packed `dn_id`-based TLV-like buffers from `<netinet/ip_dummynet.h>`.

## Public Surface

Exported functions declared in `ipfw2.h`:

- `void ipfw_config_pipe(int ac, char **av)`: parses and submits `pipe N config`, `queue N config`, and `sched N config`.
- `void dummynet_list(int ac, char *av[], int show_counters)`: handles dummynet `list`/`show`.
- `void dummynet_flush(void)`: sends a dummynet flush command.
- `int ipfw_delete_pipe(int pipe_or_queue, int n)`: deletes a pipe, queue/flowset, or scheduler.

Internal helpers include:

- `oid_fill()` and `o_next()` for building request objects in a contiguous buffer.
- `read_bandwidth()` for parsing numeric bandwidths and suffixes.
- `load_extra_delays()` for profile file parsing and interpolation.
- `process_extra_parms()` for CoDel/PIE/FQ parameter parsing.
- `list_pipes()` and related print helpers for rendering kernel responses.
- `parse_range()` for dummynet list filters.

## Main Data and Tokens

`dummynet_params[]` maps CLI words to shared parser tokens from `ipfw2.h`, covering packet loss, masks, queue sizes, RED/GRED, AQM names, bandwidth, delay, scheduler type, IPv4/IPv6 mask fields, profiles, and burst.

With `NEW_AQM` defined locally, `aqm_params[]` maps AQM option names such as `target`, `interval`, `flows`, `quantum`, `tupdate`, `alpha`, `beta`, `ecn`, `capdrop`, `dre`, and `derand`.

The code builds and interprets kernel structures including `dn_sch`, `dn_link`, `dn_fs`, `dn_profile`, `dn_flow`, and `dn_extra_parms`. `g_co.do_pipe` selects the dummynet object class:

- `1`: pipe/link compatibility path.
- `2`: queue/flowset.
- `3`: scheduler.

## Configuration Flow

`ipfw_config_pipe()` is the central parser. It allocates one contiguous command buffer large enough for the command header, scheduler, link, flowset, optional profile, and optional AQM/scheduler extra-parameter blocks. It then:

1. Skips `config` and parses the numeric object id.
2. Builds a different initial object layout depending on `g_co.do_pipe`.
3. Initializes fields to sentinel values when the kernel should reuse existing state.
4. Walks remaining arguments and mutates `dn_sch`, `dn_link`, `dn_fs`, masks, profile, or extra parameter objects.
5. Validates queue limits, delay bounds, RED thresholds, ECN compatibility, and sysctl-derived dummynet limits.
6. Sends the packed command with `do_cmd(IP_DUMMYNET3, ...)`.

Pipe configuration creates a scheduler, link, and FIFO flowset for backward compatibility. Queue configuration only emits a flowset. Scheduler configuration emits a scheduler and a default flowset for non-multiqueue schedulers.

## AQM Handling

The file compiles with `NEW_AQM` enabled. AQM handling is split between:

- `process_extra_parms()`: consumes the remaining argument vector after `codel`, `fq_codel`, `pie`, `fq_pie`, or scheduler `type fq_*`, stores parsed values in `dn_extra_parms.par[]`, and uses `-1` to request kernel defaults.
- `get_extra_parms()`: issues `DN_CMD_GET` requests for `DN_AQM_PARAMS` or `DN_SCH_PARAMS` and formats kernel-returned parameter arrays for listing.

Time values are converted through `time_to_us()` and `us_to_time()`. PIE floating parameters are scaled with `PIE_SCALE` and `PIE_FIX_POINT_BITS`.

One important behavior: selecting `fq_codel`/`fq_pie` through the scheduler `type` consumes the remaining arguments as scheduler-specific parameters, so ordering on the command line is significant.

## Listing and Formatting

`dummynet_list()` builds a `DN_CMD_GET` request, optionally embeds ranges parsed by `parse_range()`, estimates or retries response buffer size, then passes the response to `list_pipes()`.

`list_pipes()` expects the kernel response order described in comments:

- Pipes/schedulers: link, scheduler, internal flowset, instances.
- Flowsets: flowset then queues.

It switches by `oid->type` and renders links, schedulers, flowsets, profiles, flows, child-flowset lists, and unknown objects. Flow formatting supports both IPv4 and IPv6 `ipfw_flow_id` layouts.

`print_flowset_parms()` prints queue size, packet-loss rate, RED/GRED/AQM mode, buckets, scheduler id, weight, `lmax`, priority, and masks. `print_mask()` handles IPv4 and IPv6 masks.

## Delay Profiles

`load_extra_delays()` parses an external profile file with tokens:

- `samples`
- `loss-level`
- `name`
- `bw`
- `delay prob` or `prob delay`

It validates counts and probabilities, sorts points by probability/delay, interpolates delays into `dn_profile.samples[]`, and stores loss and profile name. It requires at least two data points and defaults missing sample count to 100 and missing loss level to no loss.

## Kernel and System Dependencies

This file depends on:

- `do_cmd()` from `ipfw2.c` for `IP_DUMMYNET3` socket operations.
- `g_co` for global command flags, especially `do_pipe`, `verbose`, and sort/list flags.
- `n2mask()` from `ipfw2.c` for IPv6 masks.
- `sysctlbyname()` for queue-size and RED defaults/limits.
- `expand_number()` and `humanize_number()` from libutil for burst/list display.

## Error Handling and Risks

The parser mostly fails fast with `errx()`/`err()` on malformed commands. Buffer construction uses explicit object lengths and `safe_calloc()`/`safe_realloc()`, but correctness depends on keeping packed object lengths aligned with kernel ABI structures.

Risk points:

- `process_extra_parms()` consumes all remaining arguments after an AQM token; invalid tokens only print a diagnostic and continue, rather than failing in every default case.
- `ipfw_delete_pipe()` overwrites the requested id variable with the `do_cmd()` return and then warns using `rule %u` with `i` reset to `1`, so warnings do not preserve the original object id.
- Delay-profile parsing stores up to `ED_MAX_SAMPLES_NO` points but increments `points_no` without an immediately adjacent explicit bounds check in the data-point branch; the sample count is checked separately.
- Several formatting buffers are fixed-size stack buffers; expected strings are bounded by kernel ABI names and address lengths, but new AQM names/parameters should be checked carefully if extended.

## Testing Notes

Useful coverage would include:

- `dnctl pipe N config` with bandwidth units, byte/slot queue sizes, burst, masks, and delay bounds.
- RED/GRED validation including ECN threshold rules.
- CoDel, PIE, FQ-CoDel, and FQ-PIE parameter parsing with default, numeric, time-unit, and invalid tokens.
- Delay profile files with missing defaults, sorted/unsorted points, duplicate headers, invalid probability, and too few samples.
- Listing responses with IPv4 flows, IPv6 flows, schedulers, profiles, and range filters.

<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/dummynet.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/ipfw2.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/ipfw2.c

## Purpose

`ipfw2.c` is the main implementation of the FreeBSD `ipfw` userland rule engine. It owns global command options, shared utility routines, socket communication with the kernel, token tables, rule display, dynamic-state display, set operations, sysctl toggles, rule deletion/zeroing/flushing, object lookup/packing, and the large rule compiler used by `ipfw add`.

It is the behavioral center of this file group. `main.c` dispatches here; `ipv6.c` and `dummynet.c` provide helper surfaces used from here or routed through `g_co`; `ipfw2.h` exports the shared contract.

## Public Surface

Externally visible functions implemented here include:

- `int is_ipfw(void)`
- buffer helpers: `bp_alloc()`, `bp_free()`, `bp_flush()`, `bprintf()`, `pr_u64()`
- allocation helpers: `safe_calloc()`, `safe_realloc()`
- parser helpers: `_substrcmp()`, `_substrcmp2()`, `stringnum_cmp()`, `match_token()`, `match_token_relaxed()`, `get_token()`, `match_value()`, `concat_tokens()`, `fill_flags()`, `print_flags_buffer()`
- kernel operation wrappers: `do_cmd()`, `do_set3()`, `do_get3()`
- rule/control handlers: `ipfw_add()`, `ipfw_delete()`, `ipfw_flush()`, `ipfw_zero()`, `ipfw_list()`, `ipfw_sets_handler()`, `ipfw_sysctl_handler()`, `ipfw_internal_handler()`
- shared rule helpers: `n2mask()`, `fill_table()`, `ipfw_check_object_name()`

## Global State and Tables

The file defines:

- `struct cmdline_opts g_co`: global command options set by `main.c`.
- `int resvd_set_number = RESVD_SET`: exported reserved set upper bound.
- `static int ipfw_socket = -1`: lazily opened raw IPv4 socket for kernel control calls.
- `struct format_opts`: per-listing display configuration, including counter widths, set masks, requested rule range, dynamic-state count, and table/object name state.

Static token tables encode the command grammar: TCP flags/options, IP options/TOS/offset flags, DSCP names, limit masks, EtherTypes, rule actions, external actions, action parameters, lookup keys, table-value names, and rule options.

## Kernel Operation Model

The file uses a raw socket to issue classic and versioned ipfw operations:

- `do_cmd()` supports legacy `setsockopt()` plus `getsockopt()` when the option name is negative or `IP_FW3`.
- `do_set3()` writes an `ip_fw3_opheader` and calls `setsockopt(IP_FW3)`.
- `do_get3()` writes an `ip_fw3_opheader` and calls `getsockopt(IP_FW3)`.

Global flags affect this layer:

- `g_co.debug_only` dumps binary request headers and payloads to stdout.
- `g_co.test_only` short-circuits kernel calls and returns success.

Most higher-level operations build packed TLV/control buffers, then call `do_get3()` or `do_range_cmd()`.

## Rule Display

Rule display is organized around `show_static_rule()` and `show_state`.

`show_static_rule()`:

1. Skips disabled sets unless `show_sets` is requested.
2. Prints rule number, optional counters, timestamp, and set number.
3. Prints probability, action, action modifiers, protocol, source, destination, and remaining options.
4. Handles compact/comment-only modes.
5. Prints comments stored as `O_NOP`.

The printer uses `show_state.printed[]` to avoid printing the same instruction twice while reconstructing canonical CLI syntax from packed kernel instructions. It has dedicated formatters for IPv4/IPv6 addresses, table lookups, MAC addresses, ports/ranges, DSCP, ICMP types, TCP/IP flags, forwarding addresses, state names, external actions, marks, tags, and dynamic states.

Dynamic states are formatted by `show_dyn_state()` and reached through `foreach_state()`/`list_dyn_range()`. It supports IPv4 and IPv6 flow identifiers, state names, parent/limit/keep-state types, counters, expirations, and verbose TCP state flags.

## Listing Configuration

`ipfw_list()` parses optional rule/range filters, decides whether static rules, dynamic states, and counters are needed, retrieves configuration with `ipfw_get_config()`, and calls `ipfw_show_config()`.

`ipfw_get_config()` retries up to 16 times with larger buffers on `ENOMEM`. Returned configuration can include:

- table/object name TLVs,
- static rule list TLVs,
- dynamic state TLVs.

`ipfw_show_config()` sorts object names, initializes formatting widths, lists all rules or specific requested ranges, and returns `EX_UNAVAILABLE` when requested static rules are missing.

When `g_co.do_pipe` is set, `ipfw_list()` delegates directly to `dummynet_list()`.

## Set, Sysctl, Delete, Zero, and Flush Operations

`ipfw_sets_handler()` supports:

- `set show`
- `set swap X Y`
- `set move X to Y`
- `set move rule X to Y`
- mixed `set enable`/`disable` masks

It uses `do_range_cmd()` and `IP_FW_SET_*`/`IP_FW_XMOVE` operations.

`ipfw_sysctl_handler()` toggles firewall, one-pass, debug, verbose, dynamic keepalive, skipto cache, and optionally ALTQ. Skipto cache is handled through a versioned `IP_FW_SKIPTO_CACHE` request rather than a sysctl.

`ipfw_delete()` deletes rules, sets, NAT configs, or dummynet objects depending on `g_co`. It supports rule ranges and dynamic-only deletion through `g_co.do_dynamic == 2`.

`ipfw_zero()` zeroes counters or log counters for all rules or selected rules.

`ipfw_flush()` prompts unless forced/quiet, delegates to `dummynet_flush()` for pipes, and otherwise deletes all rules or a selected set.

## Object Name Packing

The compiler uses `struct tidx` to collect referenced named kernel objects before submitting a rule:

- tables,
- state names,
- external actions,
- external action instances.

`pack_object()` de-duplicates by name, set, and TLV type, assigns local indices, and grows the object array. `pack_table()` wraps table-name validation. `object_sort_ctlv()`, `object_search_ctlv()`, and `table_search_ctlv()` sort and search kernel/user object TLVs.

`fill_table()` parses `table(NAME)` and `table(NAME,value)` or `table(NAME,key=value)`, sets lookup/table-value flags, and embeds the packed table index in an instruction.

## Rule Compiler

`compile_rule()` parses `ipfw add` syntax and assembles the packed `struct ip_fw_rule` instruction stream. It is the most complex function in the file.

It uses separate temporary buffers:

- `cmdbuf[]` for match instructions.
- `actbuf[]` for actions.
- caller-provided `rbuf` for the final rule.

The compiler handles:

- optional rule number,
- optional `set N`,
- optional `prob D`,
- mandatory action,
- action parameters such as `log`, `altq`, `tag`, and `untag`,
- `proto from src [ports] to dst [ports]`,
- option-only rule forms,
- `not` and OR blocks with braces/parentheses,
- comments.

Supported actions include allow/deny/count, reject/reset/unreach for IPv4 and IPv6, skipto, pipe/queue, divert/tee, netgraph/ngtee, fwd IPv4/IPv6, NAT, reass, setfib, setdscp, call/return, setmark, external actions, and `tcp-setmss`.

Supported match options include IPv4/IPv6 source/destination, table lookups with optional masks, MAC table lookups, MAC address/type matches, ports/ranges/service names, uid/gid/jail, TCP flags/options/sequence/ack/window/MSS/data length, IP length/id/TTL/version/precedence/TOS/options/DSCP, ICMP/ICMPv6 types, IPv6 extension headers and flow IDs, in/out/via/xmit/recv, fib, sockarg, tagged, mark, stateful `keep-state`/`record-state`, `limit`/`set-limit`, reverse-path checks, antispoof, ipsec, and defer-action.

Final instruction ordering is deliberate:

1. Match probability.
2. Generated `O_PROBE_STATE` for stateful rules when needed.
3. Match instructions excluding late-position state/action modifiers.
4. `O_KEEP_STATE` or `O_LIMIT`.
5. `O_SKIP_ACTION`.
6. Action-section offset.
7. `O_LOG`, `O_ALTQ`, `O_TAG`.
8. Actual actions.

`ipfw_add()` wraps the compiled rule in `IPFW_TLV_RULE_LIST`, optionally prepends `IPFW_TLV_TBLNAME_LIST`, aligns rule size to 64-bit boundaries, sends `IP_FW_XADD`, and prints the resulting rule unless quiet.

## Address and Operand Parsing

IPv4 handling is local to this file:

- `fill_ip()` supports `me`, `any`, single addresses, masks by `/bits` or `:mask`, address lists, and `/24`-to-`/31` compact address sets.
- `add_srcip()` and `add_dstip()` map the filled instruction to source/destination opcodes.
- `lookup_host()` resolves IPv4 hostnames.

IPv6 handling is delegated to `ipv6.c` through `add_srcip6()`, `add_dstip6()`, `fill_icmp6types()`, `fill_flow6()`, and `fill_ext6hdr()`.

Port parsing uses `strtoport()` with service-name lookup, EtherType-name lookup for MAC type, range support, and comma-separated lists.

## Internal Commands and Monitoring

`ipfw_internal_handler()` dispatches hidden/internal commands:

- `iflist`: tracked interface list via `IP_FW_XIFLIST`.
- `talist`: table algo list from `tables.c`.
- `olist`: service object list via `IP_FW_DUMP_SRVOBJECTS`.
- `vlist`: table value list from `tables.c`.
- `monitor`: route-socket firewall log monitor.

`ipfw_rtsock_monitor()` opens `socket(PF_ROUTE, SOCK_RAW, AF_IPFWLOG)` and continuously decodes `RTM_IPFWLOG` messages with Ethernet addresses, source/destination socket addresses, set/rule/tablearg/opcode/mark metadata, optional next-hop, and optional comment filtering.

## Error Handling and Risks

The code uses `err()`/`errx()` heavily and generally exits on malformed input. It performs many command-buffer length checks through `CHECK_LENGTH`, `CHECK_CMDLEN`, `CHECK_ACTLEN`, and `CHECK_RBUFLEN`.

Important risk areas:

- `compile_rule()` mutates argument strings in place using `strsep()`, inserted NULs, and pointer increments; callers must pass mutable argument storage.
- `compile_rule()` uses fixed temporary instruction arrays of 255 `uint32_t`; length checks reduce risk but every new opcode path must update length before writing payload fields.
- `do_set3()` debug initializer contains `.total_len = optlen, sizeof(struct debug_header),` which uses the comma operator in an initializer-like expression and appears intended to include the debug header size. This should be reviewed if debug binary output matters.
- `concat_tokens()` increments `bufsize` instead of decreasing remaining capacity after `snprintf()`; this utility appears suspicious and should be tested before reuse for bounded output.
- `eaction_check_name()` rejects a name only when it is present in both `rule_actions` and `rule_action_params`; the comment says it restricts special names, but the condition may not match the intended union-style restriction.
- Some action paths increment `av` after accepting keywords where a missing argument would already have failed, but changes to optional argument syntax can easily desynchronize parsing.
- Object TLV search assumes sorted kernel-provided object lists with fixed object size; callers must sort user-built lists before kernel submission.

## Testing Notes

High-value tests would cover:

- `ipfw add` dry-run/debug output for representative actions and every address family.
- Canonical print round-trips for rules with tables, named states, comments, OR blocks, `not`, and external actions.
- Dynamic state list decoding.
- Buffer-boundary tests for long comments, large port lists, many table references, and long rule option chains.
- `set`, `delete`, `zero`, and `flush` range/set behavior.
- `lookup key:mask table` variations for supported and unsupported key types.

<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/ipfw2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/ipfw2.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/ipfw2.h

## Purpose

`ipfw2.h` is the shared declaration and token header for the `ipfw`/`dnctl` userland sources. It defines global command-line state, parser token ids, common macros, the dynamic print buffer type, utility prototypes, kernel operation wrappers, and cross-file command handler declarations.

It intentionally forward-declares many kernel ABI structs instead of including every heavy network header in each source file.

## Key Definitions

`enum cmdline_prog` distinguishes whether the binary is acting as:

- `cmdline_prog_ipfw`
- `cmdline_prog_dnctl`

`struct cmdline_opts` is global CLI state. Major flags include:

- display modes: counters, compact, comments-only, timestamps, set display, sorting, resolving names,
- behavior modes: quiet, force, test-only, debug-only,
- command target modes: pipe/queue/scheduler, NAT, dynamic state handling, selected set,
- `prog` to distinguish `ipfw` from `dnctl`.

The comment notes that when reading commands from a file, option context is not restored after each line. That is an important behavior inherited by `main.c`.

`struct _s_x` is the string-to-token table type used across parsers. `f_ipdscp[]` is exported for DSCP name lookup.

## Token Namespace

`enum tokens` is a large shared token namespace for:

- parser punctuation: `TOK_OR`, `TOK_NOT`, braces,
- rule actions: accept/count/pipe/queue/divert/forward/deny/reject/reset/check-state/NAT/reass/call/return/external actions,
- action parameters: log, ALTQ, tag/untag,
- rule options: UID/GID/jail, in/out/via/xmit/recv, layer2, diverted variants, IP/TCP/ICMP fields, MAC fields, stateful options, comments,
- dummynet options: PLR, buckets, bandwidth, delay, queue, scheduler, RED/GRED/AQM, masks, profile, burst, weights/priorities,
- NAT and table options,
- IPv6 options and NAT64/NPTv6 options,
- newer mark/setmark and defer-action options.

Because the token enum is shared by multiple files, adding grammar in one source can require coordinated updates to this header and token tables in `ipfw2.c` or `dummynet.c`.

## Shared APIs

The header declares:

- buffer printing: `struct buf_pr`, `bp_alloc()`, `bp_free()`, `bp_flush()`, `bprintf()`, `pr_u64()`
- allocation wrappers: `safe_calloc()`, `safe_realloc()`
- token/string helpers: `_substrcmp()`, `_substrcmp2()`, `stringnum_cmp()`, `match_token()`, `match_token_relaxed()`, `get_token()`, `match_value()`, `concat_tokens()`
- flag helpers: `fill_flags()`, `print_flags_buffer()`
- kernel command wrappers: `do_cmd()`, `do_set3()`, `do_get3()`
- mask helpers: `n2mask()`, `contigmask()`

It also declares first-level handlers implemented across the `sbin/ipfw` directory: add/list/delete/flush/zero, dummynet, NAT, tables, sysctl toggles, internal commands, NAT64/NPTv6, and validation helpers.

## Cross-File Boundaries

The header makes the following boundaries explicit:

- `dummynet.c` exports dummynet list/config/delete/flush routines.
- `ipv6.c` exports IPv6 print and fill helpers.
- `ipfw2.c` exports table filling and general rule/config functions.
- `tables.c`, NAT, NAT64, NPTv6, and optional ALTQ modules provide other handlers not in this group.

The `PF` conditional controls ALTQ availability. Without `PF`, `NO_ALTQ` is defined and ALTQ-specific calls are compiled out in `ipfw2.c`.

## Error/Compatibility Macros

`NEED()` and `NEED1()` are parser convenience macros that terminate with `EX_USAGE` when required arguments are missing.

The header preserves historical parser compatibility through `_substrcmp()` and `_substrcmp2()` prototypes, which intentionally allow abbreviations but warn about deprecated substring matching.

## Risks and Extension Notes

The shared `enum tokens` can become fragile because many token values are used in independent static token tables. New tokens should be added carefully and tested in both parse and print paths.

`struct cmdline_opts` is process-global mutable state. File-based command execution reuses it line to line, and the header explicitly documents that context is not restored. New options should account for this persistence.

Forward declarations reduce include coupling but mean ABI mismatches are caught only when implementation files include the real kernel headers.

<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/ipfw2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/ipv6.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/ipv6.c

## Purpose

`ipv6.c` implements IPv6-specific parsing and formatting helpers for the `ipfw` rule compiler and printer. It handles IPv6 unreachable codes, IPv6 address operands, ICMPv6 type bitsets, IPv6 flow-id lists, and IPv6 extension-header masks.

The file is deliberately narrower than `ipfw2.c`: it exports helpers consumed by the main rule compiler/printer while keeping IPv6 address-specific logic out of the large core file.

## Public Surface

Exported functions:

- `uint16_t get_unreach6_code(const char *str)`
- `void print_unreach6_code(struct buf_pr *bp, uint16_t code)`
- `void print_ip6(struct buf_pr *bp, const ipfw_insn_ip6 *cmd)`
- `void fill_icmp6types(ipfw_insn_icmp6 *cmd, char *av, int cblen)`
- `void print_icmp6types(struct buf_pr *bp, const ipfw_insn_u32 *cmd)`
- `void print_flow6id(struct buf_pr *bp, const ipfw_insn_u32 *cmd)`
- `int fill_ext6hdr(ipfw_insn *cmd, char *av)`
- `void print_ext6hdr(struct buf_pr *bp, const ipfw_insn *cmd)`
- `ipfw_insn *add_srcip6(ipfw_insn *cmd, char *av, int cblen, struct tidx *tstate)`
- `ipfw_insn *add_dstip6(ipfw_insn *cmd, char *av, int cblen, struct tidx *tstate)`
- `void fill_flow6(ipfw_insn_u32 *cmd, char *av, int cblen)`

## Address Parsing

`fill_ip6()` is the central internal parser. It accepts:

- `any`, producing an empty/no-op instruction,
- `me` and `me6`,
- `table(...)`, delegated to `fill_table()` with `O_IP_DST_LOOKUP` before source/destination opcode adjustment,
- single IPv6 addresses,
- address plus prefix length,
- address plus explicit IPv6 mask,
- comma-separated address/mask lists.

It resolves numeric IPv6 addresses with `inet_pton()` and hostnames with `gethostbyname2(AF_INET6)`. It applies masks with `APPLY_MASK()`, stores single-address cases compactly, and stores lists as address/mask pairs.

`add_srcip6()` and `add_dstip6()` call `fill_ip6()` and then choose the final opcode:

- source/destination `me6`,
- single source/destination IPv6,
- source/destination IPv6 mask list,
- table lookup variants.

## Formatting

`print_ip6()` reconstructs CLI syntax from packed IPv6 instructions. It handles:

- `me6`,
- generic `ip6`,
- single addresses,
- address/mask pairs,
- `any`,
- optional reverse lookup via `g_co.do_resolv`,
- non-contiguous masks by printing explicit mask addresses.

`print_unreach6_code()`, `print_icmp6types()`, `print_flow6id()`, and `print_ext6hdr()` provide specialized printing for action and option operands.

## ICMPv6, Flow ID, and Extension Headers

`icmp6codes[]` maps textual unreachable names such as `no-route`, `admin-prohib`, `address`, and `port` to ICMPv6 destination-unreachable codes.

`fill_icmp6types()` parses comma-separated numeric type values into a bitmap instruction. It validates separators and rejects values above `ICMP6_MAXTYPE`.

`fill_flow6()` parses comma-separated 20-bit flow labels into a variable-length `ipfw_insn_u32` instruction and stores the count in `o.arg1`.

`ext6hdrcodes[]` maps extension-header tokens:

- `frag`
- `hopopt`
- `route`
- `dstopt`
- `ah`
- `esp`
- `rthdr0`
- `rthdr2`

`fill_ext6hdr()` ORs these into `cmd->arg1`, sets `O_EXT_HDR`, and returns whether any valid bit was set.

## Dependencies

This file depends on shared helpers from `ipfw2.c`:

- `match_token()` / `match_value()`
- `bprintf()`
- `contigmask()`
- `n2mask()`
- `fill_table()`
- global `g_co`

It also depends on kernel instruction layout macros and opcodes from `<netinet/ip_fw.h>`.

## Error Handling and Risks

Most malformed operands terminate with `errx(EX_DATAERR, ...)`.

Risk points:

- Like the IPv4 parser, `fill_ip6()` mutates the argument string by inserting NUL terminators around commas and slashes. Callers must provide mutable storage.
- `fill_ip6()` uses `strdup()` but exits via `errx()` on many parse failures before freeing; this is acceptable for a short-lived CLI process but relevant for reuse.
- `fill_flow6()` calls `strtoul(av, &av, 0)` after `strsep()` and then checks `*av != ','`; because `strsep()` already split at commas, only the end-of-token check matters in practice.
- The comment in `fill_icmp6types()` questions whether the upper bound should allow all 8-bit values rather than `ICMP6_MAXTYPE`.

## Testing Notes

Useful tests:

- Source and destination IPv6 `any`, `me6`, single address, prefix, explicit mask, and comma-list operands.
- Table-backed IPv6 operands.
- Non-contiguous mask printing.
- ICMPv6 unreachable code names and numeric values.
- ICMPv6 type lists at boundary values.
- Extension-header parse/print round trips.
- Flow labels at `0`, valid maximum `0xfffff`, and out-of-range values.

<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/ipv6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/main.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/main.c

## Purpose

`main.c` is the command-line entry point for the `ipfw` and `dnctl` binaries. It provides top-level usage text, normalizes command-line arguments, sets global options in `g_co`, dispatches commands to the handler functions declared in `ipfw2.h`, and supports reading command files with optional preprocessing.

The file distinguishes behavior by executable basename: `dnctl` restricts the command set to dummynet operations, while any other basename acts as `ipfw`.

## Main Flow

`main()`:

1. Performs Windows/TCC Winsock setup when compiled in that environment.
2. Sets `g_co.prog` based on `basename(av[0])`.
3. If the last argument is an absolute readable pathname, treats it as a command file and calls `ipfw_readfile()`.
4. Otherwise calls `ipfw_main()`.
5. On parser failure, exits with usage guidance.

`help()` prints separate syntax summaries for `ipfw` and `dnctl`, then exits.

## Argument Normalization

`ipfw_main()` receives an argument vector including program name. It supports two input shapes:

- Normal `argc/argv` from the shell.
- A single command string, used by file-reading mode.

For a single command string, it:

- strips comments beginning with `#`,
- collapses whitespace,
- joins tokens after commas by removing spaces after comma-separated syntax,
- allocates one block containing both pointer array and copied argument strings.

For normal shell arguments, it joins adjacent arguments when an argument ends in `,`, preserving legacy comma-list syntax.

The resulting `av` array is mutable and NUL-terminated, which is required by downstream parsers that mutate argument strings.

## Option Parsing

For `ipfw`, `ipfw_main()` handles options:

- `-a`: show accounting counters,
- `-b`: comment-only compact mode,
- `-c`: compact mode,
- `-d`: display dynamic rules,
- `-D`: dynamic-only display/delete,
- `-f`: force,
- `-h`: help,
- `-i`: show table values as IP,
- `-n`: test-only,
- `-N`: resolve names,
- `-p`: rejected here because command-file preprocessing requires an absolute pathname mode,
- `-q`: quiet,
- `-s`: sort field,
- `-S`: show sets,
- `-t`/`-T`: timestamp display,
- `-v`: verbose,
- `-x`: binary debug output.

For `dnctl`, it handles `-h`, `-n`, `-s`, and `-v`.

If not already forced, non-interactive stdin sets `g_co.do_force`.

## Command Dispatch

`ipfw_main()` supports historical syntax where a rule number precedes `add`, swapping the first two arguments to normalize.

It detects command domains:

- `nat`
- `pipe`
- `queue` / `flowset`
- `sched`
- `set N`

For `pipe`/`queue`/`sched`/`nat`, it also normalizes `pipe N config` into `pipe config N` for easier parsing.

Primary dispatch includes:

- `ipfw_add()`
- `ipfw_show_nat()`
- `ipfw_config_pipe()`
- `ipfw_config_nat()`
- `ipfw_sets_handler()`
- `ipfw_table_handler()`
- `ipfw_sysctl_handler()` for `enable`/`disable`
- `ipfw_delete()`
- NAT64 and NPTv6 handlers
- `ipfw_flush()`
- `ipfw_zero()`
- `ipfw_list()`
- `ipfw_internal_handler()`

For `dnctl`, commands outside the dummynet domain fall back to help.

## Command File Mode

`ipfw_readfile()` is used when the last CLI argument is an absolute readable path. It supports options that can apply globally before the file name:

- for `ipfw`: `-c`, `-f`, `-N`, `-n`, `-p`, `-q`, `-S`
- for `dnctl`: `-n`, `-q`

With `-p`, it runs a preprocessor command with the file as stdin and reads commands from the preprocessor stdout. It uses `pipe()`, `fork()`, `dup2()`, `execvp()`, `fdopen()`, and `waitpid()`.

Each input line is passed to `ipfw_main(2, args)` as a single mutable string. `setprogname()` is changed to `Line N` while processing, improving diagnostics for file lines.

## Dependencies

`main.c` is the only file in this group with the actual C `main()`. It depends on handler and global declarations from `ipfw2.h`, especially:

- `g_co`
- `is_ipfw()`
- command handler prototypes
- `resvd_set_number`
- `_substrcmp()`

## Error Handling and Risks

The file generally exits with `errx()`/`err()` on invalid usage, unreadable files, fork/pipe/exec errors, and preprocessor failure.

Important behavioral caveats:

- `g_co` is global and not reset between command-file lines. The header explicitly documents this; options in one line can affect later lines.
- The single-string parser mutates the original input line; this is required for downstream parsing but means the string must not be immutable storage.
- File mode is triggered only by an absolute pathname in the last argument. Relative command files are not treated as file mode by `main()`.
- `-p` in normal command mode is rejected; preprocessing is only meaningful through `ipfw_readfile()`.
- Preprocessor argument handling rewrites `av[ac-1] = NULL` and passes the remaining arguments to `execvp()`, so command-file `-p` syntax depends on exact argument positioning.

## Testing Notes

Useful tests:

- Basename-driven `ipfw` versus `dnctl` dispatch.
- One-string parsing with comments, whitespace, and comma-separated operands.
- Shell-argv comma joining.
- Legacy `100 add ...` normalization.
- `pipe N config` and `pipe config N` equivalence.
- Command-file mode with and without preprocessor, including preprocessor nonzero exit and signal termination.
- Persistence of global options across file lines.

<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipfw/main.c -->