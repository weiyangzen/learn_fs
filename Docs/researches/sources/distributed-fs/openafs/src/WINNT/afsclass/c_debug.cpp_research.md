# sources/distributed-fs/openafs/src/WINNT/afsclass/c_debug.cpp

## Purpose

`c_debug.cpp` implements debug-only assertion, tracing, debug-window output, and formatted logging helpers for the Windows AfsClass code. All executable content is compiled only under `DEBUG`.

## Important APIs, Types, and Functions

The file defines global `Debugstr debug`, static `Debugstr` window/buffer state, `AssertFn`, `Debugstr` stream operators for strings, numbers, pointers, rectangles, and `LPIDENT`, `Debugstr::Register`, `Initialize`, `OutString`, `Output`, `DebugWndProc`, `cxAvgWidth`, and `LogOut` constructor/destructor formatting support.

## Control Flow

`AssertFn` reports failed assertions to the debug stream and a message box. `Debugstr::operator<<(char*)` handles control tokens (`ANGLES_ON`, `ANGLES_OFF`, `LASTERROR`) or posts copied strings to a lazily created debug window. `OutString` writes to `OutputDebugString`, paints the window, handles newlines and screen wrap, and optionally records lines in the ring-like `gdata` buffer. `DebugWndProc` consumes posted strings, frees the allocated buffer, and repaints recorded lines. `LogOut` stores pointers to varargs on construction and formats them when destructed.

## State and Persistence Behavior

State is process-local debug UI state: window handle, font/brush, cursor positions, screen buffer, angle mode, registered/init flags, and `LogOut` temporary formatting state. There is no file persistence.

## Dependencies and Integration Points

The code depends on Win32 GDI/window APIs, `OutputDebugString`, `FormatMessage`, `MessageBox`, `LPIDENT` name getters, AfsClass allocation helpers, and debug macros from `c_debug.h`.

## Risks and Edge Cases

The debug path uses fixed-size buffers (`xMAX`, `yMAX`, 256-byte format buffers) and unbounded `strcat` into `gdata[gcY]`, so long debug strings can overflow in debug builds. `DebugWndProc` repaint loop never increments `gcY` inside the `for`, which appears to risk an infinite repaint loop. `LogOut` stores raw vararg pointers and assumes the pointed values remain alive until destruction.

## Test Signals

Debug-build smoke tests should exercise assertion failures, `LASTERROR`, `LPIDENT` formatting for each type, newlines, repaint, destruction cleanup, and long strings. Retail-build tests should confirm `ASSERT` still evaluates to a boolean without pulling in debug UI code.
