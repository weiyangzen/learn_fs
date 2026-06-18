# File Research: sources/cow-pools/bcachefs-tools/fs/sb/members.h

Header for member access, iteration, refcounting, lookup, and property helpers. It provides v1/v2 member readers that copy variable-sized on-disk entries into padded `struct bch_member` values, plus mutable v2 accessors.

Defines RCU and refcounted device iteration macros, online/rw/readable member loops using enumerated IO refs, percpu-ref device lifetime helpers, outer memory-lifetime refs, and device lookup variants that either tolerate missing devices or report fs inconsistency. It also exposes bucket validity checks and bkey/bucket-specific tryget helpers.

Member utilities include alive/existing predicates, endian conversion to `bch_member_cpu`, btree bitmap inline checks, GC/marking prototypes, member allocation/cleanup, device metadata upgrade entry points, and member-name printing.
