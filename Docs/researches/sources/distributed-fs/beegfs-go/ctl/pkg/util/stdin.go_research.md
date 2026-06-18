# sources/distributed-fs/beegfs-go/ctl/pkg/util/stdin.go

## Purpose
Handles delimiter parsing and scanner setup for CTL commands that read path or string input from stdin.

## Important APIs, Types, And Functions
Exports `GetStdinDelimiterFromString`, `GetWalkStdinScanner`, and `ReadFromStdin`.

## Control Flow
`GetStdinDelimiterFromString` converts user-provided strings into a single byte using `strconv.Unquote`, with special handling for the default newline display string. `GetWalkStdinScanner` builds a `bufio.Scanner` with a custom split function that returns tokens separated by the delimiter and emits trailing data at EOF. `ReadFromStdin` scans, sends tokens to a channel respecting context cancellation, reports scanner errors to `errChan`, and closes the output channel.

## State And Persistence
No persistence. It reads process stdin and sends transient channel values.

## Dependencies And Integration Points
Used by `paths.go` and any command needing delimited stdin. Depends on `os.Stdin`, `bufio.Scanner`, context cancellation, and byte delimiters.

## Risks And Edge Cases
`bufio.Scanner` retains its default token size limit, so very long paths/input records can fail. `ReadFromStdin` checks `scanner.Err()` inside the scan loop, where it is normally only meaningful after scanning completes; final scanner errors after the loop are not reported. Delimiters are restricted to one byte, not full runes.

## Test Signals
No direct tests. Needed coverage includes escape parsing, invalid delimiters, NUL delimiter scanning, long token behavior, cancellation, and scanner error propagation.
