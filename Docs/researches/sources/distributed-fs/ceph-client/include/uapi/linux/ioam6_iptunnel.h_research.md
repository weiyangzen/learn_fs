
# sources/distributed-fs/ceph-client/include/uapi/linux/ioam6_iptunnel.h

## Purpose

`ioam6_iptunnel.h` defines lightweight tunnel attributes for IPv6 IOAM insertion, including insertion mode, destination/source addresses, trace header, and insertion frequency. The complete 64-line file was read.

## Important APIs, Types, and Functions

Enums define tunnel modes `IOAM6_IPTUNNEL_MODE_INLINE`, `ENCAP`, and `AUTO`, min/max mode helpers, attributes `IOAM6_IPTUNNEL_MODE`, `DST`, `TRACE`, `FREQ_K`, `FREQ_N`, and `SRC`, plus frequency bounds `IOAM6_IPTUNNEL_FREQ_MIN` and `IOAM6_IPTUNNEL_FREQ_MAX`.

## Control Flow

User space configures an lwtunnel route with IOAM attributes. Kernel routing/tunnel code inserts IOAM inline, encapsulates in ip6ip6, or chooses auto behavior for local versus transit packets, applying k/n packet frequency sampling.

## State and Persistence Behavior

IOAM tunnel mode, destination/source, trace header template, and insertion frequency are route/lwtunnel state and persist with the route.

## Dependencies and Integration Points

The header references `struct in6_addr` and `struct ioam6_trace_hdr` by contract and integrates with IPv6 lightweight tunnels, IOAM trace formatting, and rtnetlink route configuration.

## Risks and Edge Cases

Frequency must satisfy `0 < k <= n` within the documented range. Mode-specific address requirements differ; encap/auto need destination and optional source handling. Trace-header size and validation must match `ioam6.h`.

## Test Signals

Route/lwtunnel tests should configure inline/encap/auto modes, validate k/n boundaries, require destination where needed, check trace insertion on sampled packets, and reject malformed trace headers.
