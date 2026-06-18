<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/enrich_formatter.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/kdoc/enrich_formatter.py

## Purpose
This module defines an argparse help formatter that preserves raw description line breaks and optionally enriches marked-up help text for terminals.

## Important APIs, Types, and Functions
- `class EnrichFormatter(argparse.HelpFormatter)` is the only public class.
- `__init__` records whether stdout is a TTY.
- `enrich_text(text)` converts ReST inline literals ``text`` to ANSI bold only on TTY output.
- `_fill_text` preserves existing description line breaks while applying enrichment.
- `_format_usage` constructs usage text with positional arguments uppercased and enriched.
- `_format_action_invocation` enriches positional argument names and returns option strings for flags.

## Control Flow and State
Formatting is synchronous and stateless except for `_tty` and argparse's inherited formatter state. Terminal enrichment is disabled for non-TTY output to keep generated help plain.

## Dependencies and Integration Points
It depends on `argparse`, `re`, and `sys`. Kernel-doc command-line tools can use it as `formatter_class` to make positional arguments and inline literals easier to read.

## Risks and Test Signals
The custom `_format_usage` is simpler than argparse's default and may omit some advanced grouping/nargs formatting. ANSI insertion depends on stdout, not necessarily the destination argparse writes to. Tests should cover TTY/non-TTY behavior, options with arguments, positionals, descriptions with multiple lines, and literal markup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/enrich_formatter.py -->
