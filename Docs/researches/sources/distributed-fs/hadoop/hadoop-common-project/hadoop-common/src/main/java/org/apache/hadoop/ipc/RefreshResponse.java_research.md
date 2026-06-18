# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RefreshResponse.java

## Purpose
`RefreshResponse` is the status object returned by refresh handlers, carrying an exit code, message, and optional sender name.

## Important APIs, Types, and Functions
`successResponse()` returns code `0` and message `Success`. The constructor sets return code and message. Getters/setters expose `senderName`, `returnCode`, and `message`. `toString` formats optional sender, message, and exit code.

## Control Flow
Handlers create or mutate responses. `RefreshRegistry.dispatch` sets sender names before returning responses.

## State and Persistence Behavior
It is a mutable in-memory value object. No persistence is performed.

## Dependencies and Integration Points
It is used by `RefreshHandler` and `GenericRefreshProtocol`.

## Risks and Test Signals
Risks are null messages, mutable responses being shared, and consumers treating nonzero codes inconsistently. Tests should cover string formatting with and without sender/message and success/failure codes.
