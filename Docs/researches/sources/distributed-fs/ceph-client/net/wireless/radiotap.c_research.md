# sources/distributed-fs/ceph-client/net/wireless/radiotap.c

## Purpose

`radiotap.c` implements the exported radiotap iterator used to parse variable-length IEEE 802.11 radiotap headers. It validates header length/version, walks normal and extended present bitmaps, handles per-field alignment relative to the radiotap header, supports vendor namespaces, and returns one present argument at a time to callers.

## Important APIs, Types, and Functions

- `rtap_namespace_sizes[]` defines alignment and size for known standard radiotap fields such as TSFT, FLAGS, RATE, CHANNEL, MCS, AMPDU status, and VHT.
- `radiotap_ns` describes the standard namespace.
- `ieee80211_radiotap_iterator_init()` initializes `struct ieee80211_radiotap_iterator` and validates header bounds.
- `ieee80211_radiotap_iterator_next()` advances to the next present argument and returns `0`, `-ENOENT`, or `-EINVAL`.
- `find_ns()` selects a registered vendor namespace by OUI and subnamespace.

## Control Flow

Initialization rejects packets shorter than a radiotap header, non-zero radiotap versions, and `it_len` values larger than the available packet length. It seeds bitmap and argument pointers from `it_present` and skips any extended present words, with bounds checks before each dereference. The iterator starts in the standard namespace.

`iterator_next()` loops over bits in the current present bitmap. For absent bits it advances. For present bits it obtains the field alignment and size, applies padding relative to the radiotap header start, checks that the field fits in `it_len`, records `this_arg_index`, `this_arg`, and `this_arg_size`, then advances internal state. Standard namespace, vendor namespace, and extension bits receive special handling: vendor namespaces parse OUI/subns/length and either switch to a known vendor namespace or return raw vendor data; radiotap namespace switches back to standard fields; extension bits load the next bitmap word.

## State and Persistence Behavior

All state is held in the caller-provided iterator. It tracks the radiotap header pointer, maximum radiotap length, current argument pointer, current bitmap shifter, next bitmap pointer, namespace metadata, reset-on-extension behavior, and the last returned argument. The file has only static constant namespace tables and no persistent runtime allocations.

## Dependencies and Integration Points

The implementation depends on cfg80211/public radiotap iterator types, `net/ieee80211_radiotap.h`, `linux/unaligned.h`, and exported symbols used by wireless drivers, monitor injection paths, sniffers, and tests that need robust radiotap parsing.

## Risks and Edge Cases

Radiotap fields are little-endian and may be unaligned; callers must use unaligned access helpers. Bounds checks are security-sensitive because radiotap headers can originate from packets or userspace injection. Unknown standard fields terminate standard parsing with `-ENOENT`; unknown vendor namespaces are returned as raw vendor data and skipped as a block. Namespace reset across extended bitmaps is subtle and easy to break.

## Test Signals

Parser tests should include minimal headers, invalid version, truncated `it_len`, extended bitmaps, every known field alignment, unknown standard bits, known and unknown vendor namespaces, and malformed vendor lengths. KASAN/UBSAN and packet-injection tests can catch out-of-bounds or unaligned misuse.
