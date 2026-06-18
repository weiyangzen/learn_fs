# sources/distributed-fs/ceph-client/tools/lib/python/kdoc/latex_fonts.py

Purpose: Detects variable-format Noto CJK fonts visible to XeTeX that can break Linux documentation PDF builds, and returns a diagnostic message with mitigation guidance.

Important APIs/types/functions: `LatexFontChecker.__init__()` configures an environment with `XDG_CONFIG_HOME` pointing at a denylist directory and compiles a CJK font regex. `description()` returns the module docstring. `get_noto_cjk_vf_fonts()` runs `fc-list : file family variable` and extracts paths for variable Noto Sans/Sans Mono/Serif CJK fonts. `check()` formats a warning block or returns `None`.

Control flow: `check()` calls `get_noto_cjk_vf_fonts()`, indents the returned font paths, and if non-empty builds a bordered message explaining that XeTeX must hide the variable fonts or skip CJK pages. `get_noto_cjk_vf_fonts()` filters `fc-list` output to `variable=True` lines matching the CJK regex.

State and persistence: No persistence. The only state is a copy of the process environment used for the subprocess, plus the compiled regex.

Dependencies/integration: Requires the external `fc-list` command from fontconfig and imports `os`, `re`, `subprocess`, `textwrap`, and `sys`. It is intended for the PDF documentation error path, likely through a wrapper such as `tools/docs/check-variable-fonts.py`.

Risks: Missing `fc-list` raises `FileNotFoundError`, which is not caught. The regex and `fc-list` output parsing are distribution-sensitive. The `rel_file` variable in `check()` is computed but unused. `sys.exit()` is used on subprocess errors, which is appropriate for a CLI helper but awkward for library-style use.

Test signals: Mock `subprocess.run()` for empty output, variable CJK fonts, non-CJK variable fonts, and command failure. Integration tests should verify the denylist environment changes the `fc-list` view as expected.
