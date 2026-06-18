# sources/distributed-fs/openafs/src/WINNT/afsclass/c_debug.h

## Purpose

`c_debug.h` defines the AfsClass debug interface. In retail builds it supplies a minimal `ASSERT` fallback; in debug builds it declares the debug stream, assertion function, debug output window, and delayed formatting helper.

## Important APIs, Types, and Functions

Retail `ASSERT(b)` evaluates the expression and returns `TRUE` or `FALSE`. Debug builds declare `AssertFn`, `Debugstr` stream operators, `Debugstr::DebugWndProc`, `OutString`, static window helpers, `LogOut`, control tokens `ANGLES_ON`, `ANGLES_OFF`, `LASTERROR`, constants for the debug window buffer, and global `debug`.

## Control Flow

The header only declares behavior. Its main control-flow effect is the `ASSERT` macro: debug builds route failed assertions to `AssertFn`, while retail builds allow failure paths to execute by returning false.

## State and Persistence Behavior

It declares static debug-window state in the `Debugstr` class but owns no storage directly except through the corresponding implementation.

## Dependencies and Integration Points

Debug builds include `windows.h` and use `LPIDENT` from `afsclass.h`. The header is included by debug code and by assertions in the identity/object model.

## Risks and Edge Cases

Changing retail `ASSERT` semantics can alter production control flow because many methods use `if (!ASSERT(...)) return NULL;`. The debug declarations are tightly coupled to Win32 and are not portable.

## Test Signals

Build both debug and retail configurations. Verify assertion expressions are evaluated in retail, debug stream overloads compile for expected types, and including this header does not conflict with platform `ASSERT` definitions.
