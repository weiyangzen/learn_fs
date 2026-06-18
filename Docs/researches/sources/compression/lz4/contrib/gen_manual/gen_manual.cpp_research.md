# sources/compression/lz4/contrib/gen_manual/gen_manual.cpp

## Purpose
`gen_manual.cpp` converts annotated LZ4 C headers into a simple HTML manual. It scans comments and declarations in a header, classifies comment markers, emits declaration blocks, chapter headings, and a contents list.

## Important APIs, Types, and Functions
The program uses C++ standard library types `std::string`, `std::vector<std::string>`, `std::stringstream`, `std::ifstream`, and `std::ofstream`. Helpers include `trim()` for removing leading/trailing marker characters, `trim_comments()` for stripping C comment delimiters, `get_lines()` for collecting lines through a terminator or empty-line boundary, and `print_line()` for emitting declaration text while stripping `LZ4LIB_API` or `LZ4FLIB_API`. `main()` owns parsing and HTML emission.

## Control Flow
`main()` requires `version`, `input_file`, and `output_html`. It loads the whole input file into memory, then iterates line by line. `typedef ... { ... }` blocks are emitted directly. Inline `/**<` or `/*!<` comments on declarations are emitted as bold declaration snippets. Larger comments are detected by markers such as `/**=`, `/*!`, `/**`, `/*-`, and `/*=`. `/*!` sections swap comment text with the following declaration block; `/*=` and `/**=` become `<h3>` sections with following declarations; other recognized comments become `<h2>` chapters and are added to the contents list. At the end, the accumulated body is wrapped in a minimal HTML document.

## State and Persistence
All parse state is in memory: `input`, `comments`, `chapters`, `linenum`, and `sout`. The only persistent result is the output HTML file. There is no incremental cache.

## Dependencies and Integration Points
It depends on specific header documentation conventions used by LZ4 headers. It is invoked by the local Makefile and shell script. It does not parse C fully; it relies on line prefixes, C comment delimiters, and empty lines.

## Risks
The parser is intentionally ad hoc. `trim_comments()` assumes both `/*` and `*/` exist and is unused in the current flow, while the main parser assumes marker positions are valid. The generated HTML is not escaped for arbitrary header text, so unusual characters in comments or declarations may affect markup. A malformed comment can desynchronize `linenum` and either skip declarations or capture too much.

## Test Signals
Generate manuals from `lz4.h` and `lz4frame.h`, then inspect that contents, chapter anchors, function declarations, typedefs, and stripped API visibility macros appear as expected.
