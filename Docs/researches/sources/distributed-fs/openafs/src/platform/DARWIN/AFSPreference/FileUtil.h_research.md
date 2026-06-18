# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/FileUtil.h

Purpose: declares an older privileged file-operation helper for moving, copying, deleting, and changing ownership using Authorization Services.

Important APIs and state: `FileUtil` has an `AuthUtil *autorization` ivar but the implementation uses `[AuthUtil shared]` directly. Methods are `autorizedMoveFile:toPath:`, `autorizedChown:owner:group:`, `autorizedCopy:toPath:`, and `autorizedDelete:`.

Control flow and persistence: callers build a temp file or modified plist and use this helper to copy/move/chown it into privileged locations, especially `/etc/authorization` in `PListManager`.

Dependencies and integration: imports Cocoa and `AuthUtil.h`. It predates the XPC privileged helper used by `TaskUtil`.

Risks: file paths are caller-provided and not allowlisted here. The misspelled method names are public local API. Security depends entirely on the AuthorizationRef held by `AuthUtil`.

Test signals: successful/denied authorization, paths with spaces, chown owner/group formatting, copy without overwrite expectations, and delete failure handling.
