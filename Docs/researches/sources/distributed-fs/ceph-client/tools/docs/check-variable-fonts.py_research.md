# sources/distributed-fs/ceph-client/tools/docs/check-variable-fonts.py

Purpose: Python wrapper that detects problematic Noto CJK variable fonts for kernel documentation PDF/LaTeX builds.

Important APIs, types, and functions: Adds `tools/lib/python` to `sys.path`, imports `kdoc.latex_fonts.LatexFontChecker`, builds argparse description from checker, accepts `--deny-vf`, calls `LatexFontChecker(args.deny_vf).check()`, prints any returned message, and exits with status 1.

Control flow: Always runs the font check once and exits 1 regardless of whether a message was printed.

State and persistence: May read fontconfig data under the optional deny-vf config directory. No writes in this wrapper.

Dependencies and integration points: Depends on the kernel documentation Python helper package and local/fontconfig font state. Used by documentation build checks.

Risks: The unconditional `sys.exit(1)` means callers must interpret output or this script may be intended only as a failing guard. Behavior depends on `LatexFontChecker` implementation and system fonts.

Test signals: Run with and without problematic fonts, with `--deny-vf`, and verify caller expectations for exit status.
