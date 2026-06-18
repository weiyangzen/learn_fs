# sources/compression/zstd/contrib/gen_html/gen_html.cpp

Purpose: C++ parser/generator that extracts documented API comments and declarations from `zstd.h` and emits an HTML manual.

Important APIs and control flow: `trim()` strips selected characters from both ends, `trim_comments()` extracts C comment bodies, `get_lines()` collects input lines until a terminator or blank-line boundary, and `print_line()` removes `ZSTDLIB_API` and toggles bold around inline comments. `main()` reads version/input/output args, loads all input lines, scans for typedef blocks, inline member comments, and comment markers (`/**=`, `/*!`, `/**`, `/*-`, `/*=`). It emits bold declarations, paragraph comments, chapter anchors, a table of contents, and fixed ISO-8859-1 HTML boilerplate.

State, dependencies, and integration: state is in vectors/stringstreams during one run. It depends only on C++ standard streams/strings/vectors and zstd comment conventions. It integrates with `contrib/gen_html/Makefile` and release checks.

Risks and test signals: parsing is ad hoc and sensitive to comment/declaration formatting. It does not HTML-escape arbitrary content robustly. Deterministic output comparison in `release_check.yml` is the main test signal.
