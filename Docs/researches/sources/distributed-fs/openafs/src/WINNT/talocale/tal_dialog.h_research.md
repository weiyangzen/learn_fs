# sources/distributed-fs/openafs/src/WINNT/talocale/tal_dialog.h

## Purpose

`tal_dialog.h` declares TaLocale's dialog creation and generic message-box helpers. It is the public interface used by Windows UI code that wants localized dialog templates and formatted localized messages.

## Important APIs, Types, and Functions

- Defines `MB_MODELESS` as a high-bit flag consumed by TaLocale's `Message()` wrapper, not by Win32 `MessageBox()` directly.
- Declares `ModelessDialog`, `ModelessDialogParam`, `ModalDialog`, and `ModalDialogParam`.
- Declares overloaded `Message()` and `vMessage()` forms for literal/resource-ID title and text combinations.
- Uses `EXPORTED` for DLL export by default.

## Control Flow

The header has no runtime flow. It exposes overloads that implementation code funnels into the `LONG`-based formatter and message-box executor in `tal_dialog.cpp`.

## State and Persistence

No state is defined here. State is transient in implementation-allocated message parameter blocks and resource handles.

## Dependencies and Integration Points

Consumers need Win32 dialog types (`HWND`, `DLGPROC`, `LPARAM`, `INT_PTR`, `UINT`, `LPCTSTR`) and C varargs support. It is normally included through `talocale.h` after Windows headers.

## Risks and Edge Cases

- The custom `MB_MODELESS` value occupies the high bit of a `UINT` message type and must be stripped before calling `MessageBox()`.
- C++ overloads make call-site type selection important; integer constants can bind to resource-ID overloads instead of pointer overloads.
- `cdecl` varargs declarations require callers and the implementation to agree on calling convention.

## Test Signals

Compile/link tests should verify all overloads are exported and callable from UI modules. Runtime tests should validate `MB_MODELESS`, literal strings, resource IDs, and `va_list` variants.
