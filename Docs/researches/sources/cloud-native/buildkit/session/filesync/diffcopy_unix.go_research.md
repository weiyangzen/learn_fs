<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/diffcopy_unix.go -->
# sources/cloud-native/buildkit/session/filesync/diffcopy_unix.go

Purpose: Unix implementation of sending a diffcopy stream.

Important APIs, types, and functions: `sendDiffCopy(stream, fs, progress)` wraps `fsutil.Send(stream.Context(), stream, fs, progress)` with stack errors.

Control flow and state: no persistent state. It streams filesystem content and metadata through the provided stream.

Dependencies and integration: compiled on non-Windows platforms and called by the filesync protocol table.

Risks and test signals: behavior is primarily in fsutil. Test through session filesync integration, include/exclude filters, and exporter copy paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/diffcopy_unix.go -->
