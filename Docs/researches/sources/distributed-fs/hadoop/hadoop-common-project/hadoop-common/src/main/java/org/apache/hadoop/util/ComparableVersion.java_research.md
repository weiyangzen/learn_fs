# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ComparableVersion.java

Purpose: `ComparableVersion` is Hadoop's copy of Maven's generic version comparator, supporting numeric parts, string qualifiers, dot/dash separators, and canonical equality.

Important APIs and types: public constructor, `parseVersion`, `compareTo`, `toString`, `equals`, and `hashCode`. Internal `Item` implementations are `IntegerItem`, `StringItem`, and recursive `ListItem`.

Control flow: parsing lowercases the version, splits on dots, dashes, and digit/letter transitions, creates integer or string items, creates nested list items for numeric dash segments, normalizes trailing null items, and stores a canonical list string. Comparison delegates recursively: integers compare numerically with `BigInteger`, known qualifiers order as alpha, beta, milestone, rc, snapshot, release, sp, and unknown qualifiers sort after known ones lexically.

State and persistence behavior: stores original value, canonical string, and parsed item tree. No persistence.

Dependencies and integration points: used wherever Hadoop needs Maven-like version ordering. Depends on Hadoop `StringUtils.toLowerCase` and Java `BigInteger`.

Risks: behavior is compatibility-sensitive with Maven semantics. Empty or malformed numeric segments may throw through `BigInteger`. Equality is canonical, so different strings like `1.0` and `1` can be equal.

Test signals: cover numeric ordering, qualifier aliases (`ga`, `final`, `cr`), short qualifiers (`a1`, `b1`, `m1`), dash versus dot precedence, unknown qualifiers, canonical equality/hash, huge numeric segments, and case-insensitivity.
