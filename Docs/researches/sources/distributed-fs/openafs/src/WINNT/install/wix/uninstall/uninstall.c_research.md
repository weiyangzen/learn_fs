<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/wix/uninstall/uninstall.c -->
## sources/distributed-fs/openafs/src/WINNT/install/wix/uninstall/uninstall.c

Purpose: Standalone helper that uninstalls all MSI products related to the OpenAFS for Windows upgrade code.

Important APIs, types, and functions: `main` sets MSI UI to progress-only, loops over `MsiEnumRelatedProducts` for upgrade code `{6823EEDD-84FC-4204-ABB3-A80D25779833}`, and calls `MsiConfigureProduct(..., INSTALLSTATE_ABSENT)` for each product code found.

Control flow and state: The loop increments `iProduct` after each successful configure call and stops when `MsiEnumRelatedProducts` returns something other than success. It returns 0 only when the terminal code is `ERROR_NO_MORE_ITEMS`.

Persistence and dependencies: Persists uninstallation of matching MSI products. Depends on Windows Installer APIs and installed product metadata.

Integration points: Used by installer/uninstaller flows to remove related OpenAFS products by upgrade code.

Risks: Incrementing `iProduct` while uninstalling products can skip entries if enumeration order compacts after removal; a safer pattern often keeps index 0 until no products remain. It ignores `MsiConfigureProduct` return code, so configure failures do not directly stop/report. Product code buffer is 39 chars, matching GUID length plus NUL.

Test signals: Multiple related products installed, configure failure simulation, return code on no products, and UI level behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/wix/uninstall/uninstall.c -->
