# sources/distributed-fs/openafs/src/WINNT/license/main.cpp

## Purpose

`main.cpp` implements a standalone Windows command-line converter named in usage as `sgml2rtf`. It reads SGML-like license/source text files, converts a small set of markup tags into RTF paragraph/header formatting, escapes RTF-special characters, and writes `.rtf` files next to the input names.

## Important APIs, types, and functions

Global state is `g::CodePage`, defaulting to `CP_ACP` and overrideable by numeric command-line switches. `EscapeSpecialCharacters` escapes `\`, `{`, and `}` for RTF. `FormatFile` maps input text to RTF output. `TranslateFile` reads the source file, converts wide input text to a multibyte target with `WideCharToMultiByte`, and calls `FormatFile`. `FindFullPath` combines a wildcard path prefix with a found filename. `main` parses arguments, expands wildcards with `FindFirstFile`/`FindNextFile`, accumulates file names with `mstrcat`, and invokes conversion.

## Control flow

`main` scans command-line arguments. Switches beginning with `-` or `/` set the code page. Other arguments are treated as wildcard file specs. For each matching non-directory file, it appends the full path to a null-separated multistring. It then walks that multistring and calls `TranslateFile`.

`TranslateFile` opens the file, reads the entire content into a zero-padded buffer, allocates a target buffer four times the source size, converts from wide characters with the selected code page, and passes the text to `FormatFile`. `FormatFile` replaces the extension with `.rtf`, creates a new output file, writes an RTF prolog with the code page, tokenizes the input by whitespace, newlines, and `<...>` tags, maps `<?>` and `<p>` to paragraph breaks, maps `<d>` to bold section headings, writes escaped text runs, and finishes with an RTF trailer.

## State and persistence behavior

Persistent output is the generated `.rtf` file. The converter overwrites existing output with `CREATE_ALWAYS`. `EscapeSpecialCharacters` uses a static heap buffer reused across calls, and `FindFullPath` uses a static `MAX_PATH` buffer, so both are single-threaded helpers. Input file lists are stored in the license utility's custom multistring allocation and freed after processing.

## Dependencies and integration points

The file depends on Win32 file APIs, wildcard enumeration, `WideCharToMultiByte`, RTF syntax, and `license/multistring.h`. It is independent of NetIDMgr and the AFS plugin.

## Risks and edge cases

The converter assumes the source buffer can be interpreted as `LPCWSTR`, which is risky for byte-oriented SGML inputs. `EscapeSpecialCharacters` computes `cchReq = cchIn * 2 + 1`, but a `}` expands to four characters (`\\'7D`), so the static output buffer can be too small for many right braces. `FormatFile` uses `lstrcpy`/`lstrcat` into `MAX_PATH` buffers with no length checks. File-size based allocations have little overflow/error handling. The parsing only understands a tiny tag subset and skips leading whitespace/newlines aggressively.

## Test signals

Tests should convert files containing backslashes, braces, `<?>`, `<p>`, and multiple `<d>` headings; verify code-page values in the RTF prolog; exercise wildcard expansion; check extension replacement for names with and without dots; and stress right-brace-heavy input to catch the escaping buffer bug.
