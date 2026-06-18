# sources/distributed-fs/openafs/src/WINNT/talocale/tal_dialog.cpp

## Purpose

`tal_dialog.cpp` provides localized dialog and message-box helpers for TaLocale. It loads dialog templates through the TaLocale resource search chain and wraps `MessageBox()` so callers can supply literal strings or resource IDs with TaLocale formatting.

## Important APIs, Types, and Functions

- `ModelessDialog()` and `ModelessDialogParam()` load a dialog template with `TaLocale_GetDialogResource()` and create it with `CreateDialogIndirectParam()`.
- `ModalDialog()` and `ModalDialogParam()` do the same for modal dialogs through `DialogBoxIndirectParam()`.
- Overloaded `Message()` and `vMessage()` variants accept title/text as `LPCTSTR` or integer resource IDs.
- `MESSAGE_PARAMS` stores message-box type, formatted title, and formatted text for synchronous or background display.
- `Message_ThreadProc()` calls `MessageBox()`, frees formatted strings, deletes the parameter block, and returns the selected button.

## Control Flow

Dialog creation first resolves a localized `DLGTEMPLATE` and module handle. If no resource exists, creation returns `NULL`; otherwise the resolved module handle is used for indirect dialog creation. Message formatting funnels all overloads into `vMessage(UINT, LONG, LONG, LPCTSTR, va_list)`. It allocates a `MESSAGE_PARAMS`, formats the title with `FormatString()` and text with `vFormatString()`, adds a default icon if the low message-box bits imply a question/info style but no icon bits are present, and either creates a background thread for `MB_MODELESS` or calls `Message_ThreadProc()` synchronously.

## State and Persistence

There is no persistent module-local state. Each message allocates temporary formatted strings and a parameter block that are freed in `Message_ThreadProc()`. Modeless messages outlive the caller on a Win32 thread.

## Dependencies and Integration Points

The file depends on `WINNT/talocale.h`, which brings in TaLocale resource lookup, string formatting, and allocation macros. It integrates with the localized resource system in `tal_main.cpp` and the formatting/string allocation functions in `tal_string.cpp`. Win32 dependencies include indirect dialog creation, `CreateThread`, `SetThreadPriority`, and `MessageBox`.

## Risks and Edge Cases

- The overload set encodes either pointers or integer resource IDs into `LONG`, which is unsafe on 64-bit builds and relies on `PtrToLong`.
- The same `va_list` is passed to both `FormatString()` and `vFormatString()` without a `va_copy`; on ABIs where consuming a `va_list` mutates it, text formatting may see an exhausted list.
- For modeless messages, failure to create the thread leaks `pmp` and its strings because the code still returns `-1`.
- Background message threads are not closed with `CloseHandle()`, so thread handles leak after successful `CreateThread()`.

## Test Signals

Useful tests include loading modal and modeless dialogs from localized DLLs, formatting message titles/text from both literals and resource IDs, verifying default icon selection, and checking cleanup under synchronous and modeless message paths.
