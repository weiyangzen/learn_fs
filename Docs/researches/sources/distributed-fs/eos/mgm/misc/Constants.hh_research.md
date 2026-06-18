# sources/distributed-fs/eos/mgm/misc/Constants.hh

Purpose: centralizes string constants for MGM extended attributes and policy keys so callers avoid repeated allocations and typo-prone string literals.

Important APIs and constants: atomic/injection attributes include `EOS_ATOMIC` and `EOS_INJECTION`. System namespace attributes include hard-link metadata, owner authorization, versioning, alternative checksums, forced atomicity, ENOENT redirect, forced size/stall/space/group/layout/checksum/blocksize/blockchecksum/stripe settings. User attributes mirror versioning and forced layout/checksum/blocksize/blockchecksum/stripe controls plus `user.stall.unavailable` and `user.tag`. Policy keys include bandwidth, IO priority, IO type, and schedule.

Control flow and state behavior: this header has no functions. Consumers perform map lookups or assignments against `static const std::string` objects. The comment explains the current choice: `std::string` helps existing `map.find` call sites avoid temporary construction until transparent lookup or string-view migration is available.

Dependencies and integration points: depends only on `<string>`. Integration points include MGM policy resolution in `mgm/policy/Policy.cc`, attribute helpers in `mgm/utils/AttrHelper.cc`, LRU conversion space selection, and unit tests in `unit_tests/mgm/utils/AttrHelperTests.cc`.

Risks and test signals: `static const std::string` in a header creates one internal-linkage object per translation unit, which is acceptable for read-only constants but can complicate address identity assumptions. Tests should focus on consumer behavior: forced atomic precedence, system versus user forced policy resolution, and exact key spelling for externally visible xattrs.
