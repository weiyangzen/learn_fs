<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/sphinx-build-wrapper -->
# sources/distributed-fs/ceph-client/tools/docs/sphinx-build-wrapper

Purpose: Kernel-specific Sphinx build launcher that translates make targets into `sphinx-build`, handles build directories, parallelism, venv activation, man/PDF/info post-processing, Rust docs, locale fixes, and static asset copying.

Important APIs/types/functions: `SphinxBuilder` contains `get_path()`, `check_rust()`, `get_sphinx_extra_opts()`, `run_sphinx()`, `handle_html()`, `handle_pdf()`, `pdf_parallel_build()`, `handle_info()`, `handle_man()`, `cleandocs()`, and `build()`. `TARGETS` maps kernel make targets to Sphinx builders and output subdirectories. `jobs_type()` validates `-j`. `main()` checks Python version and dispatches.

Control flow: Initialization reads environment such as `KERNELVERSION`, `KERNELRELEASE`, `PDFLATEX`, `PYTHON3`, `LATEXOPTS`, `srctree`, `SPHINXBUILD`, and `KERNELDOC`. `build()` prepares Sphinx arguments for each `SPHINXDIRS` entry, runs `sphinx-build` with jobserver-aware parallelism, handles `mandocs` directly via `kernel-doc`, then performs target-specific post-steps for HTML/EPUB, PDF, info, and Rust docs.

State and persistence: Persistent output is under `--builddir` with per-directory Sphinx output and `.doctrees`; `cleandocs` deletes that tree. The process mutates environment passed to subprocesses, optionally activates a venv by changing `PATH`/`VIRTUAL_ENV`, and may set `LC_ALL` or `XDG_CONFIG_HOME`.

Dependencies/integration: Integrated with the kernel documentation Makefile. Depends on `sphinx-build`, local `tools/docs/kernel-doc`, GNU make jobserver support through `jobserver.JobserverExec`, LaTeX tools for PDF, `kdoc.python_version`, and `kdoc.latex_fonts`.

Risks/tests: Risks include incorrect jobserver claims, broken cross-directory references from per-directory builds, LaTeX false failures, locale-sensitive Sphinx crashes, and manpage splitting based on `.TH`. Test signals include all target mappings (`htmldocs`, `mandocs`, `pdfdocs`, `infodocs`, `cleandocs`), venv mode, `SPHINXOPTS` parsing, missing tool paths, Rust-enabled `.config`, and parallel PDF output checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/sphinx-build-wrapper -->
