## sources/distributed-fs/openafs/src/WINNT/client_exp/results_dlg.cpp

Purpose: Implements a reusable two-column results dialog for multi-file operations.

Important APIs/functions: `SetContents` stores dialog title, result column title, file list, and result list. `OnInitDialog` asserts equal list sizes, sets tab stops, and adds `file\tresult` rows. `OnHelp` routes to the caller-supplied help ID.

Control flow/state: The caller prepares all rows; the dialog only displays copied arrays. It is used by operations like cell display, server display, and mount point removal.

Dependencies/integration: Uses MFC list boxes, localized dialog templates, and `ShowHelp`.

Risks/tests: Equal-size mismatch is only asserted; release builds can read past one array. Long filenames/results may not align. Test empty lists, mismatched arrays, many rows, long localized strings, and caller-specific help IDs.
