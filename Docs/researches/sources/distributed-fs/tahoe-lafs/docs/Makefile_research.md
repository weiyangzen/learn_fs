## sources/distributed-fs/tahoe-lafs/docs/Makefile

Purpose: Sphinx-generated documentation Makefile exposing common builders.

Important targets: `help`, `clean`, `html`, `dirhtml`, `singlehtml`, `pickle`, `json`, `htmlhelp`, `qthelp`, `applehelp`, `devhelp`, `epub`, `latex`, `latexpdf`, `latexpdfja`, `text`, `man`, `texinfo`, `info`, `gettext`, `changes`, `linkcheck`, `doctest`, `coverage`, `xml`, `pseudoxml`, and `livehtml`.

Control flow: validates `sphinx-build` exists at parse time, builds with doctree output under `_build/doctrees`, passes paper and user options, and routes each builder to the appropriate `_build/<builder>` directory. `livehtml` uses `sphinx-autobuild`.

State and dependencies: writes documentation build artifacts under `_build`. Depends on Sphinx, make, optional LaTeX/makeinfo/linkcheck/autobuild tooling depending on target.

Risks: parse-time `which` failure prevents even non-build introspection. The Makefile is mostly stock, so project-specific behavior lives in `docs/conf.py` and requirements.
