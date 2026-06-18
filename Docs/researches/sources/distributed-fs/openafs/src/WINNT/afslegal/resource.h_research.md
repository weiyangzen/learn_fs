# sources/distributed-fs/openafs/src/WINNT/afslegal/resource.h

## Purpose
Assigns numeric resource IDs for the afslegal dialog, message strings, and controls.

## Important APIs, Types, And Functions
Defines `IDS_MESSAGE_1` through `IDS_MESSAGE_5`, `IDD_LAWYER`, `IDC_TITLE`, `IDC_MESSAGE`, and `IDC_STATIC`. The `APSTUDIO_INVOKED` block contains Visual Studio resource-editor defaults.

## Control Flow
No runtime code. RC scripts bind these IDs to strings/dialog templates; `afslegal.cpp` uses the IDs to load and set text.

## State And Persistence
No state. IDs are resource ABI contracts across code, `.rc`, and localized modules.

## Dependencies And Integration Points
Integrated with `afslegal.cpp`, `afslegal_stub.rc`, and language-specific `afslegal.rc` files.

## Risks
Changing IDs without updating resources breaks localization or control lookup. Message ID zero can surprise tooling that treats zero specially.

## Test Signals
Resource compilation and successful localized dialog creation with correct title/message validate the file.
