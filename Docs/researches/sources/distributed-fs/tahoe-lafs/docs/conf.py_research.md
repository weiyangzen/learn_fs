## sources/distributed-fs/tahoe-lafs/docs/conf.py

Purpose: Sphinx configuration for Tahoe-LAFS documentation.

Important settings: extensions `recommonmark` and `sphinx_rtd_theme`, source suffixes `.rst` and `.md`, `master_doc = index`, project metadata, language `en`, exclude `_build`, Pygments style, RTD HTML theme, static path, HTML help base name, and LaTeX/man/Texinfo document tuples.

Control flow: Sphinx imports this file to configure builders; there is no dynamic project import or version discovery.

State and dependencies: no persistent state; docs output paths are controlled by Sphinx/Makefile. Depends on recommonmark and sphinx_rtd_theme being installed by docs requirements.

Risks: hard-coded version/release `1.x` can drift from package version. Markdown support depends on recommonmark, which may lag modern MyST-style docs. Most settings are stock defaults, so warnings or strictness are likely configured elsewhere.
