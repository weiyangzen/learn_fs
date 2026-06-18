<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/creds.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/creds.cpp

## Purpose
Handles cell opening, credential acquisition/refresh, and monitoring-scope selection.

## Important APIs, Types, And Functions
Open-cell hook helpers manage OK, subset changes, advanced UI, and `taskOPENCELL` completion. Public APIs are `OpenCellDialog`, `NewCredsDialog`, `CheckForExpiredCredentials`, and `CheckCredentials`.

## Control Flow
The open-cell dialog initializes monitoring choices, populates subsets as cell text changes, validates credentials via KFW or app-library paths, builds an `OPENCELL_PACKET` for all/one/subset monitoring, and starts `taskOPENCELL`; task success closes the dialog.

## State And Persistence
Updates global `g.hCreds`. Saves/loads subsets through the subset subsystem. Uses dialog controls/params for transient state and `gr.fWarnBadCreds` for warning preference.

## Dependencies And Integration Points
Depends on AFS app-library credential/open-cell dialogs, KFW, subsets, task framework, global display state, and alert/scout credential checks.

## Risks And Edge Cases
Passwords live in stack buffers. KFW and non-KFW validation differ. Advanced resizing is layout-sensitive. Current-cell subset handling assumes `g.sub` shape.

## Test Signals
KFW/non-KFW success/failure, bad/expired credentials, monitoring packet variants, dirty subset save failure, advanced toggle, and task failure UI re-enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/creds.cpp -->
