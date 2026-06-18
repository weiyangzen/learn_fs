
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/RandomDistribution.java

Purpose: Test helper library for discrete random distributions used by TFile key/value workload generators.

Important APIs and types: Defines `DiscreteRNG` plus implementations `Flat`, `Zipf`, and `Binomial`. `Flat` samples uniformly from `[min,max)`. `Zipf` builds compressed cumulative probability tables. `Binomial` builds a cumulative binomial distribution.

Control flow: Constructors validate ranges and precompute distribution tables. `nextInt()` methods draw a random double or integer and map it through direct arithmetic or binary search over cumulative probabilities.

State and persistence: Each distribution stores a `Random` and immutable parameters/tables. No durable state.

Dependencies and integration points: Consumed by `KVGenerator`, `KeySampler`, and TFile seek/comparison tests to vary key, value, and dictionary word lengths.

Risks: Zipf table approximation depends on epsilon and may be imprecise for large ranges. Binomial probability math can suffer floating-point limits. Invalid argument handling is constructor-only.

Test signals: Provides repeatable workload shaping when seeded; not directly asserted here.
