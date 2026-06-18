# sources/distributed-fs/ceph-client/fs/unicode/utf8-norm.c

`utf8-norm.c` implements the runtime trie decoder and normalization cursor used by Unicode-aware filesystems. It validates UTF-8, filters by selected Unicode version, expands decompositions, performs algorithmic Hangul decomposition, and emits bytes in canonical combining class order.

Public functions are `utf8version_is_supported()`, `utf8nlen()`, `utf8ncursor()`, and `utf8byte()`. Internal helpers include `utf8clen()`, `utf8decode3()`, `utf8encode3()`, `utf8hangul()`, `utf8nlookup()`, and `utf8lookup()`. The packed trie is interpreted with `BITNUM`, `NEXTBYTE`, `OFFLEN`, `RIGHTPATH`, `TRIENODE`, `RIGHTNODE`, and `LEFTNODE`; leaves use generation, CCC, and optional decomposition strings.

`utf8nlookup()` walks the generated trie from the selected table offset and returns a leaf only for valid UTF-8 Unicode sequences. Hangul leaves are expanded into cursor-local scratch. `utf8nlen()` sums original byte length, decomposition length, or zero for empty ignorable decompositions. `utf8ncursor()` initializes bounded cursor state and rejects initial continuation bytes. `utf8byte()` handles decomposition pointer switching and rescans between stopper characters to emit nonzero CCCs in ascending order.

Dependencies are `utf8n.h`, generated data, module exports, and `utf8-core.c`. Risks include malformed/truncated UTF-8, length accounting, combining-class rescan complexity, Hangul correctness, and newer-than-selected characters. Signals are KUnit, generator self-tests, invalid input tests, and filesystem name-equivalence tests.
