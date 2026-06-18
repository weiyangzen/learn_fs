<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/termtest/stripansi.go -->
# sources/cloud-native/moby/integration/internal/termtest/stripansi.go

Purpose: provides a test helper that parses ANSI terminal output and returns the final visible one-dimensional character stream. It is aimed at integration tests that compare output passing through a Windows pseudoterminal with output redirected to a file.

Important APIs/types/functions: `StripANSICommands` builds an `Azure/go-ansiterm` parser with a package-local `stringHandler`, parses the input bytes, and returns the rendered string plus parser error. `stringHandler` embeds `ansiterm.AnsiEventHandler`, tracks a byte buffer and cursor, and implements `Print`, `Execute`, `ED`, `CUP`, `DECTCEM`, `SGR`, `DA`, `Flush`, and `String`.

Control flow: printable bytes append or overwrite at `cursor`; backspace moves the cursor left and trims a trailing space in one narrow case; carriage return and newline are treated as printed bytes. `ED` implements erase-display modes by blanking before the cursor, replacing the current buffer with spaces, or truncating after the cursor. `CUP` rejects multi-row cursor movement (`x > 1`) and otherwise maps ANSI column `y` onto the linear cursor.

State/persistence: state is transient per call: a byte slice and cursor. There is no filesystem or daemon state, but the lossy rendering intentionally persists overwrite/erase effects in the returned string.

Dependencies/integration: depends on `github.com/Azure/go-ansiterm`. The helper is internal to integration tests and supplies a lightweight alternative to a full terminal screen model.

Risks: the model is one-dimensional and byte-oriented, so multi-line cursor movement, wide runes, combining characters, and unsupported ANSI sequences can produce wrong output or parser errors. `CUP` has a suspicious padding loop (`len(h.b) - y`) that does not append when `y` is beyond the buffer, and default `ED` truncates to `cursor+1`, so edge cases around cursor bounds deserve care.

Test signals: `stripansi_test.go` covers realistic PTY escape streams with clear-screen, cursor visibility, graphics rendition, title-setting, cursor-home, cursor-column movement, and backspace behavior. Additional signals should include explicit unsupported cursor-row errors and erase/truncate boundary cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/termtest/stripansi.go -->
