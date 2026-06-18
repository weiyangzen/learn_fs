# sources/distributed-fs/openafs/src/WINNT/afslegal/afslegal.cpp

## Purpose
Small Windows GUI that displays the OpenAFS legal notice for a fixed interval. It is a localized modeless dialog wrapper around string resources.

## Important APIs, Types, And Functions
`Lawyer_OnInitDialog` bolds the title control font, formats the message from `IDS_MESSAGE_1`, sets `IDC_MESSAGE`, and frees the string. `Lawyer_DlgProc` handles initialization, timer, destroy, static-control coloring, and cancel. `WinMain` loads the matching locale module, creates `IDD_LAWYER`, positions it at the bottom of the Z order, and runs the message loop.

## Control Flow
Startup creates and shows the dialog without activation. Init populates controls and starts a 5000 ms timer. The timer destroys the window, destroy posts quit, and the message loop exits.

## State And Persistence
Only transient GUI state exists: dialog handle, timer, generated bold font, and static background brush. No disk/config state.

## Dependencies And Integration Points
Depends on Win32 GUI APIs, `WINNT/talocale.h`, `resource.h`, and localized `.rc` files. Likely launched by installer/startup flows requiring a legal notice.

## Risks
The created font and static brush are not explicitly deleted, though process lifetime is short. Missing localized resources would leave message text wrong or absent. Five-second auto-close may be poor for accessibility.

## Test Signals
Verify localized resource loading, visible title/message, timer auto-close, cancel close, intended Z-order/activation behavior, and no repeated-launch GDI growth.
