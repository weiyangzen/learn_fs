# sources/distributed-fs/ceph-client/net/core/net_test.c

## Purpose

`net_test.c` is a KUnit suite for selected networking core helpers. It currently tests GSO segmentation behavior for different SKB layouts and compatibility conversion for IP tunnel flag bitmaps.

## Important APIs, Types, And Functions

The GSO section defines `struct gso_test_case`, a table of cases, `__init_skb()`, parameter generation with `KUNIT_ARRAY_PARAM()`, and `gso_test_func()`. It exercises `build_skb()`, SKB frags, `frag_list`, `skb_segment()`, `GSO_BY_FRAGS`, and expected segment sizing/header placement.

The tunnel section defines `struct ip_tunnel_flags_test`, flag bit arrays, `IP_TUNNEL_FLAGS_TEST`, and `ip_tunnel_flags_test_run()`. It exercises `ip_tunnel_flags_is_be16_compat()`, `ip_tunnel_flags_to_be16()`, and `ip_tunnel_flags_from_be16()`. The suite is registered as `net_core`.

## Control Flow

Each GSO test allocates an SKB backed by a page, writes a dummy MAC header, configures GSO size and protocol, optionally adds page frags or frag-list SKBs, sets feature flags, runs `skb_segment()`, then validates segment count, segment lengths including header size, MAC/network header positions, copied header bytes, and `segs->prev` last-segment linkage before consuming all SKBs.

Each tunnel flag test constructs source and expected bitmaps, checks whether source flags are compatible with legacy `__be16` representation, compares the converted big-endian value, converts back, and validates the expected bitmap.

## State And Persistence Behavior

This file has no persistent state. It allocates temporary pages and SKBs per test and consumes them before returning. Test cases are static const-like data in the module.

## Dependencies And Integration Points

It depends on KUnit, SKB/GSO internals, page allocation, network feature flags, and IP tunnel flag helpers. It provides regression coverage for behavior used by transport offload and tunnel implementations.

## Risks

The GSO tests manipulate low-level SKB internals, so incorrect setup can test an artificial invalid state rather than real stack behavior. Some cases depend on feature flags such as `NETIF_F_SG`, `NETIF_F_HW_CSUM`, and `NETIF_F_GSO_PARTIAL`. The tunnel flag tests depend on endian-specific legacy conflicts and must remain correct on both little-endian and big-endian builds.

## Test Signals

The main signal is KUnit execution of suite `net_core` across architectures/endian variants and configs with relevant SKB/GSO support. Failures indicate regressions in segmentation sizing, header propagation, frag-list handling, `GSO_BY_FRAGS`, or tunnel flag compatibility.
