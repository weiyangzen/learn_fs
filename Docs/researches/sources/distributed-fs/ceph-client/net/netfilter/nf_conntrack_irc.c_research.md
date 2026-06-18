# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_irc.c

## Purpose
This module implements the IRC DCC conntrack helper. It inspects client-to-server IRC TCP payloads for `PRIVMSG ... :\001DCC ...` commands, validates the advertised IPv4 address and port, and creates TCP expectations so DCC data/chat connections can be classified as related to the IRC control connection. It also exposes `nf_nat_irc_hook` for the NAT companion to rewrite embedded DCC address text.

## Important APIs, Types, And Functions
Module parameters are `ports[]`, `max_dcc_channels`, and `dcc_timeout`. The registered helper array is `irc[MAX_PORTS]`, initialized by `nf_ct_helper_init()` for each configured server port. `irc_exp_policy` carries the per-master maximum and timeout. `parse_dcc()` extracts the numeric IPv4 address and port from a DCC command and returns pointers to the embedded address text. `help()` is the packet inspection callback.

## Control Flow
The helper ignores reply-direction packets, non-established connections, packets without a full TCP header, and packets with no payload. It copies at most `MAX_SEARCH_SIZE` bytes into a global `irc_buffer` under `irc_buffer_lock`, skips leading whitespace, optionally verifies `PRIVMSG `, then scans for the CTCP marker `" :\001DCC "`. It matches known DCC verbs (`SEND`, `CHAT`, `MOVE`, `TSEND`, `SCHAT`), parses address and port, and validates that the advertised address is either the original source address or the NAT-visible reply destination address. Forged or zero-port DCC commands are rate-limited warnings and ignored.

For valid DCC commands, it allocates an expectation on the reply-side destination address and advertised TCP port. If NAT is active and `nf_nat_irc_hook` is registered, NAT handles payload rewrite and expectation setup; otherwise `nf_ct_expect_related()` installs the expectation directly. Allocation or expectation insertion failures drop the packet with helper logging.

## State And Persistence
State is in memory: module parameters, the helper array, expectation policy, exported NAT hook pointer, and `irc_buffer`. Per-flow persistence is in conntrack expectations until timeout or use. The helper does not keep protocol state across packets, so DCC commands split across TCP segments can be missed.

## Dependencies And Integration Points
The module depends on IPv4 TCP conntrack helpers, expectations, helper registration, and optional NAT IRC support through `nf_nat_irc_hook`. It registers aliases for legacy `ip_conntrack_irc` and helper autoload name `irc`.

## Risks
The scanner is intentionally simple and bounded, but it can miss DCC commands beyond the first 4095 payload bytes or across segment boundaries. It is IPv4-specific because DCC address parsing uses decimal IPv4. The global buffer serializes parsing with a spinlock. The address validation is critical; without it, arbitrary DCC expectations could be injected.

## Test Signals
Tests should cover default port registration, multiple configured ports, invalid `max_dcc_channels`, normal DCC SEND/CHAT parsing, leading whitespace, forged address rejection, zero-port rejection, NAT hook invocation offsets, expectation timeout/max limits, no inspection on server-to-client packets, and segmented or oversized payload behavior.
