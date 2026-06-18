# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_viewlog.cpp

Purpose: Implements log viewing for a service or arbitrary server log. It discovers a remote log name, downloads the log to a temporary local file, displays the tail, and supports Save As.

Important APIs/functions: `Services_ShowServiceLog` and `Services_ShowServerLog` create modeless view-log dialogs. `Services_ShowLog_TakeNextStep` is a small state machine: local file ready, remote name known, service log discovery, or user pick. `Services_ShowLog_OnEndTask` handles `taskSVC_FINDLOG` and `taskSVC_VIEWLOG`. `Services_ShowLog_OnInitDialog` stores service log preference, reads/truncates local file, and populates the edit control. `Services_ShowLog_OnSaveAs` copies the temp file via `SHFileOperation`. `Services_ShowLog_Pick` opens the remote log-name dialog.

Control flow: The dialog begins hidden, runs discovery/download steps asynchronously, then shows itself only after local content is ready. If service log discovery fails, it prompts for a filename once; if download fails after user-chosen or repeated attempt, it shows an error. Server log viewing can prompt for server/file when no remote path is given.

State and persistence: `SVC_VIEWLOG_PACKET` stores service/server identities, remote path, local temp path, and download attempt count. The local temp file is deleted on dialog destroy. Successful service log viewing persists `szRemote` in `SERVICE_PREF::szLogFile` via `Services_SavePreferences`. Window rectangle persists in `gr.rViewLog`.

Dependencies/integration: Uses shell API, open/save dialogs, service preferences, server enumeration, task-based download/discovery, and Win32 file APIs.

Risks: Reads file bytes into `TCHAR` buffer using byte count, which is fragile for Unicode builds or non-text encodings. The trailing CR/LF trimming loop lacks parentheses around `&&`/`||`, making it evaluate `pszLog[cch-1]` when `cch == 0` if the second disjunct is reached. `WM_CTLCOLOREDIT` creates a brush per paint without caching/deleting. Only the last 20 KB are shown by design.

Test signals: Known service log, unknown service prompting, failed first download then prompt, server-level log, temp file cleanup, large log truncation and line count, Save As copy, Unicode/ANSI builds, and empty file handling.
