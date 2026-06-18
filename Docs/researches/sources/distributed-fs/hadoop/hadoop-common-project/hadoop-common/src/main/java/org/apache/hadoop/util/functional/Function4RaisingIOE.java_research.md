# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/Function4RaisingIOE.java

`Function4RaisingIOE<I1, I2, I3, I4, R>` is a four-argument functional interface whose `apply()` method can throw `IOException`. It fills a gap left by `java.util.function`, which has neither checked exceptions nor a standard arity-four function.

There is no default unchecked adapter, state, persistence, synchronization, or control flow beyond the single abstract method. The dependency surface is only `java.io.IOException`. Its intended role is API shape support: Hadoop code can accept a lambda involving several IO-related inputs without broadening the signature to `Exception` or inventing local functional interfaces.

Integration is package-level rather than strongly coupled in this source subset. It belongs to the same family as `FunctionRaisingIOE` and `BiFunctionRaisingIOE`, allowing utility code to remain explicit about IO failures. Risks are mostly API ergonomics: without an unchecked helper, callers crossing into Java stream/future APIs need their own wrapper; with four generic inputs, lambda target typing can be harder to read and overloads should be avoided. Test signals are indirect through compile-time usage and package tests for neighboring checked-IO functional adapters.
