
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/KeySampler.java

Purpose: Generates random seek keys whose first four bytes fall between a TFile reader's first and last keys.

Important APIs and types: Constructor accepts `Random`, first and last `RawComparable` keys, and a key-length `DiscreteRNG`. Public `next(BytesWritable key)` fills a sampled key.

Control flow: The constructor converts first and last key prefixes to integers. `next()` chooses a length of at least four bytes, fills random bytes, then overwrites the first four bytes with a random integer in `[min, max)`, encoded big-endian.

State and persistence: Holds prefix bounds, random source, and length generator. No durable state.

Dependencies and integration points: Used by `TestTFileSeek` to drive `Scanner.lowerBound()` with keys likely to hit the TFile key range.

Risks: `random.nextInt(max - min)` fails if first and last prefixes are equal. It only constrains the prefix, so sampled suffixes may miss exact keys.

Test signals: Provides randomized seek workload with bounded key distribution.
