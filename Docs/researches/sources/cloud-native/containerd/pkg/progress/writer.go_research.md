<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/progress/writer.go -->
# sources/cloud-native/containerd/pkg/progress/writer.go

## Purpose
Implements a buffered terminal writer that clears previously printed progress lines before writing the next screen.

## Important APIs, Types, And Functions
Writer wraps an io.Writer, buffered output, and prior line count. NewWriter, Write, Flush, clearLines, countLines, and stripLine implement refresh behavior.

## Control Flow
Write appends to an internal buffer. Flush clears the previous number of lines, counts visible lines in the new buffer using console width and ANSI-stripped text, writes the buffer, and resets it.

## State And Persistence
State is in-memory only: buffered bytes and last visible line count. It reads console dimensions from os.Stdin at flush time.

## Dependencies And Integration Points
Depends on containerd/console and lazyregexp. Uses escape control sequences for moving up and clearing lines.

## Risks And Edge Cases
If stdin is not a console or width cannot be determined, countLines returns zero, so old output may not clear. stripLine only removes a narrow color-code pattern, not all ANSI sequences.

## Test Signals
No direct tests in this subset; observable through progress UI refresh behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/progress/writer.go -->
