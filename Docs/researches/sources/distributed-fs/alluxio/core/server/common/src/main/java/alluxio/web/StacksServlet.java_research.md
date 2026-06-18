# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/StacksServlet.java

## Purpose
`StacksServlet` returns a plain-text thread dump for the current Alluxio process and optionally logs it.

## Important APIs, Types, and Functions
It overrides `doGet(HttpServletRequest, HttpServletResponse)`, uses `ThreadUtils.printThreadInfo()`, `ThreadUtils.logThreadInfo()`, and configuration key `WEB_THREAD_DUMP_TO_LOG`.

## Control Flow, State, and Persistence
For GET requests, it sets `text/plain; charset=UTF-8`, writes thread info to the response output stream with UTF-8 encoding, and logs thread info if configured. It has no persistent state.

## Dependencies and Integration Points
It depends on servlet APIs, Alluxio configuration, and thread utilities. `WebServer` mounts it at the REST common thread-dump path.

## Risks and Test Signals
Risks include exposing stack traces, response cost under high thread counts, and optional log volume. Signals are UTF-8 plain-text output and conditional log emission.
