# sources/distributed-fs/ceph-client/scripts/dtc/of_unittest_expect

Purpose: Perl log post-processor for Linux devicetree unittest console output. It highlights expected messages, suppresses optional expected output, and reports missing/unexpected unittest expectation markers.

Important APIs/functions/state: `compare()` matches expected text against log lines with literal segments plus special tokens `<<int>>`, `<<hex>>`, and `<<all>>`. `usage()` prints CLI help. `Getopt::Long` parses display options. The main `LINE` loop strips optional timestamps, recognizes `EXPECT \`, `EXPECT /`, `EXPECT_NOT \`, and `EXPECT_NOT /` markers with the `### dt-test ###` prefix, tracks stacks/queues for begin/end matching, prefixes output lines, and prints statistics.

Control flow/state: expectation begin lines push patterns onto stacks. Matching normal lines move entries into found queues. End markers validate nesting and whether the expected or forbidden message occurred. Global counters track found/missing expectations, unittest failures, and internal errors.

Dependencies/integration: Perl script using `Getopt::Long` and `Text::Wrap` plus console output conventions from `drivers/of/unittest.c`. It is not linked with DTC/libfdt C code but belongs to the same devicetree tooling area.

Risks: there appear to be variable-name mistakes in some branches (`@begin` instead of `@exp_begin_stack`/`@expnot_begin_stack`), which can affect matching. Regex handling is intentionally simple and case-sensitive. Hex matching only accepts lowercase `a-f`.

Test signals: logs with nested EXPECT/EXPECT_NOT regions, missing begin/end markers, timestamp stripping, hidden expected lines, line-number mode, fail-line detection, stats toggling, and special-token comparisons.
