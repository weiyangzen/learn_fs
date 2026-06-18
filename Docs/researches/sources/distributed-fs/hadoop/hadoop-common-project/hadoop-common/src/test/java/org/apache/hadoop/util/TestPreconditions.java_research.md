# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestPreconditions.java

Purpose: exhaustive message-formatting tests for Hadoop `Preconditions` null, argument, and state checks.

Important APIs and types: `checkNotNull`, `checkArgument`, `checkState`, default-message getters, string messages, format-string overloads, and `Supplier<String>` message overloads.

Control flow: success tests call each precondition with valid input while providing null suppliers, null messages, null format strings, null args, bad format specifiers, insufficient args, and supplier formatting failures to prove success paths do not eagerly evaluate or throw. Failure tests intercept `NullPointerException`, `IllegalArgumentException`, and `IllegalStateException`, checking explicit messages when formatting succeeds and default messages when formatting fails or suppliers are null/bad.

State and persistence: only a reusable `errorMessage` field; no external state.

Dependencies and integration points: protects a shared utility used widely across Hadoop from Guava-version drift and message-evaluation side effects.

Risks: eager supplier evaluation, leaking `IllegalFormatException`, null formatter crashes, wrong default message, or exception-type mismatch. Test signals are `LambdaTestUtils.intercept` assertions on type and message.
