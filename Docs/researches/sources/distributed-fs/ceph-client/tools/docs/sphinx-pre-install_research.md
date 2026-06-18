<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/sphinx-pre-install -->
# sources/distributed-fs/ceph-client/tools/docs/sphinx-pre-install

Purpose: Dependency checker and install-hint generator for kernel Sphinx documentation builds, including system tools, Python modules, Sphinx versions, virtual environments, and optional PDF/LaTeX dependencies.

Important APIs/types/functions: `DepManager` tracks missing dependency classes. `AncillaryMethods` provides compatibility wrappers for `which()` and `subprocess.run()`. `MissingCheckers` implements file, program, Perl, Python, RPM, pacman, TeX, Sphinx-version, and distro-release checks. `SphinxDependencyChecker` adds distro-specific hint methods for Debian, Red Hat, openSUSE, Mageia/OpenMandriva, Arch, and Gentoo, plus venv recommendation logic and `check_needs()`.

Control flow: `main()` parses `--no-virtualenv`, `--no-pdf`, and `--version-check`, checks Python compatibility, then runs `check_needs()`. That method reads `Documentation/conf.py` for `needs_sphinx`, detects the OS, checks current and venv Sphinx versions, probes mandatory/optional dependencies, emits package-manager commands, and exits nonzero when mandatory dependencies remain missing.

State and persistence: It does not install packages itself. It reads OS metadata, `Documentation/conf.py`, requirements files, `/etc/portage/package.use` on Gentoo, and possible existing `sphinx_*` or `Sphinx_*` virtualenv directories. State is in dependency counters and printed recommendations.

Dependencies/integration: Integrated with kernel documentation setup workflows and Makefile diagnostics. Depends on distro package tools (`rpm`, `pacman`, etc. when available), `kpsewhich`, Perl, Python imports, and kernel-local `kdoc.python_version`.

Risks/tests: Risks include stale distro mappings, wrong package names, false PDF dependency failures, Python-version recommendation bugs, and command suggestions that are unsafe for unusual systems. Test signals are container smoke tests for supported distros, `--version-check`, `--no-pdf`, missing-Sphinx scenarios, existing venv selection, and mandatory/optional dependency counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/sphinx-pre-install -->
