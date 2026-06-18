# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/animate_icon.h

Purpose: declares the setup progress icon animation API.

Important APIs/types/functions: exports `AnimateIcon(HWND hIcon, int *piFrameLast = NULL)`, `StartAnimation(HWND hIcon, int fps)`, and `StopAnimation(HWND hIcon)`.

Control flow: UI code can directly set a single frame through `AnimateIcon()` or manage timer-driven animation with start/stop calls.

State/persistence: no header state; implementation caches icons and frame state.

Dependencies/integration: requires Windows `HWND` definitions and is used by `progress_dlg.cpp`.

Risks/test signals: because there is no include guard in this header, repeated inclusion is harmless only due to prototypes but still nonstandard. Compile tests should ensure C++ default argument use is compatible with all callers.
